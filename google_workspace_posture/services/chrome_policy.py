from google_workspace_posture.services.service import Service
from google_workspace_posture.config import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json 
import os     
import logging

                                   
class ChromePolicy(Service):
    SCOPES = [
        'https://www.googleapis.com/auth/chrome.management.policy.readonly']
   
   
    def setup(self):
        try:
            c = config['google']  
            k = json.loads(c['api_key'])
            credentials = service_account.Credentials\
                    .from_service_account_info(
                        k, scopes=self.SCOPES) 
            delegated_creds = credentials.with_subject(
                    c['admin_email'])
            service = build('chromepolicy', 'v1',
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
        
    
    def load_data(self, ou, policy_key):
    
        if not hasattr(self, 'service'):
            self.setup()    


        response = self.service.customers().policies().resolve(
            customer='customers/' +config['google']['customer_id'],
            body={
                'policySchemaFilter': policy_key,
                'policyTargetKey': {'targetResource': 'orgunits/'+ou}
            }
        ).execute()
        if response:
            yield response['resolvedPolicies']



