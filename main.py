import csv
import smtplib
import time
import json
import sys
import os
from email.message import EmailMessage

"""
Setup Instructions:

To use this tool you will need a Gmail Account (Burner is Sufficient)

1. Enable 2 Factor Authentication
  'https://myaccount.google.com/signinoptions/twosv'

2. Create an App Password
  'https://myaccount.google.com/u/2/apppasswords'

3. Create 'secrets.json' File

Structure secrets.json as such:

{
  "email": "EMAIL_ADDRESS@google.com",
  "password": "GOOGLE_APP_PASSWORD_HERE"
}

4. Create Numbers File

Place Numbers in numbers.csv as such:
'''
number,provider
1234567890,tmobile
'''

5. (Optional) Create Test Numbers File

Place your own Phone Number in test_numbers.csv as a test, with matching structure.
'''
number,provider
1234567890,tmobile
'''

"""


VERSION = 1.2
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
TEST_CSV = "test_numbers.csv"
CSV_FILE = "numbers.csv"
DELAY_SECONDS = 5

# Set to "sms" for normal text gateways or "mms" for multimedia/longer-message gateways.
MESSAGE_GATEWAY_TYPE = "mms"

SMS_CARRIER_GATEWAYS = {
    "verizon"   : "vtext.com",
    "att"       : "txt.att.net",
    "tmobile"   : "tmomail.net",
    "sprint"    : "messaging.sprintpcs.com",
    "boost"     : "sms.myboostmobile.com",
    "cricket"   : "sms.cricketwireless.net",
    "metro"     : "mymetropcs.com",
    "uscellular": "email.uscc.net",
}

MMS_CARRIER_GATEWAYS = {
    "verizon"   : "vzwpix.com",
    "att"       : "mms.att.net",
    "tmobile"   : "tmomail.net",
    "sprint"    : "pm.sprint.com",
    "boost"     : "myboostmobile.com",
    "cricket"   : "mms.cricketwireless.net",
    "metro"     : "mymetropcs.com",
    "uscellular": "mms.uscc.net",
}

CARRIER_GATEWAYS = {
    "sms": SMS_CARRIER_GATEWAYS,
    "mms": MMS_CARRIER_GATEWAYS,
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_message() -> str:
    clear_screen()
    source = input("Choose Message Source:\n1.  File\n2.  Input Here\n\n")
    match(source.strip().lower()):
        case "1":
            filename = input("Provide Filename:\n\n")
            with open(filename, "r", encoding="utf-8") as file:
                message = file.read()
                clear_screen()
                print("\n" + message)
                good = input("\nDoes this Message look accurate?\n(Y)/n\n").strip().lower()
                if good == "" or good == "y":
                    return message
                else:
                    sys.exit(1)
        case "2":
            return input("Enter Message:\n\n")
        case _:
            sys.exit(1)

def clean_number(phone: str) -> str:
    return "".join(char for char in phone if char.isdigit())


def send_sms_email(
    sender: str,
    to_number: str,
    carrier: str,
    message: str,
    server
):
    number = clean_number(to_number)
    carrier = carrier.lower().strip().replace("-","").replace("&","")

    gateway_type = MESSAGE_GATEWAY_TYPE.lower().strip()
    if gateway_type not in CARRIER_GATEWAYS:
        raise ValueError(f"Unsupported gateway type: {MESSAGE_GATEWAY_TYPE}")

    gateways = CARRIER_GATEWAYS[gateway_type]
    if carrier not in gateways:
        raise ValueError(f"Unsupported carrier: {carrier}")

    sms_address = f"{number}@{gateways[carrier]}"
    email = EmailMessage()
    email["From"] = sender
    email["To"] = sms_address
    email["Subject"] = ""
    email.set_content(message)
    server.send_message(email)

def send_messages(csv_file: str, text_message: str):
    clear_screen()
    with open("secrets.json", "r") as file:
        data = json.load(file)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(data.get("email"), data.get("password"))
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                phone = row["number"]
                carrier = row["carrier"]
                try:
                    send_sms_email(
                        data.get("email"),
                        phone,
                        carrier,
                        text_message,
                        server
                    )
                    print(f"Sent to {phone}")
                except Exception as e:
                    print(f"Failed for {phone}: {e}")
                time.sleep(DELAY_SECONDS)


def main():
    print("=============================")
    print("     Text Message Sender     \n")
    print(f"  Ver. {VERSION}")
    print("=============================\n\n")
    is_test = input("Choose Action:\n1.  Run Test\n2.  Send Message\n3.  Quit\n\n")

    match(is_test.strip().lower()):
        case ("1"):
            send_messages("test_numbers.csv", get_message())
        case ("2"):
            send_messages("numbers.csv", get_message())
        case ("3"):
            sys.exit(1)


if __name__ == "__main__":
    main()
