import os
import json
import argparse
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account


def run():
    from google_workspace_posture.checks.accounts import \
            require_2_step_verification_for_users,\
            prevent_password_reuse_with_password_alert,\
            enforce_security_keys_for_admins,\
            use_unique_passwords

    check = require_2_step_verification_for_users()

    result = check.check()   
    print(result)


    check = enforce_security_keys_for_admins()
    result = check.check()
    print(result)


    check = prevent_password_reuse_with_password_alert()
    result = check.check()
    print(result)

    check = use_unique_passwords()
    result = check.check()
    print(result)

def test():
    from google_workspace_posture.services.alertcenter_beta_alerts import\
        AlertcenterBetaAlerts 

    with AlertcenterBetaAlerts() as alert_center:
        print(list(alert_center.load_data()))
        for x in alert_center.load_data():
            print(x)





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


