import os
import json
import argparse
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account


def run():
    from google_workspace_posture.services.admin_directory import \
            AdminDirectory
    from google_workspace_posture.checks.accounts import \
            require_2_step_verification_for_users,\
            enforce_security_keys_for_admins

    check = require_2_step_verification_for_users()

    result = check.check()   
    print(result)


    check = enforce_security_keys_for_admins()
    result = check.check()
    print(result)

def test():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    SCOPES = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.device.chromeos',
            'https://www.googleapis.com/auth/admin.directory.orgunit',
            'https://www.googleapis.com/auth/chrome.management.policy.readonly'
    ]
    
    api_key = os.getenv('GOOGLE_API_KEY')
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(api_key), scopes = SCOPES
    )

    delegated_creds = credentials.with_subject(
            os.getenv('GOOGLE_ADMIN_EMAIL'))
    
    service = build('admin', 'directory_v1', credentials=delegated_creds)

    chromeservice = build('chromepolicy', 'v1', credentials=delegated_creds)


    response = service.customers().policies().resolve(
        customer='customers/' + os.getenv('GOOGLE_CUSTOMER_ID'),
        body={
            'policySchemaFilter': 'chrome.users.*'  # Adjust this filter based on your needs
        }
    ).execute()





def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Google Workspace Posture')
    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run',\
        help='Run the Google Workspace Posture check')
    run_parser.set_defaults(func=run)

    test_parser = subparsers.add_parser('test',\
        help='Test Google Workspace Posture')
    test_parser.set_defaults(func=test)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


