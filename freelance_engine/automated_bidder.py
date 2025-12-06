"""
Automated Bidder & Proposal Generator - V4 Freelance Engine
Generates compelling proposals and places bids on freelance platforms.
"""

from typing import Dict, List, Optional
from datetime import datetime
import random


class ProposalGenerator:
    """
    Generates human-like, compelling proposals for freelance jobs.
    Uses LLM-style templates and personalization.
    """
    
    def __init__(self, chimera_profile: Optional[Dict] = None):
        """
        Initialize the proposal generator.
        
        Args:
            chimera_profile: Profile information for proposals
        """
        self.profile = chimera_profile or self._default_profile()
        self.proposal_templates = self._load_templates()
        self.past_successes = []
        
    def _default_profile(self) -> Dict:
        """Create default Chimera profile."""
        return {
            "name": "Chimera Development",
            "experience_years": 5,
            "specialties": [
                "Python Development",
                "JavaScript/React",
                "API Integration",
                "Automation Solutions",
                "Bug Fixes & Debugging"
            ],
            "completion_rate": 98,
            "response_time": "within 1 hour",
            "availability": "40+ hours/week"
        }
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load proposal templates for different job types."""
        return {
            "greeting": [
                "Hello! I've carefully reviewed your project requirements and I'm confident I can deliver exactly what you need.",
                "Hi there! Your project caught my attention, and I believe I'm a perfect fit for this work.",
                "Greetings! I'm excited about this opportunity and have extensive experience in this area.",
                "Hello! I've read through your requirements thoroughly and I'm ready to get started immediately."
            ],
            "experience": [
                "With over {years} years of professional experience in {specialty}, I've successfully completed similar projects.",
                "I specialize in {specialty} and have a proven track record of delivering high-quality work.",
                "My expertise in {specialty} makes me uniquely qualified to handle this project efficiently.",
                "I've been working with {specialty} professionally for {years} years with excellent results."
            ],
            "approach": [
                "Here's my approach: I'll start by thoroughly analyzing your requirements, then develop a clear implementation plan, and keep you updated throughout the process.",
                "My methodology involves careful planning, regular communication, and iterative development to ensure the final product exceeds your expectations.",
                "I believe in transparent communication and will provide daily updates on progress, ensuring you're always in the loop.",
                "I'll begin with a detailed requirements analysis, followed by implementation with comprehensive testing to ensure quality."
            ],
            "timeline": [
                "I can complete this project within {hours} hours, delivering high-quality, well-documented code.",
                "Based on the requirements, I estimate {hours} hours for completion, including thorough testing.",
                "I'm available to start immediately and can deliver the completed work in approximately {hours} hours.",
                "The estimated timeline is {hours} hours, though I'm flexible and can adjust based on your schedule."
            ],
            "commitment": [
                "I guarantee clean, efficient code with comprehensive documentation and post-delivery support.",
                "My commitment includes not just delivering working code, but also ensuring you understand the solution fully.",
                "I stand behind my work with ongoing support and will make any necessary adjustments at no extra charge.",
                "You'll receive production-ready code with proper error handling, testing, and detailed documentation."
            ],
            "closing": [
                "I'd love to discuss this project further. Feel free to reach out with any questions!",
                "Looking forward to the opportunity to work with you on this project.",
                "Ready to get started whenever you are. Let's make this project a success!",
                "Excited to bring your vision to life. Please let me know if you'd like to discuss further."
            ]
        }
    
    def generate_proposal(self, job_data: Dict) -> Dict:
        """
        Generate a compelling proposal for a job.
        
        Args:
            job_data: Parsed job data with profitability assessment
            
        Returns:
            Generated proposal dictionary
        """
        # Select relevant specialty based on matched skills
        matched_skills = job_data.get("matched_skills", [])
        if matched_skills:
            primary_skill = matched_skills[0]["skill"].replace("_", " ").title()
        else:
            primary_skill = "Software Development"
        
        # Calculate estimated hours
        estimated_hours = job_data.get("estimated_hours", 10)
        
        # Generate proposal sections
        greeting = random.choice(self.proposal_templates["greeting"])
        
        experience = random.choice(self.proposal_templates["experience"]).format(
            years=self.profile["experience_years"],
            specialty=primary_skill
        )
        
        approach = random.choice(self.proposal_templates["approach"])
        
        timeline = random.choice(self.proposal_templates["timeline"]).format(
            hours=int(estimated_hours)
        )
        
        commitment = random.choice(self.proposal_templates["commitment"])
        
        closing = random.choice(self.proposal_templates["closing"])
        
        # Add relevant past success if available
        past_success_section = ""
        if self.past_successes:
            relevant_success = self._find_relevant_success(matched_skills)
            if relevant_success:
                past_success_section = f"\n\nRecently, I {relevant_success['description']}"
        
        # Combine into full proposal
        full_proposal = f"""{greeting}

