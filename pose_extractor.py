# pose_extractor.py
import cv2
import mediapipe as mp
import numpy as np
import json
import base64
from flask import Flask, request, jsonify
import os
from datetime import datetime
import argparse
from typing import Dict, List, Optional, Tuple

class PoseExtractor:
    """MediaPipe Pose keypoint extraction class"""
    
    def __init__(self):
        """Initialize MediaPipe Pose"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def extract_keypoints(self, image_path: str) -> Dict:
        """
        Extract pose keypoints from image
        
        Args:
            image_path: Path to input image
            
        Returns:
            Dictionary containing keypoints data and metadata
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.pose.process(image_rgb)
            
            # Extract keypoints
            keypoints_data = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "image_info": {
                    "width": image.shape[1],
                    "height": image.shape[0],
                    "channels": image.shape[2]
                },
                "keypoints": [],
                "pose_detected": results.pose_landmarks is not None
            }
            
            if results.pose_landmarks:
                # Extract 33 pose landmarks
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    keypoint = {
                        "id": idx,
                        "name": self._get_keypoint_name(idx),
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    }
                    keypoints_data["keypoints"].append(keypoint)
            
            return keypoints_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def extract_keypoints_from_base64(self, base64_image: str) -> Dict:
        """
        Extract keypoints from base64 encoded image
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            Dictionary containing keypoints data
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image.split(',')[1] if ',' in base64_image else base64_image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode base64 image")
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.pose.process(image_rgb)
            
            # Extract keypoints (same logic as above)
            keypoints_data = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "image_info": {
                    "width": image.shape[1],
                    "height": image.shape[0],
                    "channels": image.shape[2]
                },
                "keypoints": [],
                "pose_detected": results.pose_landmarks is not None
            }
            
            if results.pose_landmarks:
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    keypoint = {
                        "id": idx,
                        "name": self._get_keypoint_name(idx),
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    }
                    keypoints_data["keypoints"].append(keypoint)
            
            return keypoints_data
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def visualize_pose(self, image_path: str, output_path: str = None) -> str:
        """
        Create visualization of detected pose
        
        Args:
            image_path: Path to input image
            output_path: Path to save visualization (optional)
            
        Returns:
            Path to saved visualization
        """
        try:
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            results = self.pose.process(image_rgb)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )
            
            # Save visualization
            if not output_path:
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = f"pose_visualization_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            cv2.imwrite(output_path, image)
            return output_path
            
        except Exception as e:
            raise Exception(f"Visualization failed: {str(e)}")
    
    def _get_keypoint_name(self, idx: int) -> str:
        """Get keypoint name by index"""
        keypoint_names = [
            "NOSE", "LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
            "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER",
            "LEFT_EAR", "RIGHT_EAR", "MOUTH_LEFT", "MOUTH_RIGHT",
            "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "RIGHT_ELBOW",
            "LEFT_WRIST", "RIGHT_WRIST", "LEFT_PINKY", "RIGHT_PINKY",
            "LEFT_INDEX", "RIGHT_INDEX", "LEFT_THUMB", "RIGHT_THUMB",
            "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
            "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_HEEL", "RIGHT_HEEL",
            "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
        ]
        return keypoint_names[idx] if idx < len(keypoint_names) else f"UNKNOWN_{idx}"

# Flask API Application
app = Flask(__name__)
pose_extractor = PoseExtractor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MediaPipe Pose Extractor",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/extract-pose', methods=['POST'])
def extract_pose_api():
    """
    API endpoint to extract pose keypoints
    Accepts either file upload or base64 image
    """
    try:
        if 'image' in request.files:
            # Handle file upload
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Save uploaded file temporarily
            temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file.save(temp_path)
            
            # Extract keypoints
            result = pose_extractor.extract_keypoints(temp_path)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return jsonify(result)
            
        elif 'base64_image' in request.json:
            # Handle base64 image
            base64_image = request.json['base64_image']
            result = pose_extractor.extract_keypoints_from_base64(base64_image)
            return jsonify(result)
            
        else:
            return jsonify({"error": "No image provided. Use 'image' file or 'base64_image' in JSON"}), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/visualize-pose', methods=['POST'])
def visualize_pose_api():
    """
    API endpoint to create pose visualization
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save uploaded file temporarily
        temp_input = f"temp_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file.save(temp_input)
        
        # Create visualization
        output_path = pose_extractor.visualize_pose(temp_input)
        
        # Read visualization as base64
        with open(output_path, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Clean up temp files
        os.remove(temp_input)
        os.remove(output_path)
        
        return jsonify({
            "success": True,
            "visualization": f"data:image/jpeg;base64,{img_base64}",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/batch-extract', methods=['POST'])
def batch_extract_api():
    """
    API endpoint for batch processing multiple images
    """
    try:
        if 'images' not in request.files:
            return jsonify({"error": "No images provided"}), 400
        
        files = request.files.getlist('images')
        results = []
        
        for file in files:
            if file.filename == '':
                continue
            
            # Save file temporarily
            temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file.save(temp_path)
            
            # Extract keypoints
            result = pose_extractor.extract_keypoints(temp_path)
            result['filename'] = file.filename
            results.append(result)
            
            # Clean up
            os.remove(temp_path)
        
        return jsonify({
            "success": True,
            "total_processed": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Command Line Interface
def main():
    """Command line interface for pose extraction"""
    parser = argparse.ArgumentParser(description='MediaPipe Pose Keypoint Extraction')
    parser.add_argument('--mode', choices=['api', 'cli'], default='api', 
                       help='Run mode: api server or command line')
    parser.add_argument('--image', type=str, help='Path to input image (CLI mode)')
    parser.add_argument('--output', type=str, help='Output JSON file path (CLI mode)')
    parser.add_argument('--visualize', action='store_true', help='Create pose visualization')
    parser.add_argument('--port', type=int, default=5000, help='API server port')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='API server host')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        print(f"Starting MediaPipe Pose API server on {args.host}:{args.port}")
        print("Endpoints:")
        print("  GET  /health - Health check")
        print("  POST /extract-pose - Extract keypoints from image")
        print("  POST /visualize-pose - Create pose visualization")
        print("  POST /batch-extract - Batch process multiple images")
        app.run(host=args.host, port=args.port, debug=False)
        
    elif args.mode == 'cli':
        if not args.image:
            print("Error: --image is required for CLI mode")
            return
        
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}")
            return
        
        print(f"Processing image: {args.image}")
        extractor = PoseExtractor()
        result = extractor.extract_keypoints(args.image)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(json.dumps(result, indent=2))
        
        if args.visualize:
            viz_path = extractor.visualize_pose(args.image)
            print(f"Visualization saved to: {viz_path}")

if __name__ == '__main__':
    main()