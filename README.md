# Strava Shoe Mileage Tracker

Strava provides a notifier for miles run on your shoes. However, you have to tag the shoes you wear on every run - which I don't do. This automation tracks my miles-run on my current pair of shoes based on when I got them (the run I labelled "new shoes!"). 
The automation emails me a biweekly update so I never accidentally grind a pair past 400 miles.

---

## How It Works

The script (`biweekly_shoe_mileage.py`) runs automatically on a schedule via GitHub Actions. Each run it:

1. Authenticates with the Strava API using a stored refresh token
2. Fetches all new runs since the last check
3. Tallies up miles logged in **current shoes**
4. Sends an email via [Resend](https://resend.com) with current mileage
5. Saves state to `shoe_data.json` so it picks up where it left off next time

### Marking a New Pair of Shoes

When you start a new pair, name any Strava run with the phrase **`new shoes`**. The tracker will reset your mileage counter from that activity onward.
