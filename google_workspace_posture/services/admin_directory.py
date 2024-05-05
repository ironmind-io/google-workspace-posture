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
        'https://www.googleapis.com/auth/admin.directory.user.readonly',
        'https://www.googleapis.com/auth/admin.directory.userschema.readonly',
    ]
    
    def setup(self):
        try:
            service_account_info = json.loads(os.getenv('GOOGLE_API_KEY'))
            credentials = service_account.Credentials\
                    .from_service_account_info(
                        service_account_info, scopes=self.SCOPES)
            delegated_creds = credentials.with_subject(
                    os.getenv('GOOGLE_ADMIN_EMAIL'))
            service = build('admin', 'directory_v1',
                    credentials=delegated_creds)
            self.service = service
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


    def teardown(self):
        return True


    def load_data(self):

        if not self.service:
            self.setup()

        customer_id = os.getenv('GOOGLE_CUSTOMER_ID')
        request = self.service.users().list(customer=customer_id,
                projection='full', maxResults=100)
        while request is not None:
            response = request.execute()
            for user in response.get('users', []):
                yield user
            request = self.service.users().list_next(request, response)


