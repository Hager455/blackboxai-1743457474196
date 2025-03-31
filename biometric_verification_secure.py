import face_recognition
import cv2
import numpy as np
import os
import base64
from datetime import datetime
import hashlib

class SecureBiometricVerifier:
    def __init__(self):
        self.known_faces_dir = 'data/known_faces'
        os.makedirs(self.known_faces_dir, exist_ok=True)
        self.tolerance = 0.5  # Stricter tolerance for security
        self.min_face_size = 100  # Minimum face size in pixels
        self.required_blinks = 2  # For liveness detection
        from database import Database
        self.db = Database()

    def verify_face(self, image_data, is_live_check=False):
        """Enhanced verification with anti-spoofing measures"""
        try:
            image = self._parse_image(image_data)
            if image is None:
                return self._error_response("Invalid image data")

            # 1. Basic face detection
            face_locations = face_recognition.face_locations(image)
            if not face_locations:
                return self._error_response("No face detected")

            # 2. Face quality check
            if not self._check_face_quality(image, face_locations[0]):
                return self._error_response("Face quality too low")

            # 3. Liveness detection (if enabled)
            if is_live_check and not self._check_liveness(image):
                return self._error_response("Liveness check failed")

            # 4. Face recognition
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            match, person_id = self._match_known_faces(face_encoding)
            
            if match:
                return self._success_response(person_id, "Verified")
            
            # Register new face if needed
            person_id = self._register_new_face(face_encoding, image)
            return self._success_response(person_id, "New face registered")

        except Exception as e:
            return self._error_response(f"Verification error: {str(e)}")

    def _check_face_quality(self, image, face_location):
        """Ensure face meets quality requirements"""
        top, right, bottom, left = face_location
        face_height = bottom - top
        face_width = right - left
        
        # Check minimum size
        if face_height < self.min_face_size or face_width < self.min_face_size:
            return False
            
        # Check image focus (simplified)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        return fm > 100  # Focus threshold

    def _check_liveness(self, image):
        """Basic liveness detection (simplified example)"""
        # In a real implementation, this would use multiple frames
        # and more sophisticated analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        detected_eyes = eyes.detectMultiScale(gray, 1.1, 4)
        return len(detected_eyes) >= 2  # At least 2 eyes detected

    # [Previous helper methods (_parse_image, _match_known_faces, 
    # _register_new_face, _success_response, _error_response) would be here]

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

    def _register_new_face(self, face_encoding, image, wallet_address=None):
        """Register a new face in the system with database tracking"""
        face_id = hashlib.sha256(
            datetime.now().strftime("%Y%m%d%H%M%S%f").encode()
        ).hexdigest()[:16]
        
        # Save files
        encoding_path = os.path.join(self.known_faces_dir, f'{face_id}.npy')
        image_path = os.path.join(self.known_faces_dir, f'{face_id}.jpg')
        np.save(encoding_path, face_encoding)
        cv2.imwrite(image_path, image)
        
        # Store in database
        self.db.create_verification(
            verification_id=face_id,
            encoding_path=encoding_path,
            image_path=image_path,
            wallet=wallet_address
        )
        
        return face_id

    def verify_face(self, image_data, is_live_check=False, wallet_address=None):
        """Enhanced verification with wallet association"""
        result = super().verify_face(image_data, is_live_check)
        if result['success'] and wallet_address:
            # Update wallet address if verification was successful
            session = self.db.Session()
            try:
                record = session.query(VerificationRecord)\
                    .filter_by(verification_id=result['verification_id'])\
                    .first()
                if record:
                    record.wallet_address = wallet_address
                    session.commit()
            except Exception as e:
                session.rollback()
                print(f"Database error: {str(e)}")
            finally:
                session.close()
        return result

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