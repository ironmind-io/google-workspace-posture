from google_workspace_posture.check import Check, CheckPriority,\
        CheckStatus, CheckResult
from google_workspace_posture.services.admin_reports import AdminReports
from google_workspace_posture.services.admin_directory_users import AdminDirectoryUsers 
from google_workspace_posture.services.admin_directory_ou import AdminDirectoryOU
from google_workspace_posture.services.chrome_policy import ChromePolicy




class enforce_security_keys_for_admins(Check):
    '''
    This check identifies users who are not enrolled in 2SV.
    It lists users who are not enrolled.  It does NOT report the status
    of 2SV enforcement as this is not available via the API.
    '''

    id = "enforce_security_keys_for_admins"
    name = "Enforce Security Keys for Admins"
    description = '''
    This check identifies admin users who are not enrolled
    in 2SV using security keys. This places them at increased risk 
    of account compromise as security keys are resistant to 
    many phishing attacks.
    https://support.google.com/accounts/answer/6103523
    '''
    priority = CheckPriority.HIGH

    def check(self):
        params = 'accounts:is_super_admin,accounts:is_delegated_admin,accounts:num_security_keys'
        admins_missing_keys = []
        with AdminReports() as adm_rpt:
            data = adm_rpt.load_data(params)
            for i in data:
                report_data = i.get('parameters', [{}])
                is_admin = (report_data[0].get('boolValue', False)
                            or
                            report_data[1].get('boolValue', False))
                        
                has_keys = int(report_data[2].get('intValue', 0)) > 0
                if  is_admin and not has_keys:
                    admins_missing_keys.append(i['entity']['userEmail'])

        if len(admins_missing_keys) > 0:
            return CheckResult(
                id=self.id,
                result=CheckStatus.FAIL,
                message=f'{len(admins_missing_keys)} admin users are missing security keys: {", ".join(admins_missing_keys)}'
            )
        return CheckResult(
            id=self.id,
            result=CheckStatus.PASS,
            message='All admin users have security keys'   
        )


