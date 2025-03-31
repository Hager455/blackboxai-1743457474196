from web3 import Web3
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class VotingContract:
    def __init__(self):
        """
        Initialize Web3 connection and contract instance
        """
        try:
            # Connect to blockchain network
            self.w3 = Web3(Web3.HTTPProvider(Config.BLOCKCHAIN_URL))
            
            # Load contract ABI
            with open('contract_abi.json', 'r') as f:
                contract_abi = json.load(f)
            
            # Create contract instance
            self.contract = self.w3.eth.contract(
                address=Config.CONTRACT_ADDRESS,
                abi=contract_abi
            )
            
            logger.info("Successfully initialized Web3 connection and contract")
            
        except Exception as e:
            logger.error(f"Error initializing VotingContract: {str(e)}")
            raise

    def cast_vote(self, voter_address: str, candidate_id: int) -> dict:
        """
        Cast a vote for a candidate using the smart contract
        """
        try:
            # Verify voter address format
            if not self.w3.is_address(voter_address):
                return {
                    'success': False,
                    'error': 'Invalid voter address format'
                }

            # Build transaction
            transaction = self.contract.functions.castVote(candidate_id).build_transaction({
                'from': voter_address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(voter_address)
            })

            # Note: The actual transaction signing and sending should be done by the client
            # using MetaMask, as we don't want to handle private keys on the server
            return {
                'success': True,
                'transaction': transaction
            }

        except Exception as e:
            logger.error(f"Error casting vote: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_candidates(self) -> dict:
        """
        Get list of all candidates
        """
        try:
            candidate_count = self.contract.functions.getCandidateCount().call()
            candidates = []
            
            for i in range(candidate_count):
                name, vote_count = self.contract.functions.getCandidate(i).call()
                candidates.append({
                    'id': i,
                    'name': name,
                    'vote_count': vote_count
                })
            
            return {
                'success': True,
                'candidates': candidates
            }
            
        except Exception as e:
            logger.error(f"Error getting candidates: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def verify_voter(self, voter_address: str) -> dict:
        """
        Verify if a voter is registered and hasn't voted
        """
        try:
            voter = self.contract.functions.voters(voter_address).call()
            
            return {
                'success': True,
                'is_registered': voter[0],  # isRegistered
                'has_voted': voter[1]       # hasVoted
            }
            
        except Exception as e:
            logger.error(f"Error verifying voter: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_vote_count(self, candidate_id: int) -> dict:
        """
        Get vote count for a specific candidate
        """
        try:
            name, vote_count = self.contract.functions.getCandidate(candidate_id).call()
            
            return {
                'success': True,
                'candidate_name': name,
                'vote_count': vote_count
            }
            
        except Exception as e:
            logger.error(f"Error getting vote count: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def register_voter(self, admin_address: str, voter_address: str, biometric_hash: str) -> dict:
        """
        Register a new voter (admin only)
        """
        try:
            # Verify addresses format
            if not (self.w3.is_address(admin_address) and self.w3.is_address(voter_address)):
                return {
                    'success': False,
                    'error': 'Invalid address format'
                }

            # Build transaction
            transaction = self.contract.functions.registerVoter(
                voter_address,
                self.w3.to_bytes(hexstr=biometric_hash)
            ).build_transaction({
                'from': admin_address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(admin_address)
            })

            return {
                'success': True,
                'transaction': transaction
            }

        except Exception as e:
            logger.error(f"Error registering voter: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
