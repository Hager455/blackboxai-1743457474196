import cv2
import numpy as np
from mtcnn import MTCNN
from facenet_pytorch import InceptionResnetV1
import mediapipe as mp
import torch

class BiometricVerifier:
    def __init__(self):
        # Initialize models
        self.face_detector = MTCNN()
        self.face_recognizer = InceptionResnetV1(pretrained='vggface2').eval()
        self.iris_detector = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
    def preprocess_face(self, image):
        """Normalize and resize face image"""
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (160, 160))
        return (image - 127.5) / 128.0

    def detect_face(self, frame):
        """Step 2: Face detection with MTCNN"""
        try:
            faces = self.face_detector.detect_faces(frame)
            if not faces:
                raise ValueError("No face detected")
            x, y, w, h = faces[0]['box']
            return frame[y:y+h, x:x+w]
        except Exception as e:
            print(f"Face detection error: {str(e)}")
            return None

    def recognize_face(self, face_img):
        """Step 3: Face recognition with FaceNet"""
        try:
            face_tensor = torch.tensor(self.preprocess_face(face_img)).permute(2,0,1).float()
            embedding = self.face_recognizer(face_tensor.unsqueeze(0))
            return embedding.detach().numpy()
        except Exception as e:
            print(f"Face recognition error: {str(e)}")
            return None

    def detect_iris(self, frame):
        """Step 4: Iris detection with MediaPipe"""
        try:
            results = self.iris_detector.process(frame)
            if not results.multi_face_landmarks:
                raise ValueError("No iris detected")
            return results.multi_face_landmarks[0]
        except Exception as e:
            print(f"Iris detection error: {str(e)}")
            return None

    def verify_biometrics(self, frame):
        """Complete verification pipeline"""
        # Face detection
        face = self.detect_face(frame)
        if face is None:
            return False, "Face detection failed"
        
        # Face recognition
        embedding = self.recognize_face(face)
        if embedding is None:
            return False, "Face recognition failed"
        
        # Iris detection
        iris = self.detect_iris(frame)
        if iris is None:
            return False, "Iris detection failed"
        
        return True, "Verification successful"

# Example usage
if __name__ == "__main__":
    verifier = BiometricVerifier()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        success, message = verifier.verify_biometrics(frame)
        print(f"Verification: {success} - {message}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()