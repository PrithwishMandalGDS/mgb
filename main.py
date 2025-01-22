from fastapi import FastAPI, HTTPException
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

# Service Principal Credentials
CLIENT_ID = "264791ae-ca1f-4828-9212-166163b8127c"       # appId from the Service Principal
CLIENT_SECRET = "eGA8Q~vUggc_8ai7ZaobwE3dERisYWQ5zfyMnaR."  # password from the Service Principal
TENANT_ID = "720edb1f-5c4e-4043-8141-214a63a7ead5"       # tenant from the Service Principal
SUBSCRIPTION_ID = "7ddcaa55-cb88-46a1-8e71-066668a39ca0"

# Authenticate with Service Principal
credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

# Initialize FastAPI app
app = FastAPI()

def perform_operation(vm_name: str, operation: str):
    # List all VMs in the subscription
    vms = compute_client.virtual_machines.list_all()

    for vm in vms:
        if vm.name == vm_name:
            resource_group = vm.id.split("/")[4]  # Extract resource group from VM ID

            if operation == "start":
                async_vm_start = compute_client.virtual_machines.begin_start(resource_group, vm_name)
                async_vm_start.result()
                return f"VM {vm_name} started successfully."
            elif operation == "stop":
                async_vm_stop = compute_client.virtual_machines.begin_power_off(resource_group, vm_name)
                async_vm_stop.result()
                return f"VM {vm_name} stopped successfully."
            else:
                raise HTTPException(status_code=400, detail="Invalid operation. Use 'start' or 'stop'.")
    raise HTTPException(status_code=404, detail=f"VM {vm_name} not found.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Azure VM Operations API!"}

@app.post("/vm/operate/")
def operate_vm(vm_name: str, operation: str):
    """
    Perform an operation (start/stop) on a VM.

    Args:
        vm_name (str): Name of the VM
        operation (str): Operation to perform ('start' or 'stop')
    """
    try:
        result = perform_operation(vm_name, operation)
        return {"message": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
