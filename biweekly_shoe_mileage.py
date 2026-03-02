#automatic for github
import os
import smtplib
from email.mime.text import MIMEText
from stravalib.client import Client
from datetime import datetime

# --- Load secrets ---
CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
RECIPIENT = os.environ["RECIPIENT_EMAIL"]

KEYWORD = "new shoes"  # activity name marking start of current shoes

# --- Initialize Strava client ---
client = Client()

token_response = client.refresh_access_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    refresh_token=REFRESH_TOKEN
)
client.access_token = token_response["access_token"]


# Pull only running activities (most recent 200)
activities = list(client.get_activities(limit=200, activity_type='Run'))
activities.sort(key=lambda x: x.start_date_local)  # oldest → newest

# --- Find start index of current shoes ---
start_index = 0
for idx, act in enumerate(activities):
    if KEYWORD.lower() in act.name.lower():
        start_index = idx
        break

# --- Sum miles since start_index ---
total_miles = 0
for i in activities[start_index:]:
    total_miles += act.distance.num 

# --- Prepare email message ---
#if total_miles < 400:
#    message = f"You have run {total_miles:.1f} miles in your current shoes."
#else:
#    message = f"Woohoo! You hit {total_miles:.1f} miles! Time to buy new shoes!!"

# --- Send email ---
#msg = MIMEText(message)
#msg["Subject"] = "Shoe Mileage Update"
#msg["From"] = EMAIL_ADDRESS
#msg["To"] = RECIPIENT

#with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#    server.send_message(msg)

#print("✅ Email sent.")