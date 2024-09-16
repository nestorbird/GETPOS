// server.js
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();

app.use(cors({ origin: 'http://localhost:3000' }));
app.use(bodyParser.json());

app.post('/api/authenticate', async (req, res) => {
  const { client_id, client_secret, auth_token_url } = req.body;

  const params = new URLSearchParams();
  params.append('grant_type', 'client_credentials');
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('scope', 'urn:viva:payments:core:api');

  try {
    const response = await axios.post(`${auth_token_url}/connect/token`, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error obtaining access token:', error);
    res.status(500).json({ error: 'Failed to obtain access token' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
