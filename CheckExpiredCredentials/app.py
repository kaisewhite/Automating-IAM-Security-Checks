from re import sub
from botocore.exceptions import ClientError
from datetime import datetime, date
import boto3
import json
iam = boto3.client('iam')
ses = boto3.client('ses', region_name='us-east-1')


def send_ses(sender, recipient, subject, body):
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = ses.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body,
                    },

                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def get_age(date):
    delta = (datetime.now().date() - date)
    return delta.days


def lambda_handler():

    for user in iam.list_users()['Users']:

        access_key_metadata = iam.list_access_keys(UserName=user['UserName'])[
            'AccessKeyMetadata'][0]
        access_key = access_key_metadata.get(
            "AccessKeyId", datetime.now())
        access_key_status = access_key_metadata.get(
            "Status", datetime.now())
        access_key_create_date = access_key_metadata.get(
            "CreateDate", datetime.now())

        access_key_age = get_age(access_key_create_date.date())
        password_age = get_age(
            user.get("PasswordLastUsed", datetime.now()).date())

        list_mfa_devices = iam.list_mfa_devices(UserName=user['UserName'])
        users = []

        # Check for Inactive API Keys
        if access_key_status == 'Inactive':
            subject = f"Access Key Deletion Notice - Your AWS Access Keys Have Been Deleted"
            recipient = user['UserName']
            body = f"""<html>
                <head></head>
                <body>
                  <h1>Dear {recipient},</h1>
                  <p></p>
                  <p>Your AWS API access keys have been deleted because they
                    are more than 90 days old. You will need to login to the console to generate
                    new access keys in order to make programmatic calls to AWS from the AWS CLI, 
                    Tools for PowerShell, AWS SDKs, or direct AWS API calls. </b
                    To generate new keys please go to: <a href='https://aws.amazon.com/sdk-for-python/'> </b
                    <p>If you need any help, contact us via email: helpdesk@nih.gov. </br> </
                    Sincerely, <br />
                    The IT Department. <br />
                    </p>"
                    </p>
                </body>
                </html>"""
            #print(subject, recipient)
            # Delete Access Key if it is inactive
            # iam.delete_access_key(
            #    Username=user['UserName'], AccessKeyId=access_key)
        if access_key_age >= 80:
            subject = f"Access Key Expiration Notice - Your AWS Access Keys Expire In {90 - access_key_age} Days"
            recipient = user['UserName']
            body = f"""<html>
                <head></head>
                <body>
                  <h1>Dear {recipient},</h1>
                  <p></p>
                  <p>Your AWS API access keys will expire soon. Please generate new access keys. You will need to login to the console to generate
                    new access keys in order to make programmatic calls to AWS from the AWS CLI, 
                    Tools for PowerShell, AWS SDKs, or direct AWS API calls. </b
                    To generate new keys please go to: <a href='https://aws.amazon.com/sdk-for-python/'> </b
                    <p>If you need any help, contact us via email: helpdesk@nih.gov. <br /></
                    Sincerely, <br />
                    The IT Department. <br />
                    </p>"
                    </p>
                </body>
                </html>"""
            #print(subject, recipient)

        if access_key_age > 90:
            # iam.update_access_key(
            #    Username=user['UserName'], AccessKeyId=access_key,
            #    Status='Inactive')
            recipient = user['UserName']
            subject = f"Access Key Expiration Notice - Your AWS Access Keys Have Been Deactivated"
            body = f"""<html>
                            <head></head>
                            <body>
                              <h1>Dear {recipient},</h1>
                              <p></p>
                              <p>Your AWS API access keys have been deactived because they
                                are more than 90 days old. You will need to login to the console to generate
                                new access keys in order to make programmatic calls to AWS from the AWS CLI, 
                                Tools for PowerShell, AWS SDKs, or direct AWS API calls. </br>

                                To generate new keys please go to: <a href='https://aws.amazon.com/sdk-for-python/'> </br>

                                <p>If you need any help, contact us via email: helpdesk@nih.gov. </br> </p>

                                Sincerely, <br />
                                The IT Department. <br />
                                </p>"
                                </p>
                            </body>
                            </html>"""

            #print(subject, recipient)

        # Check for passwords older 80 days
        if password_age >= 80:
            subject = f"Password Expiration Notice - Your AWS password expires in {90 - access_key_age} Days"
            recipient = user['UserName']
            body = f"""<html>
                <head></head>
                <body>
                  <h1>Dear {recipient},</h1>
                  <p></p>
                  <p>Your AWS password will expire soon. You will need to login to the console to generate
                    update your password. </br>
                    To update your password please go to: <a href='https://aws.amazon.com/sdk-for-python/'> </br>
                    <p>If you do not update your password in {90 - access_key_age} days, you will not be able to log in, so please make sure you update your password. </br></p>
                    <p>If you need any help, contact us via email: helpdesk@nih.gov. </br>
                    Sincerely, <br />
                    The IT Department. <br />
                    </p>"
                    </p>
                </body>
                </html>"""
            #print(subject, recipient)

        if password_age > 90:
            # iam.delete_login_profile(
            #    UserName=user['UserName']
            # )
            subject = f"Password Expiration Notice - Your AWS Account Has Been Disabled"
            recipient = user['UserName']
            body = f"""<html>
                <head></head>
                <body>
                  <h1>Dear {recipient},</h1>
                  <p></p>
                  <p>Your AWS account has been disabled. You will need to contact helpdesk in order to unlock your account
                    <p>If you need any help, contact us via email: helpdesk@nih.gov. </br>
                    Sincerely, <br />
                    The IT Department. <br />
                    </p>"
                    </p>
                </body>
                </html>"""
            #print(subject, recipient)

        # Check if MFA is enabled
        if len(list_mfa_devices['MFADevices']) == 0:
            subject = f"Enable MFA Notice - MFA Not Enabled on AWS Account"
            recipient = user['UserName']
            body = f"""<html>
                <head></head>
                <body>
                  <h1>Dear {recipient},</h1>
                  <p></p>
                  <p>This is your daily reminder to enable MFA on your AWS account. </br>
                    
                    <p> Sign in to the AWS Management Console. <a href='https://aws.amazon.com/sdk-for-python/'></br>
                    <p> In the navigation pane at the top, click on your name/username. </br>
                    <p> Choose the Security credentials tab. </br>
                    <p> Next to Assigned MFA device, choose Manage.</br>
                    <p> In the Manage MFA Device wizard, choose Virtual MFA device, and then choose Continue. </br>

                    <p>If you need any help, contact us via email: helpdesk@nih.gov. </br>
                    Sincerely, <br />
                    The IT Department. <br />
                    </p>"
                    </p>
                </body>
                </html>"""
            print(subject, recipient)


# print("User: {0}\nUserID: {1}\nARN: {2}\nCreatedOn: {3}\nPasswordAge: {4}\nAccessKeyStatus: {5}\nAccessKeyAge: {6}\n".format(
    #    user['UserName'],
    #    user['UserId'],
    #    user['Arn'],
    #    user.get("CreateDate", datetime.now()).date(),
    #    password_age,
    #    access_key_status,
    #    access_key_age
    # )
    # )
