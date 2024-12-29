## Steps taken:
1) Set up ngrok account (https://dashboard.ngrok.com/observability/traffic-inspector)
2) added app.py and secrets.txt
3) added a folder to postman
4) created Strava api, registered webhook, checked that the webhook endpoint was working
    - Might need to update the urls by re-registering with updated tokens from the strava portal

5) [in progress] adding OAuth tokens

## Current MIT
- new activities aren't triggering the webhook

## To run app
1) `ngrok http 5000`
2) `python app.py` (in a separate tab)

