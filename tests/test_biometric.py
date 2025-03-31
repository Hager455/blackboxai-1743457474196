import pytest
from biometric_verification import verify_biometric
import cv2
import os

@pytest.fixture
def sample_image():
    img = cv2.imread('tests/sample_face.jpg')
    yield img
    del img

def test_biometric_verification(sample_image):
    # Test with known good image
    result = verify_biometric(sample_image)
    assert result['success'] == True
    assert 'verification_id' in result
    
    # Test with empty image
    empty_img = cv2.imread('tests/empty.jpg')
    result = verify_biometric(empty_img)
    assert result['success'] == False
    assert 'No face detected' in result['message']