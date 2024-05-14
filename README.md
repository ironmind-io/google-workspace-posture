# IronMind.io Google Workspace Posture


## Overview
This implements automated checks against Google Workspace's recommended security checklist
(and maybe more in the future).  See a full list of the checks 
[here](https://support.google.com/a/answer/7587183?sjid=15506710759404807892-NA#zippy=%2Cadministrator-accounts%2Capps-google-workspace-only%2Caccounts)



## Creating a Service Account
Enable the Admin SDK API and Chrome Policy API:

    Go to the Google Cloud Console.
    Select or create a project.
    Navigate to "APIs & Services" > "Library".
    Search for "Admin SDK" and enable it
		Search for "Chrome Policy" and enable it
		Search for "Google Workspace Alert Center API" and enable it

Create Service Account and Credentials:

    In the same project, go to "IAM & Admin" > "Service Accounts".
    Create a new service account.
    Assign it a role like "Reports Viewer" or a custom role with the necessary permissions.
    Create and download a JSON key file for this account.
    NOTE - you may need to disable "Disable service account key creation" Organization Policy.
    This will require Organization Policy Administrator role and can be done 
    in IAM and Admin > Organization Policies at the organization level.

Delegate domain-wide authority to the service account:

    Go to your Google Workspace admin panel.
    Go to "Security" > "API Controls" > "Domain wide delegation".
    Add the client ID (AKA unique ID, the numeric one) of your service account 
    Specify the required scopes. 
    	https://www.googleapis.com/auth/admin.chrome.printers.readonly
	https://www.googleapis.com/auth/admin.directory.customer.readonly
	https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly
	https://www.googleapis.com/auth/admin.directory.device.mobile.readonly
	https://www.googleapis.com/auth/admin.directory.domain.readonly
	https://www.googleapis.com/auth/admin.directory.group.member.readonly
	https://www.googleapis.com/auth/admin.directory.group.readonly
	https://www.googleapis.com/auth/admin.directory.orgunit.readonly
	https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly
	https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly
	https://www.googleapis.com/auth/admin.directory.user.alias.readonly
	https://www.googleapis.com/auth/admin.directory.user.readonly
	https://www.googleapis.com/auth/admin.directory.userschema.readonly





