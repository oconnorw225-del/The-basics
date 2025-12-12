"""
Job Prospector Module - V4 Freelance Engine
Monitors freelance platforms and identifies promising job opportunities.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class JobPlatform(Enum):
    """Supported freelance platforms."""
    UPWORK = "upwork"
    FREELANCER = "freelancer"
    FIVERR = "fiverr"
    TOPTAL = "toptal"
    GITHUB_JOBS = "github_jobs"


class SkillCategory(Enum):
    """Skill categories Chimera can handle."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    REACT = "react"
    NODE = "node"
    API_INTEGRATION = "api_integration"
    BUG_FIX = "bug_fix"
    AUTOMATION = "automation"
    DATA_PROCESSING = "data_processing"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DATABASE = "database"
    MACHINE_LEARNING = "machine_learning"
    WEB_SCRAPING = "web_scraping"


class JobProspector:
    """
    Monitors freelance platforms and identifies promising opportunities.
    Uses NLP to parse job descriptions and match against capability matrix.
    """
    
    def __init__(self, profitability_threshold: float = 100.0):
        """
        Initialize the Job Prospector.
        
        Args:
            profitability_threshold: Minimum acceptable job value in USD
        """
        self.profitability_threshold = profitability_threshold
        self.capability_matrix = self._initialize_capability_matrix()
        self.job_queue: List[Dict] = []
        self.monitored_platforms: Set[JobPlatform] = set()
        
    def _initialize_capability_matrix(self) -> Dict[SkillCategory, Dict]:
        """
        Initialize Chimera's capability matrix.
        Defines what the system can do and confidence levels.
        """
        return {
            SkillCategory.PYTHON: {
                "confidence": 0.95,
                "keywords": ["python", "django", "flask", "fastapi", "pandas", "numpy"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 75
            },
            SkillCategory.JAVASCRIPT: {
                "confidence": 0.90,
                "keywords": ["javascript", "js", "typescript", "ts"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 70
            },
            SkillCategory.REACT: {
                "confidence": 0.88,
                "keywords": ["react", "reactjs", "next.js", "nextjs"],
                "complexity_handling": "medium",
                "estimated_hourly_rate": 80
            },
            SkillCategory.NODE: {
                "confidence": 0.90,
                "keywords": ["node", "nodejs", "express", "nest.js"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 75
            },
            SkillCategory.API_INTEGRATION: {
                "confidence": 0.95,
                "keywords": ["api", "rest", "graphql", "integration", "endpoint"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 85
            },
            SkillCategory.BUG_FIX: {
                "confidence": 0.92,
                "keywords": ["bug", "fix", "debug", "issue", "error"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 70
            },
            SkillCategory.AUTOMATION: {
                "confidence": 0.95,
                "keywords": ["automation", "script", "automate", "workflow"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 80
            },
            SkillCategory.DATA_PROCESSING: {
                "confidence": 0.93,
                "keywords": ["data", "processing", "etl", "pipeline", "csv", "json"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 75
            },
            SkillCategory.TESTING: {
                "confidence": 0.90,
                "keywords": ["testing", "test", "unittest", "pytest", "jest"],
                "complexity_handling": "medium",
                "estimated_hourly_rate": 65
            },
            SkillCategory.DEPLOYMENT: {
                "confidence": 0.85,
                "keywords": ["deploy", "deployment", "ci/cd", "docker", "kubernetes"],
                "complexity_handling": "medium",
                "estimated_hourly_rate": 80
            },
            SkillCategory.DATABASE: {
                "confidence": 0.88,
                "keywords": ["database", "sql", "postgresql", "mysql", "mongodb"],
                "complexity_handling": "medium",
                "estimated_hourly_rate": 75
            },
            SkillCategory.MACHINE_LEARNING: {
                "confidence": 0.85,
                "keywords": ["ml", "machine learning", "ai", "neural", "tensorflow", "pytorch"],
                "complexity_handling": "medium",
                "estimated_hourly_rate": 90
            },
            SkillCategory.WEB_SCRAPING: {
                "confidence": 0.95,
                "keywords": ["scraping", "scrape", "beautifulsoup", "selenium", "crawler"],
                "complexity_handling": "high",
                "estimated_hourly_rate": 70
            }
        }
    
    def add_platform(self, platform: JobPlatform):
        """Add a platform to monitor."""
        self.monitored_platforms.add(platform)
        print(f"Now monitoring {platform.value}")
    
    def remove_platform(self, platform: JobPlatform):
        """Remove a platform from monitoring."""
        self.monitored_platforms.discard(platform)
        print(f"Stopped monitoring {platform.value}")
    
    def parse_job_description(self, job_data: Dict) -> Dict:
        """
        Parse job description using NLP to extract key information.
        
        Args:
            job_data: Raw job data from platform
            
        Returns:
            Parsed job information
        """
        title = job_data.get("title", "").lower()
        description = job_data.get("description", "").lower()
        combined_text = f"{title} {description}"
        
        # Extract matched skills
        matched_skills = []
        total_confidence = 0.0
        
        for skill, data in self.capability_matrix.items():
            keywords = data["keywords"]
            for keyword in keywords:
                if keyword in combined_text:
                    matched_skills.append({
                        "skill": skill.value,
                        "confidence": data["confidence"],
                        "keyword_matched": keyword
                    })
                    total_confidence += data["confidence"]
                    break
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(matched_skills) if matched_skills else 0.0
        
        # Estimate complexity
        complexity = self._estimate_complexity(description)
        
        # Estimate time required (in hours)
        estimated_hours = self._estimate_time(complexity, len(matched_skills))
        
        # Extract budget information
        budget = self._extract_budget(job_data)
        
        return {
            "job_id": job_data.get("id"),
            "title": job_data.get("title"),
            "platform": job_data.get("platform"),
            "matched_skills": matched_skills,
            "confidence_score": avg_confidence,
            "complexity": complexity,
            "estimated_hours": estimated_hours,
            "budget": budget,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _estimate_complexity(self, description: str) -> str:
        """
        Estimate job complexity based on description.
        
        Args:
            description: Job description text
            
        Returns:
            Complexity level: "simple", "medium", or "complex"
        """
        complexity_indicators = {
            "simple": ["simple", "basic", "straightforward", "quick", "small"],
            "complex": ["complex", "advanced", "sophisticated", "large scale", "enterprise"]
        }
        
        simple_count = sum(1 for word in complexity_indicators["simple"] if word in description)
        complex_count = sum(1 for word in complexity_indicators["complex"] if word in description)
        
        if complex_count > simple_count:
            return "complex"
        elif simple_count > complex_count:
            return "simple"
        else:
            return "medium"
    
    def _estimate_time(self, complexity: str, num_skills: int) -> float:
        """
        Estimate time required in hours.
        
        Args:
            complexity: Job complexity level
            num_skills: Number of skills required
            
        Returns:
            Estimated hours
        """
        base_hours = {
            "simple": 5,
            "medium": 15,
            "complex": 40
        }
        
        hours = base_hours.get(complexity, 15)
        
        # Adjust based on number of skills required
        if num_skills > 3:
            hours *= 1.5
        
        return hours
    
    def _extract_budget(self, job_data: Dict) -> Dict:
        """
        Extract budget information from job data.
        
        Args:
            job_data: Raw job data
            
        Returns:
            Budget information dictionary
        """
        budget_str = job_data.get("budget", "")
        
        # Try to extract numeric budget
        numbers = re.findall(r'\d+', str(budget_str))
        
        if numbers:
            amount = float(numbers[0])
        else:
            amount = 0.0
        
        budget_type = job_data.get("budget_type", "fixed")
        
        return {
            "amount": amount,
            "type": budget_type,
            "currency": job_data.get("currency", "USD")
        }
    
    def assess_profitability(self, parsed_job: Dict) -> Dict:
        """
        Assess if a job meets profitability threshold.
        
        Args:
            parsed_job: Parsed job information
            
        Returns:
            Profitability assessment
        """
        budget = parsed_job["budget"]["amount"]
        estimated_hours = parsed_job["estimated_hours"]
        confidence = parsed_job["confidence_score"]
        
        # Calculate average hourly rate from matched skills
        matched_skills = parsed_job["matched_skills"]
        if matched_skills:
            avg_rate = sum(
                self.capability_matrix[SkillCategory(skill["skill"])]["estimated_hourly_rate"]
                for skill in matched_skills
            ) / len(matched_skills)
        else:
            avg_rate = 70
        
        # Calculate expected value
        if parsed_job["budget"]["type"] == "hourly":
            expected_value = budget * estimated_hours
        else:
            expected_value = budget
        
        expected_hourly_rate = expected_value / estimated_hours if estimated_hours > 0 else 0
        
        # Adjust for confidence
        risk_adjusted_value = expected_value * confidence
        
        is_profitable = (
            expected_value >= self.profitability_threshold and
            expected_hourly_rate >= avg_rate * 0.7 and  # At least 70% of our rate
            confidence >= 0.7  # At least 70% confidence
        )
        
        return {
            "is_profitable": is_profitable,
            "expected_value": expected_value,
            "expected_hourly_rate": expected_hourly_rate,
            "risk_adjusted_value": risk_adjusted_value,
            "profitability_threshold": self.profitability_threshold,
            "recommendation": "bid" if is_profitable else "skip"
        }
    
    def process_job(self, job_data: Dict) -> Optional[Dict]:
        """
        Process a job listing and add to queue if promising.
        
        Args:
            job_data: Raw job data from platform
            
        Returns:
            Processed job data if promising, None otherwise
        """
        # Parse job description
        parsed_job = self.parse_job_description(job_data)
        
        # Assess profitability
        profitability = self.assess_profitability(parsed_job)
        
        # Combine data
        full_assessment = {
            **parsed_job,
            "profitability": profitability,
            "status": "queued" if profitability["is_profitable"] else "rejected",
            "processed_at": datetime.now().isoformat()
        }
        
        # Add to queue if profitable
        if profitability["is_profitable"]:
            self.job_queue.append(full_assessment)
            print(f"✓ Added to queue: {parsed_job['title']} - Expected value: ${profitability['expected_value']}")
        
        return full_assessment
    
    def get_job_queue(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get jobs from the queue.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of queued jobs
        """
        if limit:
            return self.job_queue[:limit]
        return self.job_queue
    
    def clear_queue(self):
        """Clear the job queue."""
        self.job_queue = []
        print("Job queue cleared")
    
    def get_statistics(self) -> Dict:
        """Get prospector statistics."""
        return {
            "total_queued": len(self.job_queue),
            "monitored_platforms": [p.value for p in self.monitored_platforms],
            "profitability_threshold": self.profitability_threshold,
            "capability_count": len(self.capability_matrix),
            "timestamp": datetime.now().isoformat()
        }


def create_job_prospector(config: Optional[Dict] = None) -> JobProspector:
    """
    Factory function to create a job prospector instance.
    
    Args:
        config: Optional configuration
        
    Returns:
        JobProspector instance
    """
    if config:
        return JobProspector(
            profitability_threshold=config.get("profitability_threshold", 100.0)
        )
    return JobProspector()
