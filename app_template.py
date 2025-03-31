from flask import Flask, render_template, request, jsonify, redirect, url_for
from biometric_verification import verify_biometric
import os
from functools import wraps

app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-123'),
    DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///votes.db'),
    CONTRACT_ADDRESS=os.environ.get('CONTRACT_ADDRESS')
)

# Mock authentication decorator (replace with real auth)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add your authentication logic here
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/vote')
@login_required
def vote():
    verification_id = request.args.get('vid', '')
    if not verification_id:
        return redirect(url_for('verify'))
    return render_template('vote.html', verification_id=verification_id)

@app.route('/verify')
def verify():
    return render_template('verify.html')

# API Endpoints
@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    # Replace with database query
    candidates = [
        {'id': 1, 'name': 'Candidate A', 'vote_count': 0},
        {'id': 2, 'name': 'Candidate B', 'vote_count': 0},
        {'id': 3, 'name': 'Candidate C', 'vote_count': 0}
    ]
    return jsonify({'success': True, 'candidates': candidates})

@app.route('/api/verify_biometric', methods=['POST'])
def handle_verification():
    try:
        image_data = request.json.get('image')
        result = verify_biometric(image_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/vote', methods=['POST'])
@login_required
def submit_vote():
    try:
        data = request.json
        # Add voting logic here
        return jsonify({
            'success': True,
            'transaction': {
                'to': app.config['CONTRACT_ADDRESS'],
                'data': '0x...'  # Generated transaction data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)