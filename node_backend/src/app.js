require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const { Pool } = require('pg');
const routes = require('./routes');
const cron = require('./utils/cron');

const app = express();
app.use(express.json());
app.use('/api', routes);

const pool = new Pool({ connectionString: process.env.PG_URI });
mongoose.connect(process.env.MONGO_URI);

app.locals.pg = pool;

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Node.js backend running on port ${PORT}`);
  cron(app); // Start cron job
});