from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
# run_with_ngrok(app)
# -------------------------------------------------
# 1) VERIFY THE SUBSCRIPTION (GET endpoint)
# -------------------------------------------------
@app.route("/strava/webhook", methods=["GET"])
def strava_webhook_verify():
    """
    Strava will send a GET request to verify you own the endpoint.
    The GET includes 'hub.mode', 'hub.verify_token', and 'hub.challenge'.
    You must respond with a JSON containing the 'hub.challenge'.
    """
    # E.g., ?hub.mode=subscribe&hub.challenge=1234&hub.verify_token=SOME_TOKEN
    mode = request.args.get("hub.mode", "")
    verify_token = request.args.get("hub.verify_token", "")
    challenge = request.args.get("hub.challenge", "")

    # Optional: Check that 'verify_token' matches what you set when you create the subscription
    # if verify_token != "YOUR_RANDOM_STRING":
    #     return "Verification token mismatch", 400

    return jsonify({"hub.challenge": challenge})

# -------------------------------------------------
# 2) RECEIVE WEBHOOK EVENTS (POST endpoint)
# -------------------------------------------------
@app.route("/strava/webhook", methods=["POST"])
def strava_webhook_event():
    """
    When Strava has a new event for your subscription (activity creation, update, etc.),
    it will POST a JSON body to this endpoint. We just print it out for now.
    """
    event_data = request.json
    print("Received Strava event:", event_data)

    # event_data might look like:
    # {
    #   "object_type": "activity",
    #   "object_id": 123456789,
    #   "aspect_type": "create",
    #   "updates": {},
    #   "owner_id": 999999,
    #   "subscription_id": 13579,
    #   "event_time": 1633024800
    # }

    # We'll just return 200 OK so Strava knows we received it.
    return "OK", 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)
    # app.run()
