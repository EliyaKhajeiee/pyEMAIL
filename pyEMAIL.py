import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import requests

# ZOHO SMTP SETTINGS
zoho_smtp = 'smtp.zoho.com'
zoho_port = 465  # FOR SSL
zoho_email = 'TTPartners@turntablepartners.com'
zoho_password = 'cd$fR_hVRWA8t/q'  # DON'T SHARE THIS

# AIRTABLE SETTINGS (THIS IS WHERE YOU ADD YOUR API INFO)
AIRTABLE_API_KEY = 'patsn4WX3r3zZIhzN.da8d21aa5d208de6d216e1d7c65cb9a3ec01215d85659bd2fd8fdc2b255cabd0'  # GET YOUR OWN KEY FROM AIRTABLE
BASE_ID = 'apporh2AVB1oN9AJn'  # FROM YOUR AIRTABLE URL, DON'T CHANGE THIS
TABLE_NAME = 'tblThJ4PSzyzo6t1w'  # ALSO FROM YOUR AIRTABLE URL

# AIRTABLE FIELD IDS (DON'T TOUCH THIS UNLESS YOU'RE CHANGING THE FIELDS)
FIELD_COMPANY_NAME = 'fldg6zXxZm1r3SGDR'
FIELD_RECIPIENT = 'fldrayuHuo0X4HjeJ'
FIELD_SUBJECT = 'fldGGXXeT7B4i0iBH'
FIELD_MESSAGE = 'fldXOZM81y0JLKvQD'

# FUNCTION TO PARSE EMAIL INPUT, AKA JUST GET THE COMPANY, RECIPIENT, ETC.
def parse_email_input(email_input):
    company = re.search(r'Company:\s*(.*)', email_input).group(1).strip()  # COMPANY NAME
    recipient = re.search(r'Recipient:\s*(.*)', email_input).group(1).strip()  # EMAIL ADDRESS
    subject = re.search(r'Subject:\s*(.*)', email_input).group(1).strip()  # EMAIL SUBJECT
    message = re.search(r'Message:\s*([\s\S]*)', email_input).group(1).strip()  # MESSAGE BODY
    return company, recipient, subject, message

# FUNCTION TO SEND EMAIL, THIS PART ACTUALLY SENDS IT USING ZOHO SMTP
def send_email(recipient_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = zoho_email  # WHO IT'S FROM (YOU)
    msg['To'] = recipient_email  # WHO IT'S GOING TO (THE CLIENT)
    msg['Subject'] = subject  # THE EMAIL SUBJECT

    msg.attach(MIMEText(message, 'plain'))  # THE BODY OF THE EMAIL

    try:
        server = smtplib.SMTP_SSL(zoho_smtp, zoho_port)  # CONNECT TO ZOHO
        server.login(zoho_email, zoho_password)  # LOG INTO ZOHO
        server.sendmail(zoho_email, recipient_email, msg.as_string())  # SEND THE EMAIL
        server.close()  # LOG OUT WHEN DONE

        print(f'EMAIL SENT TO {recipient_email}')
        return True
    except Exception as e:
        print(f'FAILED TO SEND EMAIL: {e}')  # IF SOMETHING GOES WRONG, YOU'LL KNOW
        return False

# FUNCTION TO LOG EMAIL DETAILS INTO AIRTABLE, THIS IS IMPORTANT
def log_to_airtable(company_name, recipient_email, subject, message):
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'  # THE AIRTABLE API ENDPOINT
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',  # YOUR API KEY TO AUTHENTICATE
        'Content-Type': 'application/json'  # DON'T CHANGE THIS, IT'S NEEDED FOR JSON
    }
    data = {
        'fields': {
            FIELD_COMPANY_NAME: company_name,  # LOG COMPANY NAME
            FIELD_RECIPIENT: recipient_email,  # LOG RECIPIENT EMAIL
            FIELD_SUBJECT: subject,  # LOG SUBJECT
            FIELD_MESSAGE: message  # LOG THE MESSAGE BODY
        }
    }

    response = requests.post(url, headers=headers, json=data)  # SEND THE DATA TO AIRTABLE

    if response.status_code == 200:
        print(f'SUCCESSFULLY LOGGED {recipient_email} TO AIRTABLE.')
    else:
        print(f'FAILED TO LOG TO AIRTABLE: {response.content}')  # ERROR MESSAGE IF IT FAILS

# MAIN FUNCTION TO PARSE EMAIL INPUT AND SEND THE EMAIL
def process_and_send_email(email_input):
    company, recipient, subject, message = parse_email_input(email_input)  # GET DATA

    email_sent = send_email(recipient, subject, message)  # SEND THE EMAIL

    if email_sent:  # ONLY LOG IF EMAIL WAS SENT SUCCESSFULLY
        log_to_airtable(company, recipient, subject, message)

# CONTINUOUS INPUT STREAM TO KEEP RUNNING UNTIL YOU DECIDE TO STOP
def continuous_input_stream():
    while True:
        print("PASTE THE ENTIRE EMAIL TEMPLATE BELOW (END WITH A SINGLE LINE CONTAINING ONLY 'END'):")
        email_input = ""
        while True:
            line = input()
            if line.strip() == "END":
                break
            email_input += line + "\n"
        process_and_send_email(email_input)  # PROCESS AND SEND THE EMAIL

# RUN THIS FUNCTION TO START THE SCRIPT
if __name__ == "__main__":
    continuous_input_stream()  # KEEP IT RUNNING UNTIL YOU'RE DONE
