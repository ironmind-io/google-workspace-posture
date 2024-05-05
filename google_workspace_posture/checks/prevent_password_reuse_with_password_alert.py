from google_workspace_posture.check import CheckPriority, CheckStatus,\
        CheckResult, Check, CheckError
from google_workspace_posture.services.admin_directory import AdminDirectory

class prevent_password_reuse_with_password_alert(Check):
    '''
    This check identifies users who are not enrolled in 2SV.
    It lists users who are not enrolled.  It does NOT report the status
    of 2SV enforcement as this is not available via the API.
    '''

    id = "prevent_password_reuse_with_password_alert"
    name = "Prevent password reuse with password alert"
    description = '''
    This check identifies org units where the password reuse
    with password alert setting is not enforced.
    https://support.google.com/chrome/a/answer/9696707
    '''
    priority = CheckPriority.HIGH

    
    def __init__(self, config):

        #build admin directory serviceS
        self.admin_directory = AdminDirectory(config)
        error_msg = self.admin_directory.validate_config()

        if error_msg:
            raise CheckError(error_msg)

    def check(self):
        
        service = self.admin_directory.load_service()




    

