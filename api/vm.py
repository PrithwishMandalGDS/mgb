from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from api.rg import get_rg_from_subscriptions, get_subscription_id_from_rg

import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

def get_vm_details(resource_group_name):
    credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    subscription_client = SubscriptionClient(credential)
    vm_details = {}
    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id

        compute_client = ComputeManagementClient(credential, subscription_id)
        network_client = NetworkManagementClient(credential, subscription_id)

        try:
            vms = compute_client.virtual_machines.list(resource_group_name)
            for vm in vms:
                vm_name = vm.name
                vm_size = vm.hardware_profile.vm_size
                vm_location = vm.location

                instance_view = compute_client.virtual_machines.instance_view(resource_group_name, vm_name)
                statuses = instance_view.statuses
                vm_status = [status.display_status for status in statuses if "PowerState" in status.code]
                vm_status = vm_status[0].replace("VM ", "") if vm_status else "Unknown"
                network_interfaces = vm.network_profile.network_interfaces
                for nic in network_interfaces:
                    nic_name = nic.id.split("/")[-1]
                    nic_details = network_client.network_interfaces.get(resource_group_name, nic_name)
                    ip_configs = nic_details.ip_configurations
                    for ip_config in ip_configs:
                        public_ip_id = ip_config.public_ip_address.id if ip_config.public_ip_address else None
                        private_ip = ip_config.private_ip_address

                        public_ip = None
                        if public_ip_id:
                            public_ip_name = public_ip_id.split("/")[-1]
                            public_ip_details = network_client.public_ip_addresses.get(resource_group_name, public_ip_name)
                            public_ip = public_ip_details.ip_address

                        vm_details[vm_name] = {
                            "Size": vm_size,
                            "Region": vm_location,
                            "Status": vm_status,
                            "PrivateIP": private_ip,
                        }

        except Exception as e:
            print(f"Error accessing resource group '{resource_group_name}' in subscription '{subscription.display_name}': {e}")
        
    return vm_details

def start_vm_operation(rg_name, vm_name):
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    SUBSCRIPTION_ID = get_subscription_id_from_rg(rg_name)
    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    vms = compute_client.virtual_machines.list_all()
    for vm in vms:
        if vm.name == vm_name:
            compute_client.virtual_machines.begin_start(rg_name, vm_name).result()
            return True
        
def stop_vm_operation(rg_name, vm_name):
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    SUBSCRIPTION_ID = get_subscription_id_from_rg(rg_name)
    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    vms = compute_client.virtual_machines.list_all()
    for vm in vms:
        if vm.name == vm_name:
            compute_client.virtual_machines.begin_power_off(rg_name, vm_name).result()
            return True
        


def get_resource_group_of_vm(vm_name):
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    subscription_client = SubscriptionClient(credential)
    subscriptions = subscription_client.subscriptions.list()

    for subscription in subscriptions:
        subscription_id = subscription.subscription_id

        compute_client = ComputeManagementClient(credential, subscription_id)
        resource_client = ResourceManagementClient(credential, subscription_id)

        for rg in resource_client.resource_groups.list():
            for vm in compute_client.virtual_machines.list(rg.name):
                if vm.name == vm_name:
                    return rg.name

    return rg.name

from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from collections import defaultdict

def get_vm_details_grouped_by_technical_owner(resource_group_name):
    credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    subscription_client = SubscriptionClient(credential)
    vm_details_by_owner = defaultdict(list)  # Dictionary to store VM details grouped by TechnicalOwner

    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id

        compute_client = ComputeManagementClient(credential, subscription_id)
        network_client = NetworkManagementClient(credential, subscription_id)

        try:
            vms = compute_client.virtual_machines.list(resource_group_name)
            for vm in vms:
                # Get VM instance and tags
                vm_instance = compute_client.virtual_machines.get(resource_group_name, vm.name)
                tags = vm_instance.tags or {}
                technical_owner = tags.get("TechnicalOwner", "Unknown")

                vm_name = vm.name
                vm_size = vm.hardware_profile.vm_size
                vm_location = vm.location

                # Get instance view for status
                instance_view = compute_client.virtual_machines.instance_view(resource_group_name, vm_name)
                statuses = instance_view.statuses
                vm_status = [status.display_status for status in statuses if "PowerState" in status.code]
                vm_status = vm_status[0].replace("VM ", "") if vm_status else "Unknown"

                # Get network details
                network_interfaces = vm.network_profile.network_interfaces
                for nic in network_interfaces:
                    nic_name = nic.id.split("/")[-1]
                    nic_details = network_client.network_interfaces.get(resource_group_name, nic_name)
                    ip_configs = nic_details.ip_configurations
                    for ip_config in ip_configs:
                        public_ip_id = ip_config.public_ip_address.id if ip_config.public_ip_address else None
                        private_ip = ip_config.private_ip_address

                        public_ip = None
                        if public_ip_id:
                            public_ip_name = public_ip_id.split("/")[-1]
                            public_ip_details = network_client.public_ip_addresses.get(resource_group_name, public_ip_name)
                            public_ip = public_ip_details.ip_address

                        # Add VM details to the dictionary under the respective TechnicalOwner
                        vm_details_by_owner[technical_owner].append({
                            "VMName": vm_name,
                            "Size": vm_size,
                            "Region": vm_location,
                            "Status": vm_status,
                            "PrivateIP": private_ip,
                            "PublicIP": public_ip,
                        })

        except Exception as e:
            print(f"Error accessing resource group '{resource_group_name}' in subscription '{subscription.display_name}': {e}")
        
    return dict(vm_details_by_owner)