{experience}

{approach}

{timeline}
{past_success_section}

{commitment}

{closing}

Best regards,
{self.profile['name']}"""
        
        return {
            "proposal_text": full_proposal,
            "generated_at": datetime.now().isoformat(),
            "word_count": len(full_proposal.split()),
            "tone": "professional",
            "personalization_level": "high"
        }
    
    def _find_relevant_success(self, matched_skills: List[Dict]) -> Optional[Dict]:
        """Find a relevant past success to mention."""
        if not self.past_successes or not matched_skills:
            return None
        
        # Simple matching - in production, use semantic similarity
        skill_keywords = [skill["skill"] for skill in matched_skills]
        
        for success in self.past_successes:
            if any(keyword in success["tags"] for keyword in skill_keywords):
                return success
        
        return None
    
    def add_past_success(self, success: Dict):
        """Add a past success story."""
        self.past_successes.append({
            **success,
            "added_at": datetime.now().isoformat()
        })


class AutomatedBidder:
    """
    Automatically places bids on freelance platforms.
    Calculates optimal bid amounts based on market rates and complexity.
    """
    
    def __init__(self, proposal_generator: ProposalGenerator):
        """
        Initialize the automated bidder.
        
        Args:
            proposal_generator: Instance of ProposalGenerator
        """
        self.proposal_generator = proposal_generator
        self.bid_history: List[Dict] = []
        self.active_bids: List[Dict] = []
        
    def calculate_bid_amount(self, job_data: Dict) -> Dict:
        """
        Calculate optimal bid amount.
        
        Args:
            job_data: Parsed job data
            
        Returns:
            Bid calculation details
        """
        estimated_hours = job_data.get("estimated_hours", 10)
        complexity = job_data.get("complexity", "medium")
        confidence = job_data.get("confidence_score", 0.8)
        budget = job_data.get("budget", {})
        
        # Base rates by complexity
        base_rates = {
            "simple": 60,
            "medium": 75,
            "complex": 90
        }
        
        base_rate = base_rates.get(complexity, 75)
        
        # Adjust rate based on confidence
        # Higher confidence = can charge more
        adjusted_rate = base_rate * (0.8 + (confidence * 0.4))
        
        # Calculate bid amount
        if budget.get("type") == "hourly":
            bid_amount = adjusted_rate
            total_value = bid_amount * estimated_hours
        else:
            # Fixed price project
            total_value = adjusted_rate * estimated_hours
            
            # Check client's budget
            client_budget = budget.get("amount", 0)
            if client_budget > 0:
                # Bid slightly under client budget if it's reasonable
                if total_value > client_budget:
                    total_value = client_budget * 0.95
            
            bid_amount = total_value
        
        return {
            "bid_amount": round(bid_amount, 2),
            "total_value": round(total_value, 2),
            "hourly_rate": round(adjusted_rate, 2),
            "estimated_hours": estimated_hours,
            "budget_type": budget.get("type", "fixed"),
            "calculation_method": "confidence_adjusted"
        }
    
    def create_bid(self, job_data: Dict) -> Dict:
        """
        Create a complete bid package (proposal + bid amount).
        
        Args:
            job_data: Parsed job data
            
        Returns:
            Complete bid package
        """
        # Generate proposal
        proposal = self.proposal_generator.generate_proposal(job_data)
        
        # Calculate bid amount
        bid_calculation = self.calculate_bid_amount(job_data)
        
        # Create bid package
        bid = {
            "job_id": job_data.get("job_id"),
            "job_title": job_data.get("title"),
            "platform": job_data.get("platform"),
            "proposal": proposal["proposal_text"],
            "bid_amount": bid_calculation["bid_amount"],
            "total_value": bid_calculation["total_value"],
            "hourly_rate": bid_calculation["hourly_rate"],
            "estimated_hours": bid_calculation["estimated_hours"],
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        return bid
    
    def submit_bid(self, bid: Dict, auto_submit: bool = False) -> Dict:
        """
        Submit a bid to the platform.
        
        Args:
            bid: Bid package to submit
            auto_submit: If True, submit immediately; if False, queue for review
            
        Returns:
            Submission result
        """
        if auto_submit:
            # In production, this would call the platform API
            bid["status"] = "submitted"
            bid["submitted_at"] = datetime.now().isoformat()
            
            self.active_bids.append(bid)
            self.bid_history.append(bid)
            
            print(f"✓ Bid submitted for: {bid['job_title']}")
            print(f"  Amount: ${bid['bid_amount']}")
            print(f"  Platform: {bid['platform']}")
            
            return {
                "success": True,
                "bid_id": f"bid_{len(self.bid_history)}",
                "message": "Bid submitted successfully"
            }
        else:
            # Queue for manual review
            bid["status"] = "pending_review"
            self.bid_history.append(bid)
            
            print(f"✓ Bid queued for review: {bid['job_title']}")
            
            return {
                "success": True,
                "bid_id": f"bid_{len(self.bid_history)}",
                "message": "Bid queued for review"
            }
    
    def process_bid_result(self, bid_id: str, result: str):
        """
        Process the result of a bid (accepted/rejected).
        
        Args:
            bid_id: Bid identifier
            result: "accepted" or "rejected"
        """
        # Find the bid
        for bid in self.active_bids:
            if bid.get("bid_id") == bid_id or bid.get("job_id") == bid_id:
                bid["status"] = result
                bid["result_at"] = datetime.now().isoformat()
                
                if result == "accepted":
                    print(f"🎉 Bid accepted: {bid['job_title']}")
                    # Trigger Internal Coding Agent
                    return {
                        "action": "start_coding",
                        "bid": bid
                    }
                else:
                    print(f"✗ Bid rejected: {bid['job_title']}")
                
                return {"action": "logged"}
        
        return {"action": "not_found"}
    
    def get_active_bids(self) -> List[Dict]:
        """Get all active bids."""
        return [bid for bid in self.active_bids if bid["status"] == "submitted"]
    
    def get_bid_statistics(self) -> Dict:
        """Get bidding statistics."""
        total_bids = len(self.bid_history)
        accepted = sum(1 for bid in self.bid_history if bid.get("status") == "accepted")
        rejected = sum(1 for bid in self.bid_history if bid.get("status") == "rejected")
        pending = sum(1 for bid in self.active_bids if bid.get("status") == "submitted")
        
        total_value = sum(bid.get("total_value", 0) for bid in self.bid_history)
        
        return {
            "total_bids": total_bids,
            "accepted": accepted,
            "rejected": rejected,
            "pending": pending,
            "win_rate": (accepted / total_bids * 100) if total_bids > 0 else 0,
            "total_potential_value": total_value,
            "average_bid": total_value / total_bids if total_bids > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }


def create_bidding_system(profile: Optional[Dict] = None) -> tuple:
    """
    Factory function to create the bidding system.
    
    Args:
        profile: Optional Chimera profile
        
    Returns:
        Tuple of (ProposalGenerator, AutomatedBidder)
    """
    generator = ProposalGenerator(profile)
    bidder = AutomatedBidder(generator)
    return generator, bidder
