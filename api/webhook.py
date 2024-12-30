from fastapi import FastAPI, Request, HTTPException
import os
import json

app = FastAPI()

@app.get("/strava/webhook")
async def verify(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and verify_token == os.environ.get("VERIFY_TOKEN"):
        return {"hub.challenge": challenge}
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/strava/webhook")
async def webhook(request: Request):
    try:
        event_data = await request.json()
        print("Received Strava event:", event_data)
        # Add your processing logic here
        return {"message": "OK"}
    except Exception as e:
        print("Error processing webhook:", e)
        raise HTTPException(status_code=400, detail="Bad Request")
