const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const Image = require('../models/Image');

exports.extractPose = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'No image uploaded' });
    const image_id = uuidv4();

    // Store image in MongoDB
    const imgDoc = new Image({
      image_id,
      data: req.file.buffer,
      contentType: req.file.mimetype
    });
    await imgDoc.save();

    // Send image to Python API
    const base64Image = req.file.buffer.toString('base64');
    const response = await axios.post(
      process.env.PYTHON_API_URL,
      { base64_image: `data:${req.file.mimetype};base64,${base64Image}` },
      { headers: { 'Content-Type': 'application/json' } }
    );
    const keypoints = response.data;

    // Store keypoints in PostgreSQL
    const pool = req.app.locals.pg;
    await pool.query(
      'INSERT INTO keypoints (image_id, keypoints) VALUES ($1, $2)',
      [image_id, keypoints]
    );

    res.json({ image_id, keypoints });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getKeypoints = async (req, res) => {
  try {
    const pool = req.app.locals.pg;
    const { rows } = await pool.query(
      'SELECT * FROM keypoints WHERE image_id = $1',
      [req.params.id]
    );
    if (!rows.length) return res.status(404).json({ error: 'Not found' });
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.updateKeypoints = async (req, res) => {
  try {
    const pool = req.app.locals.pg;
    await pool.query(
      'UPDATE keypoints SET keypoints = $1 WHERE image_id = $2',
      [req.body.keypoints, req.params.id]
    );
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.deleteKeypoints = async (req, res) => {
  try {
    const pool = req.app.locals.pg;
    await pool.query('DELETE FROM keypoints WHERE image_id = $1', [req.params.id]);
    await Image.deleteOne({ image_id: req.params.id });
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getImage = async (req, res) => {
  try {
    const img = await Image.findOne({ image_id: req.params.id });
    if (!img) return res.status(404).json({ error: 'Not found' });
    res.set('Content-Type', img.contentType);
    res.send(img.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};