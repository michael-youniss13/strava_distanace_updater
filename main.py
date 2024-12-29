import time
import requests
from twilio.rest import Client  # Twilio Python helper library

# --------------------------------------------------------------------
# 1) STRAVA CONFIG
# --------------------------------------------------------------------
STRAVA_CLIENT_ID = "YOUR_CLIENT_ID"
STRAVA_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
STRAVA_REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"

# For polling the last known activity
LAST_ACTIVITY_ID_FILE = "last_activity_id.txt"

# --------------------------------------------------------------------
# 2) TWILIO CONFIG
# --------------------------------------------------------------------
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
FROM_PHONE_NUMBER = "+123456789"   # Twilio number
TO_PHONE_NUMBER   = "+1987654321" # User’s phone

# --------------------------------------------------------------------
# UTILS
# --------------------------------------------------------------------
def get_access_token():
    """
    Exchanges a refresh token for a short-lived Strava access token.
    """
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "refresh_token": STRAVA_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"]

def get_activities(access_token, per_page=10):
    """
    Fetch recent activities from Strava.
    """
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": per_page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def send_sms(body_text):
    """
    Send an SMS via Twilio.
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=body_text,
        from_=FROM_PHONE_NUMBER,
        to=TO_PHONE_NUMBER
    )
    return message.sid

# --------------------------------------------------------------------
# MAIN POLLING LOOP
# --------------------------------------------------------------------
def main():
    print("Starting Strava poller...")

    while True:
        try:
            # 1) Get short-lived access token
            access_token = get_access_token()
            
            # 2) Fetch recent activities
            activities = get_activities(access_token, per_page=3)

            # 3) Get last known activity ID (local file or DB)
            try:
                with open(LAST_ACTIVITY_ID_FILE, "r") as f:
                    last_id = int(f.read().strip())
            except FileNotFoundError:
                last_id = 0

            # 4) Check each activity to see if it's new & relevant
            for act in activities:
                act_id = act["id"]
                if act_id > last_id:
                    # Check if the activity is "Workout"/"HIIT"/etc
                    activity_type = act.get("type", "")
                    activity_name = act.get("name", "")
                    
                    # Example: If the name contains "HIIT" or type is "Workout"
                    if "hiit" in activity_name.lower() or activity_type.lower() in ("workout", "crossfit"):
                        print(f"Found new HIIT-like activity: {act_id} ({activity_name})")
                        
                        # 5) Send user an SMS
                        body_text = (f"We noticed you did a HIIT workout: '{activity_name}'. "
                                     "Reply with the number of miles if you want to add a distance.")
                        send_sms(body_text)
                    
                    # Update our last_id
                    if act_id > last_id:
                        last_id = act_id
            
            # 6) Write last_id to file
            with open(LAST_ACTIVITY_ID_FILE, "w") as f:
                f.write(str(last_id))
        
        except Exception as e:
            print(f"Error: {e}")

        # Poll every 5 minutes (adjust as needed)
        time.sleep(300)

if __name__ == "__main__":
    main()
