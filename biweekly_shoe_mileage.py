import os
import requests
import json
from datetime import datetime, timezone
from email.mime.text import MIMEText
import resend

# ====================================================
# Loading secrets from environment
# ====================================================
CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

KEYWORD = "new shoes"  # activity name marking start of current shoes
STORE_FILE = "shoe_data.json"

# ====================================================
# Refreshing Strava access token
# ====================================================
print("Refreshing Strava access token...")
token_response = requests.post(
    "https://www.strava.com/oauth/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
)

tokens = token_response.json()

# Safety check: Ensure we actually got a token back
if "access_token" not in tokens:
    print(f"Error refreshing token: {tokens}")
    exit(1)

access_token = tokens["access_token"]

# ====================================================
# Loading previous state (if it exists)
# ====================================================
if os.path.exists(STORE_FILE):
    with open(STORE_FILE, "r") as f:
        data = json.load(f)
        last_activity_date = datetime.fromisoformat(data.get("last_activity_date"))
        last_new_shoes_date = datetime.fromisoformat(data.get("last_new_shoes_date"))
        total_miles = data.get("miles", 0)
else:
    # First run defaults
    last_activity_date = datetime(1970, 1, 1, tzinfo=timezone.utc)
    last_new_shoes_date = datetime(1970, 1, 1, tzinfo=timezone.utc)
    total_miles = 0

after_timestamp = int(last_activity_date.timestamp())

# ====================================================
# Fetching new activities after last_activity_date
# ====================================================
runs = []
page = 1
per_page = 200

while True:
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "per_page": per_page,
            "page": page,
            "after": after_timestamp
        }
    )
    activities_page = response.json()
    if not activities_page:
        break

    # Filter only runs
    for act in activities_page:
        if act["type"] == "Run":
            runs.append(act)

    page += 1

# ====================================================
# Processing new runs
# ====================================================
for act in runs:
    act_date = datetime.fromisoformat(act["start_date"])
    
    # Check for new "new shoes" activity
    if KEYWORD in act["name"].lower():
        total_miles = act["distance"] / 1609.34  # reset mileage including this new shoes run mileage
        last_new_shoes_date = act_date  # start counting from this activity
    elif act_date > last_new_shoes_date:
        # Only add runs after the last "new shoes" run
        total_miles += act["distance"] / 1609.34  # meters → miles

# ====================================================
# Updating last_activity_date
# ====================================================
if runs:
    newest_run_date = datetime.fromisoformat(runs[-1]["start_date"])
    if newest_run_date > last_activity_date:
        last_activity_date = newest_run_date

# ====================================================
# Compiling message and sending email
# ====================================================
if total_miles < 400:
    message = f"You've run {round(total_miles, 2)} miles in your current shoes :)"
else:
    message = f"You hit {round(total_miles, 2)} miles! Time to buy new shoes!"

RESEND_KEY = os.environ["RESEND_KEY"]
resend.api_key = RESEND_KEY

r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "annp.scruggs@gmail.com",
  "subject": "Shoe Mileage Update",
  "html": message
})


# ====================================================
# Saving updated state
# ====================================================
with open(STORE_FILE, "w") as f:
    json.dump({
        "last_activity_date": last_activity_date.isoformat(),
        "last_new_shoes_date": last_new_shoes_date.isoformat(),
        "miles": total_miles
    }, f)