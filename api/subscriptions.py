# from azure.identity import ClientSecretCredential
# from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
# from dotenv import load_dotenv
# import os

# load_dotenv()

# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# TENANT_ID = os.getenv("TENANT_ID")

# def list_subscriptions_and_resource_groups(client_id, client_secret, tenant_id):
#     try:
#         credentials = ClientSecretCredential(
#             client_id=client_id,
#             client_secret=client_secret,
#             tenant_id=tenant_id
#         )
#         subscription_client = SubscriptionClient(credentials)
#         subscription_details = {}

#         print("Subscriptions and their resource group counts:")

#         for subscription in subscription_client.subscriptions.list():
#             subscription_id = subscription.subscription_id
#             subscription_name = subscription.display_name

#             resource_client = ResourceManagementClient(credentials, subscription_id)
#             resource_groups = list(resource_client.resource_groups.list())
#             resource_group_count = len(resource_groups)

#             subscription_details[subscription_name] = resource_group_count

#         return subscription_details

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return {}

# #subscription_resource_group_counts = list_subscriptions_and_resource_groups(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
