from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Reuse Strava functions from main.py or put them here:
STRAVA_CLIENT_ID = "YOUR_CLIENT_ID"
STRAVA_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
STRAVA_REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"

def get_access_token():
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "refresh_token": STRAVA_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def update_activity(access_token, activity_id, distance_meters):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "distance": distance_meters
    }
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

@app.route("/twilio-webhook", methods=["POST"])
def twilio_webhook():
    """
    This endpoint is called by Twilio whenever the user replies via SMS.
    We'll parse the user’s message (distance in miles), convert to meters,
    and update the *most recent* Strava activity that triggered the text.
    """
    try:
        # 1) Parse the incoming SMS body
        sms_body = request.form.get("Body", "").strip()
        
        # Attempt to parse a number from the SMS body
        # e.g., "3", "3.5", "3 miles", etc.
        match = re.search(r"(\d+(\.\d+)?)", sms_body)
        if not match:
            return "No valid number found.", 200
        
        miles = float(match.group(1))
        distance_meters = int(miles * 1609.34)

        # 2) Identify the activity to update
        #    (For simplicity, assume we just always update the last activity we flagged)
        #    A real system might store the "pending" activity_id somewhere in a DB
        #    or pass it along with the Twilio SMS in a custom field.
        with open("last_activity_id.txt", "r") as f:
            activity_id = int(f.read().strip())

        # 3) Get short-lived token, update activity
        access_token = get_access_token()
        updated = update_activity(access_token, activity_id, distance_meters)

        print(f"Updated activity {activity_id} with distance={distance_meters} meters.")
        
        # 4) Respond to Twilio
        return "Distance updated successfully.", 200

    except Exception as e:
        print(f"Error in twilio_webhook: {e}")
        return "Error", 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
