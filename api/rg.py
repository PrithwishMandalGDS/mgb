from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
def get_rg_from_subscriptions(subcription_name):
    resource = []
    credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    subscription_client = SubscriptionClient(credential)
    subscription_id = None
    for subscription in subscription_client.subscriptions.list():
        if subscription.display_name == subcription_name:
            subscription_id = subscription.subscription_id
            break
    if subscription_id:
        resource_client = ResourceManagementClient(credential, subscription_id)
        resource_groups = resource_client.resource_groups.list()
        for rg in resource_groups:
            resource.append(rg.name)
    
    return resource



# Authenticate using the credentials from the .env file
credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)

# Initialize the Subscription client
subscription_client = SubscriptionClient(credential)

# Function to get subscription ID from resource group name
def get_subscription_id_from_rg(rg_name):
    # Loop through all subscriptions
    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id
        print(f"Checking subscription: {subscription.display_name} ({subscription_id})")

        # Initialize the ResourceManagementClient for each subscription
        resource_client = ResourceManagementClient(credential, subscription_id)
        
        try:
            # List all resource groups in the current subscription
            resource_groups = resource_client.resource_groups.list()

            for rg in resource_groups:
                if rg.name == rg_name:
                    # Return the subscription_id if resource group is found
                    return subscription_id
        except Exception as e:
            print(f"Error accessing resource groups in subscription '{subscription.display_name}': {e}")
    
    # Return None if resource group was not found in any subscription
    return subscription_id
