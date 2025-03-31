document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let selectedCandidate = null;
    const verificationId = document.getElementById('verificationIdDisplay').textContent;
    const walletAddress = localStorage.getItem('walletAddress');

    // Load candidates when page loads
    loadCandidates();

    // Candidate selection handler
    window.selectCandidate = function(index) {
        selectedCandidate = index;
        document.querySelectorAll('#candidatesList > div').forEach((div, i) => {
            if (i === index) {
                div.classList.add('border-blue-500', 'bg-blue-50');
                div.querySelector('input').checked = true;
            } else {
                div.classList.remove('border-blue-500', 'bg-blue-50');
                div.querySelector('input').checked = false;
            }
        });
    };

    // Vote button click handler
    document.getElementById('voteButton').addEventListener('click', async function() {
        if (selectedCandidate === null) {
            showStatus('Please select a candidate', 'error');
            return;
        }

        showTransactionModal('Processing Vote', 'Please confirm the transaction in MetaMask...');
        
        try {
            const response = await fetch('/api/vote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    candidate_id: selectedCandidate,
                    verification_id: verificationId,
                    wallet_address: walletAddress
                })
            });

            const result = await response.json();

            if (result.success) {
                // Handle successful vote
                updateTransactionModal('Vote Recorded', 'Your vote has been successfully recorded on the blockchain.', 'success');
                await loadCandidates(); // Refresh candidates list
            } else {
                updateTransactionModal('Voting Failed', result.error || 'Failed to process vote', 'error');
            }
        } catch (error) {
            console.error('Voting error:', error);
            updateTransactionModal('Error', 'An error occurred while processing your vote', 'error');
        }
    });

    // Load candidates from API
    async function loadCandidates() {
        try {
            const response = await fetch('/api/candidates');
            const data = await response.json();

            if (data.success) {
                const candidatesList = document.getElementById('candidatesList');
                candidatesList.innerHTML = data.candidates.map((candidate, index) => `
                    <div class="relative flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 cursor-pointer transition-colors duration-150 ease-in-out"
                         onclick="selectCandidate(${index})">
                        <div class="flex items-center h-5">
                            <input type="radio" name="candidate" value="${index}"
                                class="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300">
                        </div>
                        <div class="ml-3 flex justify-between w-full">
                            <label class="font-medium text-gray-700">
                                ${candidate.name}
                            </label>
                            <span class="text-gray-500">
                                ${candidate.vote_count} votes
                            </span>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading candidates:', error);
            showStatus('Failed to load candidates', 'error');
        }
    }

    // Modal control functions
    function showTransactionModal(title, message) {
        document.getElementById('transactionModal').classList.remove('hidden');
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalMessage').textContent = message;
        document.getElementById('modalButton').classList.add('hidden');
    }

    function updateTransactionModal(title, message, type) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalMessage').textContent = message;
        document.getElementById('modalIcon').className = type === 'success' 
            ? 'fas fa-check text-green-600' 
            : 'fas fa-times text-red-600';
        document.getElementById('modalButton').classList.remove('hidden');
    }

    // Status message display
    function showStatus(message, type) {
        const statusDiv = document.getElementById('votingStatus');
        statusDiv.classList.remove('hidden', 'bg-yellow-50', 'bg-red-50');
        statusDiv.classList.add(type === 'error' ? 'bg-red-50' : 'bg-yellow-50');
        document.getElementById('statusMessage').textContent = message;
    }
});