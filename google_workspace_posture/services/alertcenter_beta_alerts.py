from google_workspace_posture.services.service import Service
from google_workspace_posture.config import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import os   
import logging

class AlertcenterBetaAlerts(Service): 
    #https://developers.google.com/admin-sdk/alertcenter/reference/rest/v1beta1/TopLevel/getSettings
    SCOPES = [
        'https://www.googleapis.com/auth/apps.alerts',
    ]
    
    def setup(self):
        try:
            c = config['google']
            k = json.loads(c['api_key'])
            credentials = service_account.Credentials.from_service_account_info(
                k, scopes=self.SCOPES)
            delegated_creds = credentials.with_subject(c['admin_email'])
            service = build('alertcenter', 'v1beta1', credentials=delegated_creds)
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
        if not hasattr(self, 'service'):
            self.setup()

        customer_id = config['google']['customer_id']
        #request = self.service.settings(customerId=customer_id)
        request = self.service.alerts().list()

        while request is not None:
            response = request.execute()
            print(response)
            
            for alert in response.get('alerts', []):
                yield alert
            
            # Check if there's a nextPageToken provided in the response
            page_token = response.get('nextPageToken', False)
            if page_token:
                request = self.service.alerts().list(pageToken=page_token)
            else:
                request = None


