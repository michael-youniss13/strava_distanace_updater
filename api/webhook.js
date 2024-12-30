const axios = require('axios');

// Export the serverless function handler
module.exports = async (req, res) => {
  const { method, query, body } = req;

  if (method === 'GET') {
    // Handle verification
    const hubMode = query['hub.mode'];
    const verifyToken = query['hub.verify_token'];
    const challenge = query['hub.challenge'];

    if (hubMode === 'subscribe' && verifyToken === process.env.VERIFY_TOKEN) {
      // Respond with the challenge to verify the webhook
      print("challenge:")
      print(challenge)
      res.status(200).json({ 'hub.challenge': challenge });
    } else {
      res.status(403).send('Forbidden');
    }
  } else if (method === 'POST') {
    // Handle webhook event
    try {
      const eventData = body;
      console.log('Received Strava event:', eventData);

      // Example: Filter for specific activities or athletes
      const TARGET_ATHLETE_ID = process.env.TARGET_ATHLETE_ID; // Optional
      const TARGET_ACTIVITY_TYPE = 'Run'; // Example: Run, Ride, Swim

      if (
        eventData.owner_id === parseInt(TARGET_ATHLETE_ID) &&
        eventData.object_type === 'activity' &&
        eventData.aspect_type === 'create'
      ) {
        const activityId = eventData.object_id;

        // Optional: Fetch activity details from Strava API
        if (process.env.ACCESS_TOKEN) {
          const activityDetails = await fetchActivityDetails(activityId);
          console.log('Activity Details:', activityDetails);

          // Add your processing logic here (e.g., store in database, send notifications)
        }
      }

      // Respond to Strava
      res.status(200).send('OK');
    } catch (error) {
      console.error('Error processing webhook:', error);
      res.status(400).send('Bad Request');
    }
  } else {
    // Method not allowed
    res.setHeader('Allow', ['GET', 'POST']);
    res.status(405).send('Method Not Allowed');
  }
};

// Optional: Function to fetch activity details from Strava API
const fetchActivityDetails = async (activityId) => {
  try {
    const response = await axios.get(
      `https://www.strava.com/api/v3/activities/${activityId}`,
      {
        headers: {
          Authorization: `Bearer ${process.env.ACCESS_TOKEN}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error('Error fetching activity details:', error);
    return null;
  }
};