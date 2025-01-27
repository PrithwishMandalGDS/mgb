from flask import Flask, render_template, request, redirect, url_for
from api.subscriptions import list_subscriptions_and_resource_groups
from api.rg import get_rg_from_subscriptions, get_subscription_id_from_rg
from api.vm import get_vm_details, start_vm_operation, stop_vm_operation, get_resource_group_of_vm
from dotenv import load_dotenv
from dtf import output_dict, find_vm_based_researcher, get_sub_from_vm, get_rg_from_vm, update_state_vms
from api.vm_operate import perform_operation
import os
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from flask import jsonify

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

app = Flask(__name__)

@app.route('/')
def home():
    output_dicts = output_dict
    return render_template('subscriptions.html', output_dicts=output_dicts)

@app.route('/resourcegroups/<researcher_name>')
def resourcegroups(researcher_name):
    name_list = find_vm_based_researcher(researcher_name)
    return render_template('resourcegroups.html', name_list=name_list)

@app.route('/vm_form/<sub_name>')
def vm_form(sub_name):
    try:
        vm_details = get_vm_details(rg_name)
        running_vms = [name for name, details in vm_details.items() if details.get('Status') == 'running']
        stopped_vms = [name for name, details in vm_details.items() if details.get('Status') == 'stopped']
        
    except Exception as e:
        vm_details = {}
        print(f"An error occurred: {e}")
    return render_template('vm_form.html', rg_name=rg_name, running_vms=running_vms, stopped_vms=stopped_vms)


@app.route('/start_vm/<vm>')
def start_vm(vm):
    try:
        sub_name = get_sub_from_vm(vm)
        result = perform_operation(vm, "start", sub_name)
        update_state_vms(vm, "Running")
        rg_name = get_rg_from_vm(vm)
        vm_details = get_vm_details(rg_name)
    except Exception as e:
        vm_details = {}
        print(f"An error occurred: {e}")
    return render_template('vm.html', vm_details=vm_details)

@app.route('/stop_vm/<vm>')
def stop_vm(vm):
    try:
        sub_name = get_sub_from_vm(vm)
        result = perform_operation(vm, "stop", sub_name)
        update_state_vms(vm, "Stopped")
        rg_name = get_rg_from_vm(vm)
        vm_details = get_vm_details(rg_name)
    except Exception as e:
        vm_details = {}
        print(f"An error occurred: {e}")
    return render_template('vm.html', vm_details=vm_details)

# @app.route('/vm_details')
# def get_vm_details(rg_name):
#     vm_details = get_vm_details(rg_name)
#     return render_template('vm_details.html', vm_details=vm_details)

if __name__ == '__main__':
    app.run(debug=True, port=9976)
