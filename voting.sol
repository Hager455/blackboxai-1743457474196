// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    // Structure for Voter
    struct Voter {
        bool isRegistered;
        bool hasVoted;
        uint256 votedFor;
        bytes32 biometricHash;
    }
    
    // Structure for Candidate
    struct Candidate {
        string name;
        uint256 voteCount;
    }
    
    address public admin;
    mapping(address => Voter) public voters;
    Candidate[] public candidates;
    
    // Events
    event VoterRegistered(address indexed voter);
    event VoteCast(address indexed voter, uint256 indexed candidateId);
    event CandidateAdded(uint256 indexed candidateId, string name);
    
    constructor() {
        admin = msg.sender;
    }
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    // Register a voter with their biometric hash
    function registerVoter(address _voter, bytes32 _biometricHash) public onlyAdmin {
        require(!voters[_voter].isRegistered, "Voter already registered");
        
        voters[_voter].isRegistered = true;
        voters[_voter].biometricHash = _biometricHash;
        
        emit VoterRegistered(_voter);
    }
    
    // Add a new candidate
    function addCandidate(string memory _name) public onlyAdmin {
        candidates.push(Candidate({
            name: _name,
            voteCount: 0
        }));
        
        emit CandidateAdded(candidates.length - 1, _name);
    }
    
    // Cast a vote
    function castVote(uint256 _candidateId) public {
        Voter storage sender = voters[msg.sender];
        
        require(sender.isRegistered, "Voter is not registered");
        require(!sender.hasVoted, "Voter has already voted");
        require(_candidateId < candidates.length, "Invalid candidate ID");
        
        sender.hasVoted = true;
        sender.votedFor = _candidateId;
        
        candidates[_candidateId].voteCount++;
        
        emit VoteCast(msg.sender, _candidateId);
    }
    
    // Get number of candidates
    function getCandidateCount() public view returns (uint256) {
        return candidates.length;
    }
    
    // Get candidate details
    function getCandidate(uint256 _candidateId) public view returns (string memory name, uint256 voteCount) {
        require(_candidateId < candidates.length, "Invalid candidate ID");
        Candidate memory candidate = candidates[_candidateId];
        return (candidate.name, candidate.voteCount);
    }
}
