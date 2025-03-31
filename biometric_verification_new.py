import face_recognition
import cv2
import numpy as np
import os
import base64
from datetime import datetime
import hashlib

class BiometricVerifier:
    def __init__(self):
        self.known_faces_dir = 'data/known_faces'
        os.makedirs(self.known_faces_dir, exist_ok=True)
        self.tolerance = 0.6  # Face recognition tolerance (lower is more strict)

    def verify_face(self, image_data):
        """Main verification method that handles the full workflow"""
        try:
            # Convert and validate image
            image = self._parse_image(image_data)
            if image is None:
                return self._error_response("Invalid image data")

            # Detect and extract face
            face_encoding = self._extract_face_encoding(image)
            if not face_encoding:
                return self._error_response("No face detected")

            # Check against known faces
            match, person_id = self._match_known_faces(face_encoding)
            
            if match:
                return self._success_response(person_id, "Face verified")
            
            # Register new face if no match found
            person_id = self._register_new_face(face_encoding, image)
            return self._success_response(person_id, "New face registered")

        except Exception as e:
            return self._error_response(f"Verification error: {str(e)}")

    def _parse_image(self, image_data):
        """Convert base64 image to OpenCV format"""
        try:
            if isinstance(image_data, str):
                header, encoded = image_data.split(",", 1)
                binary_data = base64.b64decode(encoded)
            else:
                binary_data = image_data
                
            image_array = np.frombuffer(binary_data, dtype=np.uint8)
            return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception:
            return None

    def _extract_face_encoding(self, image):
        """Extract face encodings from image"""
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return None
        return face_recognition.face_encodings(image, face_locations)[0]

    def _match_known_faces(self, face_encoding):
        """Compare against database of known faces"""
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith('.npy'):
                known_enc = np.load(os.path.join(self.known_faces_dir, filename))
                matches = face_recognition.compare_faces(
                    [known_enc], 
                    face_encoding,
                    tolerance=self.tolerance
                )
                if matches[0]:
                    return True, filename.split('.')[0]
        return False, None

    def _register_new_face(self, face_encoding, image):
        """Register a new face in the system"""
        face_id = hashlib.sha256(
            datetime.now().strftime("%Y%m%d%H%M%S%f").encode()
        ).hexdigest()[:16]
        
        # Save encoding
        np.save(os.path.join(self.known_faces_dir, f'{face_id}.npy'), face_encoding)
        
        # Save image for reference
        cv2.imwrite(os.path.join(self.known_faces_dir, f'{face_id}.jpg'), image)
        
        return face_id

    def _success_response(self, verification_id, message):
        return {
            'success': True,
            'verification_id': verification_id,
            'message': message
        }

    def _error_response(self, message):
        return {
            'success': False,
            'message': message
        }

# Example usage:
# verifier = BiometricVerifier()
# result = verifier.verify_face(image_data)