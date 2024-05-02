import os
import json
import argparse
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account


## Use environment variables
#GOOGLE_API_JSON = os.getenv('GOOGLE_API_JSON')
#GOOGLE_CUSTOMER_ID= os.getenv('GOOGLE_CUSTOMER_ID')
#GOOGLE_ADMIN_EMAIL = os.getenv('GOOGLE_ADMIN_EMAIL')
#SCOPES = [
#    'https://www.googleapis.com/auth/admin.chrome.printers.readonly',  
#    'https://www.googleapis.com/auth/admin.directory.customer.readonly',  
#    'https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly',
#    'https://www.googleapis.com/auth/admin.directory.device.mobile.readonly',
#    'https://www.googleapis.com/auth/admin.directory.domain.readonly',
#    'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
#    'https://www.googleapis.com/auth/admin.directory.group.readonly',
#    'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
#    'https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly',    
#    'https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly',
#    'https://www.googleapis.com/auth/admin.directory.user.alias.readonly',
#    'https://www.googleapis.com/auth/admin.directory.user.readonly',
#    'https://www.googleapis.com/auth/admin.directory.userschema.readonly'
#]
#
#def get_admin_sdk_service():
#    
#    if GOOGLE_API_JSON is None:
#        raise ValueError("GOOGLE_API_JSON environment variable not set")
#
#    # Parse the JSON credentials from the environment variable
#    service_account_info = json.loads(GOOGLE_API_JSON)
#    
#    credentials = service_account.Credentials.from_service_account_info(
#        service_account_info, scopes=SCOPES)
#    delegated_creds = credentials.with_subject(GOOGLE_ADMIN_EMAIL)
#    
#    # Build the service object
#    service = build('admin', 'directory_v1', credentials=delegated_creds)
#    return service
#
#def check_2sv_enforcement(adm_service, customer_id):
#    service = get_admin_sdk_service()
#    all_users = []
#    request = service.users().list(customer=GOOGLE_CUSTOMER_ID, projection='full', maxResults=100)
#
#    while request is not None:
#        response = request.execute()
#        users = response.get('users', [])
#        all_users.extend(users)
#        request = service.users().list_next(previous_request=request, previous_response=response)
#
#    return all_users
def run():
    from google_workspace_posture.services.admin_directory import \
            AdminDirectory
    from google_workspace_posture.checks\
            .require_2_step_verification_for_users import \
            require_2_step_verification_for_users
    adm_service = AdminDirectory() #env var config
    valid = adm_service.validate_config()
    if valid:
        raise ValueError("Invalid configuration %s" % valid)

    admin_service = adm_service.load_service()   

    check = require_2_step_verification_for_users({
        'service': admin_service,
        'customer_id': os.getenv('GOOGLE_CUSTOMER_ID')
    })

    result = check.check()   
    print(result)






def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Google Workspace Posture')
    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run',\
        help='Run the Google Workspace Posture check')
    run_parser.set_defaults(func=run)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


