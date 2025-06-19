const mongoose = require('mongoose');
const ImageSchema = new mongoose.Schema({
  image_id: { type: String, required: true, unique: true },
  data: { type: Buffer, required: true },
  contentType: { type: String, required: true },
  created_at: { type: Date, default: Date.now }
});
module.exports = mongoose.model('Image', ImageSchema);