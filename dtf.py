import pandas as pd


file_path = r'data/researcher.xlsx'
researchers = pd.read_excel(file_path)
researchers['Count'] = researchers['Count'].fillna(0).astype(int)
output_dict = researchers.set_index('Researchers')['Count'].to_dict()

def find_vm_based_researcher(name: str):
    file_path_vm = r'data/vm.xlsx'
    vm_data = pd.read_excel(file_path_vm)
    filtered_df = vm_data[vm_data["Researcher"] == name]
    vm_state_dict = dict(zip(filtered_df["VM"], filtered_df["State"]))
    return vm_state_dict
    
def get_sub_from_vm(vm_name: str) -> str:
    file_path_vm = r'data/vm.xlsx'
    data = pd.read_excel(file_path_vm)
    df = pd.DataFrame(data)
    result = df[df["VM"] == vm_name]
    if not result.empty:
        return result.iloc[0]["Subscriptions"]
    else:
        raise ValueError(f"VM '{vm_name}' not found in the data.")
        
def get_rg_from_vm(vm_name: str) -> str:
    file_path_vm = r'data/vm.xlsx'
    data = pd.read_excel(file_path_vm)
    df = pd.DataFrame(data)
    result = df[df["VM"] == vm_name]
    if not result.empty:
        return result.iloc[0]["RG"]
    else:
        raise ValueError(f"VM '{vm_name}' not found in the data.")
        
def update_state_vms(vm_name: str, new_state: str) -> str:
    file_path_vm = r'data/vm.xlsx'
    data = pd.read_excel(file_path_vm)
    df = pd.DataFrame(data)
    if vm_name in df["VM"].values:
        df.loc[df["VM"] == vm_name, "State"] = new_state
        df.to_excel(file_path_vm, index=False)
        print(f"State updated for VM '{vm_name}' to '{new_state}'.")
    else:
        print(f"VM '{vm_name}' not found in the data.")
    