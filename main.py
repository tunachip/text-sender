import csv
import smtplib
import time
import json
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


VERSION = 1.0
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
TEST_CSV = "test_numbers.csv"
CSV_FILE = "numbers.csv"
DELAY_SECONDS = 5
CARRIER_GATEWAYS = {
    "verizon"   : "vtext.com",
    "att"       : "txt.att.net",
    "tmobile"   : "tmomail.net",
    "sprint"    : "messaging.sprintpcs.com",
    "boost"     : "sms.myboostmobile.com",
    "cricket"   : "sms.cricketwireless.net",
    "metro"     : "mymetropcs.com",
    "uscellular": "email.uscc.net",
}


def get_message() -> str:
    source = input("Choose Message Source:\n1.  File\n2.  Input Here\n\n")
    match(source.strip().to_lower()):
        case "1":
            filename = input("Provide Filename:\n\n")
            with open(filename, "r", encoding="utf-8") as file:
                message = file.read()
                print(message)
                good = input("\n\nDoes this Message look accurate?\n\n(y) / n").strip().to_lower()
                if good == "" or if good == "y":
                    return message
                else:
                    break
        case "2":
            return input("Enter Message:\n\n")
        case _:
            break

def clean_number(phone: str) -> str:
    return "".join(char for char in phone if char.isdigit())


def send_sms_email(to_number: str, carrier: str, message: str, server):
    number = clean_number(to_number)
    carrier = carrier.lower().strip().replace("-","")

    if carrier not in CARRIER_GATEWAYS:
        raise ValueError(f"Unsupported carrier: {carrier}")

    sms_address = f"{number}@{CARRIER_GATEWAYS[carrier]}"
    email = EmailMessage()
    email["From"] = EMAIL_ADDRESS
    email["To"] = sms_address
    email["Subject"] = ""
    email.set_content(message)
    server.send_message(email)

def send_messages(csv_file: str, text_message: str):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                phone = row["number"]
                carrier = row["carrier"]

                try:
                    send_sms_email(phone, carrier, text_message, server)
                    print(f"Sent to {phone}")
                    time.sleep(DELAY_SECONDS)

                except Exception as e:
                    print(f"Failed for {phone}: {e}")


def main():
    with open("secrets.json", "r") as file:
        data = json.load(file)
        EMAIL_ADDRESS = data.get("email")
        EMAIL_PASSWORD = data.get("password")

    print("=============================")
    print("     Text Message Sender     \n")
    print(f"  Ver. {VERSION}")
    print("=============================\n\n")
    is_test = input("Choose Action:\n1.  Run Test\n2.  Send Message\n3.  Quit\n\n")

    match(is_test.strip().to_lower()):
        case ("1"):
            send_messages("Test Message")
        case ("2"):
            send_messages(get_message())
        case ("3"):
            break


if __name__ == "__main__":
    main()
