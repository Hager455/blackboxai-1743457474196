document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('cameraFeed');
    const startBtn = document.getElementById('startCamera');
    const captureBtn = document.getElementById('captureButton');
    const statusDiv = document.getElementById('verificationStatus');
    const successDiv = document.getElementById('verificationSuccess');
    let stream = null;

    // Start camera
    startBtn.addEventListener('click', async function() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: 1280, 
                    height: 720,
                    facingMode: 'user'
                } 
            });
            video.srcObject = stream;
            captureBtn.disabled = false;
            updateStatus('Camera ready for verification', 'success');
        } catch (err) {
            updateStatus(`Error: ${err.message}`, 'error');
        }
    });

    // Capture and verify
    captureBtn.addEventListener('click', async function() {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            updateStatus('Processing verification...', 'info');
            
            const response = await fetch('/api/verify_biometric', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: canvas.toDataURL('image/jpeg', 0.8)
                })
            });

            const result = await response.json();
            
            if (result.success) {
                handleVerificationSuccess(result.verification_id);
            } else {
                throw new Error(result.message || 'Verification failed');
            }
        } catch (err) {
            updateStatus(`Error: ${err.message}`, 'error');
        }
    });

    function handleVerificationSuccess(verificationId) {
        successDiv.classList.remove('hidden');
        const link = successDiv.querySelector('a');
        link.href = `/vote?vid=${verificationId}`;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        captureBtn.disabled = true;
    }

    function updateStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `mt-4 text-sm ${
            type === 'error' ? 'text-red-600' : 
            type === 'success' ? 'text-green-600' : 'text-blue-600'
        }`;
    }

    // Clean up camera on page leave
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
});