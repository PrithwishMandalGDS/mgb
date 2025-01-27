from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.core.exceptions import AzureError

# Service Principal Credentials
CLIENT_ID = "264791ae-ca1f-4828-9212-166163b8127c"  # appId from the Service Principal
CLIENT_SECRET = "eGA8Q~vUggc_8ai7ZaobwE3dERisYWQ5zfyMnaR."  # password from the Service Principal
TENANT_ID = "720edb1f-5c4e-4043-8141-214a63a7ead5"  # tenant from the Service Principal


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



