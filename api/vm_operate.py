from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.core.exceptions import AzureError
import os
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")


def perform_operation(vm_name: str, operation: str, subscription: str):
    SUBSCRIPTION_NAME = subscription
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    subscription_client = SubscriptionClient(credential)
    subscription_id = None
    for subscription in subscription_client.subscriptions.list():
        if subscription.display_name == SUBSCRIPTION_NAME:
            subscription_id = subscription.subscription_id
            break
    if not subscription_id:
        raise ValueError(f"Subscription '{SUBSCRIPTION_NAME}' not found.")
        
    compute_client = ComputeManagementClient(credential, subscription_id)
    try:
        vms = compute_client.virtual_machines.list_all()

        for vm in vms:
            if vm.name == vm_name:
                resource_group = vm.id.split("/")[4]  # Extract resource group from VM ID

                if operation == "start":
                    async_vm_start = compute_client.virtual_machines.begin_start(resource_group, vm_name)
                    async_vm_start.result()  # Wait for the operation to complete
                    return f"VM {vm_name} started successfully."
                elif operation == "stop":
                    async_vm_stop = compute_client.virtual_machines.begin_power_off(resource_group, vm_name)
                    async_vm_stop.result()  # Wait for the operation to complete
                    return f"VM {vm_name} stopped successfully."
                else:
                    raise ValueError("Invalid operation. Use 'start' or 'stop'.")
        raise ValueError(f"VM {vm_name} not found.")
    except AzureError as e:
        raise Exception(f"An error occurred while performing the operation: {str(e)}")



