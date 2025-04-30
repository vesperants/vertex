require('dotenv').config();
const express = require('express');
const { GoogleAuth } = require('google-auth-library');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const GOOGLE_PROJECT = process.env.GOOGLE_PROJECT;
const LOCATION = process.env.LOCATION;
const DATASTORE_ID = process.env.DATASTORE_ID;

const ENDPOINT = `https://${LOCATION}-discoveryengine.googleapis.com/v1/projects/${GOOGLE_PROJECT}/locations/${LOCATION}/dataStores/${DATASTORE_ID}/servingConfigs/default_config:search`;

app.post('/search', async (req, res) => {
  const { query, pageToken } = req.body;

  // Log request input and configuration
  console.log('\n==== INCOMING SEARCH REQUEST ====');
  console.log('Timestamp:', new Date().toISOString());
  console.log('Query:', query);
  console.log('Project:', GOOGLE_PROJECT);
  console.log('Location:', LOCATION);
  console.log('DataStore:', DATASTORE_ID);
  console.log('Endpoint:', ENDPOINT);

  const auth = new GoogleAuth({
    scopes: 'https://www.googleapis.com/auth/cloud-platform',
  });

  try {
    const client = await auth.getClient();
    console.log('Getting Google Cloud access token...');
    const tokenObj = await client.getAccessToken();
    const token = tokenObj.token || tokenObj;
    console.log('Access Token received:', token ? '[REDACTED]' : 'No token');

    const requestBody = {
      query,
      pageSize: 10,
      ...(pageToken ? { pageToken } : {}),
    };

    console.log('Request body:', JSON.stringify(requestBody, null, 2));
    // Make API call
    const response = await axios.post(
      ENDPOINT,
      requestBody,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    // Log response status and data
    console.log('--- VERTEX AI SEARCH RESPONSE ---');
    console.log('Status:', response.status);
    console.dir(response.data, { depth: null, colors: true });
    res.status(200).json(response.data);
  } catch (err) {
    // Log error explicitly
    console.error('--- ERROR FROM GOOGLE API ---');
    if (err.response) {
      console.error('Response status:', err.response.status);
      console.error('Response headers:', JSON.stringify(err.response.headers, null, 2));
      console.error('Response data:', JSON.stringify(err.response.data, null, 2));
      res.status(500).json({
        error: err.response.data?.error?.message || err.message || String(err),
        googleError: err.response.data,
      });
    } else {
      console.error(err);
      res.status(500).json({ error: err.message, raw: String(err) });
    }
  }
});

// Log server startup, env, and settings
app.listen(4000, () => {
  console.log('\n==== Vertex AI Search Proxy API STARTED ====');
  console.log('Timestamp:', new Date().toISOString());
  console.log('Listening on port: 4000');
  console.log('Project:', GOOGLE_PROJECT);
  console.log('Location:', LOCATION);
  console.log('DataStore ID:', DATASTORE_ID);
  console.log('Endpoint:', ENDPOINT);
});