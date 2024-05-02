from google_workspace_posture.services.service import Service
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import os   
import logging


class AdminDirectory(Service):

    def validate_config(self):
        if not os.getenv('GOOGLE_CUSTOMER_ID'):
            return "Missing GOOGLE_CUSTOMER_ID"
        if not os.getenv('GOOGLE_ADMIN_EMAIL'):
            return "Missing GOOGLE_ADMIN_EMAIL"
        if not os.getenv('GOOGLE_API_KEY'):
            return "Missing GOOGLE_API_KEY"
        return ''
    SCOPES = [
        #'https://www.googleapis.com/auth/admin.chrome.printers.readonly',     
        #'https://www.googleapis.com/auth/admin.directory.customer.readonly',  
        #'https://www.googleapis.com/auth/admin.directory.device.chromeos.readonl    y',
        #'https://www.googleapis.com/auth/admin.directory.device.mobile.readonly'    ,                                                                        
        #'https://www.googleapis.com/auth/admin.directory.domain.readonly',
        #'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
        #'https://www.googleapis.com/auth/admin.directory.group.readonly',  
        #'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
        #'https://www.googleapis.com/auth/admin.directory.resource.calendar.reado    nly',    
        #'https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly    ',
        #'https://www.googleapis.com/auth/admin.directory.user.alias.readonly',
        'https://www.googleapis.com/auth/admin.directory.user.readonly',
        'https://www.googleapis.com/auth/admin.directory.userschema.readonly' 
    ]
    
    def load_service(self):
        try:
            service_account_info = json.loads(os.getenv('GOOGLE_API_KEY'))
            credentials = service_account.Credentials\
                    .from_service_account_info(
                        service_account_info, scopes=self.SCOPES)
            delegated_creds = credentials.with_subject(
                    os.getenv('GOOGLE_ADMIN_EMAIL'))
            service = build('admin', 'directory_v1',
                    credentials=delegated_creds)
            return service
        except Exception as e:
            logging.error(e)
            msg = '''
            Error loading AdminDirectory service.
            Likely causes:
                - API scopes are not correct
                - env vars incorrect or missing:
                    - GOOGLE_CUSTOMER_ID
                    - GOOGLE_ADMIN_EMAIL
                    - GOOGLE_API_KEY
            '''

            raise Exception(msg, "\n\n", e)
