const express = require('express');
const multer = require('multer');
const controller = require('../controllers/controller');
const router = express.Router();
const upload = multer();

router.post('/extract-pose', upload.single('image'), controller.extractPose);
router.get('/keypoints/:id', controller.getKeypoints);
router.put('/keypoints/:id', controller.updateKeypoints);
router.delete('/keypoints/:id', controller.deleteKeypoints);
router.get('/images/:id', controller.getImage);

module.exports = router;