class require_2_step_verification_for_users(Check):
    '''
    This check identifies users who are not enrolled in 2SV.
    It lists users who are not enrolled.  It does NOT report the status
    of 2SV enforcement as this is not available via the API.
    '''

    id = "require_2_step_verification_for_users"
    name = "Require 2-Step Verification for Users"
    description = '''
    Require 2-Step Verification for Users.  
    2-Step Verification (a.k.a. 2FA, MFA) is one of the best ways
    to protect your account.  It requires a second verification step
    in addition to your password.  This check will identify users
    where the isEnforcedIn2Sv is False.
    Enforce 2SV as described here:
    https://support.google.com/a/answer/9176657
    '''
    priority = CheckPriority.CRITICAL

    def check(self):

        not_enforced_2sv = []
        not_enrolled_2sv = []
        with AdminDirectoryUsers() as dir_service:
            for u in dir_service.load_data():   
                if 'isEnforcedIn2Sv' in u and not u['isEnforcedIn2Sv']:
                    not_enforced_2sv.append(u['primaryEmail'])
                if 'isEnrolledIn2Sv' in u and not u['isEnrolledIn2Sv']:
                    not_enrolled_2sv.append(u['primaryEmail'])



        if len(not_enforced_2sv) > 0 and len(not_enrolled_2sv) == 0:
            #partial pass as some users are not enforced
            #but all users are enrolled

            msg = f'''
            2SV is not enforced for these users:
            {', '.join(not_enforced_2sv)}
            However, all users are enrolled in 2SV.
            '''
            return CheckResult(
                    id = self.id,
                    result = CheckStatus.PARTIAL_PASS,
                    message = \
                        'These users are not enforced in 2SV: {}'.format(
                        ', '.join(not_enforced_2sv)))


        if len(not_enrolled_2sv) > 0:
            return CheckResult(
                    id = self.id,
                    result = CheckStatus.FAIL,
                    message = \
                        'These user are not enrolled in 2SV: {}'.format(
                        ', '.join(not_enrolled_2sv)))
        else:
            return CheckResult(
                    id = self.id,
                    result = CheckStatus.PASS,
                    message = 'All users are enrolled in 2SV')


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
    with password alert setting is not enforced. This setting will alert a user when they are 
    reusing a password.  This can help prevent credential stuffing and other similar attacks.
    Note that this configuration requires additional setup when SSO is enabled.  For those 
    environments, the sso url must be configured as well.
    https://support.google.com/chrome/a/answer/9696707
    '''
    priority = CheckPriority.MEDIUM
    recommended =\
        "PASSWORD_PROTECTION_WARNING_TRIGGER_ENUM_WARN_ON_PASSWORD_REUSE"

    def check(self):

        failed_stmt = []
        with AdminDirectoryOU() as ou, ChromePolicy() as cs:
            for d in ou.load_data():     
                i = str(d['orgUnitId']).split(':')[-1]    
                policy = cs.load_data(i, 'chrome.users.PasswordAlert')      
                policy = next(policy, {})[0]
                print(policy)
                print(d)
                

                #check if policy is missing
                if not policy:
                    failed_stmt.append(
                        d['orgUnitPath']+" missing policy for "+\
                        "password alert. Default not recommended")

                pw_key = "passwordProtectionWarningTrigger"
                warn_setting =policy.get(pw_key, '')
                if warn_setting != self.recommended:
                    err_msg = d['orgUnitPath'] + \
                        " passwordProtectionWarningTrigger is not " +\
                        "warn on reuse"
                    failed_stmt.append(err_msg)

                chg_key = "passwordProtectionChangePasswordUrl"
                chg_setting = policy.get(chg_key, '')
                if not chg_setting:
                    err_msg = d['orgUnitPath'] + \
                        " missing passwordProtectionChangePasswordUrl " +\
                        "so resets will not be enforced"
                    failed_stmt.append(err_msg)

                protect_key = "passwordProtectionLoginUrls"
                protect_setting = policy.get(protect_key, '')
                if not protect_setting:
                    err_msg =  d['orgUnitPath'] + \
                        " missing passwordProtectionLoginUrls. "+\
                        "Passwords will not be monitored"
                    failed_stmt.append(err_msg)
            
        if len(failed_stmt) > 0:
            return CheckResult(
                id=self.id,
                result=CheckStatus.FAIL,
                message=f"{len(failed_stmt)} settins are misconfigured: "+\
                        "; ".join(failed_stmt)
            )
        return CheckResult(
            id=self.id,
            result=CheckStatus.PASS,
            message='All org units have password alert configured'   
        )


class use_unique_passwords(Check):

    id= "use_unique_passwords"
    name = "Use Unique Passwords"
    description = '''
    This check has not been implemented.  You should validate whether your 
    training and policies are effective in preventing password reuse.
    Password reuse and credential mismanagement is one of the leading causes of incidents.
    '''

    priority = CheckPriority.MEDIUM

    def check(self):
        return CheckResult(
            id=self.id,
            result=CheckStatus.SKIPPED,
            message='This check has not been implemented'
        )

                        
class regularly_review_activty_reports_and_alerts(Check):
    id= "regularly_review_activty_reports_and_alerts"
    name = "Regularly Review Activity Reports and Alerts"
    description = '''
    This check has not been implemented.  You should regularly review
    activity reports and alerts to identify suspicious activity.
    This will improve the probability of early detection of an incident.
    https://support.google.com/a/answer/4580176
    '''
    priority = CheckPriority.LOW

    def check(self):
        return CheckResult(
                id=self.id,
                result=CheckStatus.SKIPPED,
                message='This check has not been implemented'
        )




class set_up_admin_email_alerts(Check):
    id= "set_up_admin_email_alerts"
    name = "Set up Admin Email Alerts"
    description = '''
    This check has not been implemented.  You should set up admin email alerts
    to be notified of important events in your Google Workspace environment.
    These can be configured in the Rules section in the Admin console.
    https://support.google.com/a/answer/3230421
    '''
    priority = CheckPriority.MEDIUM

    def check(self):
        return CheckResult(
                id=self.id,
                result=CheckStatus.SKIPPED,
                message='This check has not been implemented'
        )


class identify_and_secure_compromised_accounts(Check):
    id= "identify_and_secure_compromised_accounts"
    name = "Identify and Secure Compromised Accounts"
    description = '''
    This check has not been implemented.  You should have a process in place
    to identify and secure compromised accounts.  This should be comprised of two components:
    1. Regular review and analysis of security logs and alerts
    2. A response plan in place to address compromised accounts
    https://support.google.com/a/answer/2984349
    '''
    priority = CheckPriority.HIGH

    def check(self):
        return CheckResult(
                id=self.id,
                result=CheckStatus.SKIPPED,
                message='This check has not been implemented'
        )


class turn_off_google_data_download_as_needed(Check):
    id= "turn_off_google_data_download_as_needed"
    name = "Turn off Google Data Download as needed"
    description = '''
    '''
    priority = CheckPriority.MEDIUM

    def check(self):
        return CheckResult(
                id=self.id,
                result=CheckStatus.SKIPPED,
                message='This check has not been implemented'
        )






