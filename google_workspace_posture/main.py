import os
import json
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account


# Load environment variables from .env file
load_dotenv()

# Use environment variables
GOOGLE_API_JSON = os.getenv('GOOGLE_API_JSON')
GOOGLE_CUSTOMER_ID= os.getenv('GOOGLE_CUSTOMER_ID')
SCOPES = [
        'https://www.googleapis.com/auth/admin.directory.user'
#        'https://www.googleapis.com/auth/admin.chrome.printers.readonly',  
#        'https://www.googleapis.com/auth/admin.directory.customer.readonly',  
#        'https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly',
#        'https://www.googleapis.com/auth/admin.directory.device.mobile.readonly',
#        'https://www.googleapis.com/auth/admin.directory.domain.readonly',
#        'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
#        'https://www.googleapis.com/auth/admin.directory.group.readonly',
#        'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
#        'https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly',    
#        'https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly',
#        'https://www.googleapis.com/auth/admin.directory.user.alias.readonly',
#        'https://www.googleapis.com/auth/admin.directory.user.readonly',
#        'https://www.googleapis.com/auth/admin.directory.userschema.readonly'
]

def get_admin_sdk_service():
    
    if GOOGLE_API_JSON is None:
        raise ValueError("GOOGLE_API_JSON environment variable not set")

    # Parse the JSON credentials from the environment variable
    service_account_info = json.loads(GOOGLE_API_JSON)
    
    # Create service account credentials from the JSON data
    #credentials = service_account.Credentials.from_service_account_info(
    #    service_account_info, scopes=SCOPES)
    credentials = service_account.Credentials.from_service_account_file(
        '/home/tash/Downloads/infrastructure-422020-5ae0ee340e81.json', scopes=SCOPES)
    delegated_creds = credentials.with_subject('tadashi@nominaloffice.us')
    
    # Build the service object
    service = build('admin', 'directory_v1', credentials=delegated_creds)
    return service

def check_2sv_enforcement():
    service = get_admin_sdk_service()
    users = service.users().list(customer=GOOGLE_CUSTOMER_ID, projection='full').execute()
    print(users)
    print(users['users'][0])

if __name__ == '__main__':
    check_2sv_enforcement()


