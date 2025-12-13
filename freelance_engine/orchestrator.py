"""
Freelance Job Orchestrator - Enhanced Autonomous System
Unified master loop for job processing, execution, and payment collection.
Cherry-picked from AI jobs orchestration engine.
ENHANCED WITH ERROR HANDLING AND RETRY LOGIC
"""

import asyncio
import logging
import sys
import signal
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from job_prospector import JobProspector, JobPlatform
from automated_bidder import ProposalGenerator, AutomatedBidder
from internal_coding_agent import CodingAgent
from payment_handler import PaymentHandler


# Configure logging with error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/freelance-orchestrator.log')
    ]
)
logger = logging.getLogger('FreelanceOrchestrator')

# Error statistics
error_stats = {
    'total_errors': 0,
    'scan_errors': 0,
    'bid_errors': 0,
    'execution_errors': 0,
    'payment_errors': 0,
    'recoveries': 0
}


class JobStatus(Enum):
    """Job processing status."""
    DISCOVERED = "discovered"
    ANALYZING = "analyzing"
    BIDDING = "bidding"
    AWAITING_ACCEPTANCE = "awaiting_acceptance"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    PAID = "paid"
    REJECTED = "rejected"
    FAILED = "failed"


class FreelanceOrchestrator:
    """
    Master orchestration engine for autonomous freelance operations.
    Manages the complete lifecycle: discovery → bidding → execution → delivery → payment.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Configuration dictionary with thresholds and settings
        """
        self.config = config or self._default_config()
        
        # Initialize components
        self.prospector = JobProspector(
            profitability_threshold=self.config['profitability_threshold']
        )
        self.proposal_generator = ProposalGenerator()
        self.bidder = AutomatedBidder()
        self.coding_agent = CodingAgent()
        self.payment_handler = PaymentHandler()
        
        # State management
        self.active_jobs: Dict[str, Dict] = {}
        self.job_queue: List[Dict] = []
        self.statistics = {
            'jobs_discovered': 0,
            'bids_placed': 0,
            'jobs_won': 0,
            'jobs_completed': 0,
            'total_revenue': 0.0,
            'success_rate': 0.0
        }
        
        # Platform connectors (to be implemented)
        self.platform_connectors = {}
        
        logger.info("🚀 Freelance Orchestrator initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration."""
        return {
            'profitability_threshold': 100.0,
            'job_confidence_threshold': 0.75,
            'scan_interval': 300,  # 5 minutes
            'max_concurrent_jobs': 3,
            'work_acceptance_timeout': 900,  # 15 minutes
            'execution_max_time': 3600,  # 1 hour
            'auto_bid': True,
            'auto_execute': False,  # Requires approval by default
            'platforms': ['upwork', 'freelancer', 'fiverr', 'toptal']
        }
    
    async def start(self):
        """Start the autonomous freelance operation loop with error handling."""
        logger.info("🎯 Starting autonomous freelance operations...")
        logger.info(f"Configuration: {self.config}")
        
        # Setup signal handlers for graceful shutdown
        self.shutdown_event = asyncio.Event()
        signal.signal(signal.SIGTERM, lambda s, f: self.shutdown_event.set())
        signal.signal(signal.SIGINT, lambda s, f: self.shutdown_event.set())
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while not self.shutdown_event.is_set():
                try:
                    # Step 1: Scan for jobs
                    await self._scan_platforms()
                    
                    # Step 2: Process job queue
                    await self._process_job_queue()
                    
                    # Step 3: Check pending acceptances
                    await self._check_pending_jobs()
                    
                    # Step 4: Execute active work
                    await self._execute_active_jobs()
                    
                    # Step 5: Deliver completed work
                    await self._deliver_completed_work()
                    
                    # Step 6: Collect payments
                    await self._collect_payments()
                    
                    # Step 7: Update statistics
                    self._update_statistics()
                    
                    # Log status
                    logger.info(f"📊 Status: {len(self.active_jobs)} active | "
                              f"{len(self.job_queue)} queued | "
                              f"${self.statistics['total_revenue']:.2f} revenue | "
                              f"Errors: {error_stats['total_errors']}")
                    
                    # Reset consecutive error counter on success
                    consecutive_errors = 0
                    
                    # Wait before next cycle
                    await asyncio.wait_for(
                        self.shutdown_event.wait(),
                        timeout=self.config['scan_interval']
                    )
                    
                except asyncio.TimeoutError:
                    # Normal timeout, continue loop
                    continue
                    
                except Exception as e:
                    consecutive_errors += 1
                    error_stats['total_errors'] += 1
                    logger.error(f"❌ Error in main loop (attempt {consecutive_errors}/{max_consecutive_errors}): {e}", exc_info=True)
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.critical(f"💥 Too many consecutive errors ({consecutive_errors}), shutting down...")
                        break
                    
                    # Exponential backoff before retry
                    await asyncio.sleep(min(60, 2 ** consecutive_errors))
                
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received...")
        finally:
            logger.info("🛑 Shutting down gracefully...")
            await self._shutdown()
    
    async def _scan_platforms(self):
        """Scan freelance platforms for new opportunities with error handling."""
        logger.info("🔍 Scanning platforms for jobs...")
        
        for platform_name in self.config['platforms']:
            try:
                # Convert platform name to enum
                platform = JobPlatform(platform_name)
                
                # Scan platform (using existing prospector)
                jobs = self.prospector.scan_platform(platform)
                
                for job in jobs:
                    # Analyze job profitability
                    assessed_job = self.prospector.assess_profitability(job)
                    
                    # Check if meets threshold
                    if assessed_job.get('profitability_score', 0) >= self.config['profitability_threshold']:
                        # Add to queue
                        self.job_queue.append({
                            'job': assessed_job,
                            'platform': platform_name,
                            'discovered_at': datetime.now().isoformat(),
                            'status': JobStatus.DISCOVERED.value
                        })
                        self.statistics['jobs_discovered'] += 1
                        
                        logger.info(f"✅ Found opportunity: {assessed_job.get('title')} "
                                  f"(${assessed_job.get('profitability_score'):.2f})")
                
            except Exception as e:
                logger.error(f"❌ Error scanning {platform_name}: {e}")
    
    async def _process_job_queue(self):
        """Process jobs in the queue - analyze and bid."""
        if not self.job_queue:
            return
        
        logger.info(f"📋 Processing {len(self.job_queue)} queued jobs...")
        
        # Process up to max concurrent
        while self.job_queue and len(self.active_jobs) < self.config['max_concurrent_jobs']:
            job_data = self.job_queue.pop(0)
            
            try:
                await self._handle_job(job_data)
            except Exception as e:
                logger.error(f"❌ Error handling job: {e}")
                job_data['status'] = JobStatus.FAILED.value
    
    async def _handle_job(self, job_data: Dict):
        """
        Master job handler - orchestrates the complete job lifecycle.
        Cherry-picked from AI jobs orchestration engine.
        """
        job = job_data['job']
        platform = job_data['platform']
        
        logger.info(f"🔍 Processing job: {job.get('title')}")
        
        # Step 1: Generate proposal
        proposal_data = self.proposal_generator.generate_proposal(job)
        
        if not proposal_data:
            logger.warning(f"❌ Failed to generate proposal for {job.get('title')}")
            return
        
        logger.info(f"📝 Generated proposal ({proposal_data['word_count']} words)")
        
        # Step 2: Calculate bid amount
        bid_amount = self.bidder.calculate_bid(job, proposal_data)
        
        logger.info(f"💰 Calculated bid: ${bid_amount:.2f}")
        
        # Step 3: Place bid (if auto-bidding enabled)
        if self.config['auto_bid']:
            bid_result = await self._place_bid(platform, job, proposal_data, bid_amount)
            
            if bid_result.get('success'):
                # Add to active jobs
                job_id = job.get('id', f"job_{len(self.active_jobs)}")
                self.active_jobs[job_id] = {
                    'job': job,
                    'platform': platform,
                    'proposal': proposal_data,
                    'bid_amount': bid_amount,
                    'status': JobStatus.AWAITING_ACCEPTANCE.value,
                    'bid_placed_at': datetime.now().isoformat()
                }
                
                self.statistics['bids_placed'] += 1
                logger.info(f"✅ Bid placed successfully for {job.get('title')}")
            else:
                logger.warning(f"❌ Failed to place bid: {bid_result.get('error')}")
        else:
            logger.info(f"⏸️ Auto-bid disabled, requires manual approval")
    
    async def _place_bid(self, platform: str, job: Dict, proposal: Dict, amount: float) -> Dict:
        """Place a bid on a platform."""
        # This would connect to actual platform APIs
        # For now, return mock success
        logger.info(f"📤 Placing bid on {platform}...")
        
        # Simulate API call
        await asyncio.sleep(0.5)
        
        return {
            'success': True,
            'bid_id': f"bid_{datetime.now().timestamp()}",
            'message': 'Bid placed successfully'
        }
    
    async def _check_pending_jobs(self):
        """Check for job acceptances on platforms."""
        pending_jobs = [
            (job_id, job_data) for job_id, job_data in self.active_jobs.items()
            if job_data['status'] == JobStatus.AWAITING_ACCEPTANCE.value
        ]
        
        if not pending_jobs:
            return
        
        logger.info(f"⏳ Checking {len(pending_jobs)} pending job(s)...")
        
        for job_id, job_data in pending_jobs:
            # Check if job was accepted (mock for now)
            # In production, poll platform APIs
            
            # For demo, randomly accept some jobs
            import random
            if random.random() > 0.7:  # 30% acceptance rate simulation
                job_data['status'] = JobStatus.ACCEPTED.value
                job_data['accepted_at'] = datetime.now().isoformat()
                self.statistics['jobs_won'] += 1
                
                logger.info(f"🎉 Job accepted: {job_data['job'].get('title')}")
    
    async def _execute_active_jobs(self):
        """Execute work for accepted jobs."""
        accepted_jobs = [
            (job_id, job_data) for job_id, job_data in self.active_jobs.items()
            if job_data['status'] == JobStatus.ACCEPTED.value
        ]
        
        if not accepted_jobs:
            return
        
        logger.info(f"🔨 Executing {len(accepted_jobs)} job(s)...")
        
        for job_id, job_data in accepted_jobs:
            if self.config['auto_execute']:
                # Autonomous execution
                job_data['status'] = JobStatus.IN_PROGRESS.value
                job_data['started_at'] = datetime.now().isoformat()
                
                # Use coding agent to complete work
                result = await self._execute_work(job_data)
                
                if result.get('success'):
                    job_data['status'] = JobStatus.DELIVERING.value
                    job_data['deliverable'] = result.get('deliverable')
                    logger.info(f"✅ Work completed: {job_data['job'].get('title')}")
                else:
                    job_data['status'] = JobStatus.FAILED.value
                    logger.error(f"❌ Work failed: {result.get('error')}")
            else:
                logger.info(f"⏸️ Auto-execute disabled for {job_data['job'].get('title')}")
    
    async def _execute_work(self, job_data: Dict) -> Dict:
        """Execute the actual work for a job."""
        job = job_data['job']
        
        logger.info(f"🔨 Executing work for: {job.get('title')}")
        
        # Analyze requirements
        requirements = job.get('description', '')
        
        # Use coding agent (in production, this would generate actual code)
        # For now, return mock deliverable
        await asyncio.sleep(2)  # Simulate work time
        
        return {
            'success': True,
            'deliverable': {
                'type': 'code',
                'files': ['main.py', 'README.md'],
                'description': 'Implementation complete with documentation'
            }
        }
    
    async def _deliver_completed_work(self):
        """Deliver completed work to clients."""
        delivering_jobs = [
            (job_id, job_data) for job_id, job_data in self.active_jobs.items()
            if job_data['status'] == JobStatus.DELIVERING.value
        ]
        
        if not delivering_jobs:
            return
        
        logger.info(f"📦 Delivering {len(delivering_jobs)} completed job(s)...")
        
        for job_id, job_data in delivering_jobs:
            # Deliver work via platform API
            delivery_result = await self._deliver_work(job_data)
            
            if delivery_result.get('success'):
                job_data['status'] = JobStatus.COMPLETED.value
                job_data['delivered_at'] = datetime.now().isoformat()
                self.statistics['jobs_completed'] += 1
                
                logger.info(f"✅ Work delivered: {job_data['job'].get('title')}")
            else:
                logger.error(f"❌ Delivery failed: {delivery_result.get('error')}")
    
    async def _deliver_work(self, job_data: Dict) -> Dict:
        """Deliver work to platform."""
        platform = job_data['platform']
        deliverable = job_data.get('deliverable')
        
        logger.info(f"📤 Delivering to {platform}...")
        
        # Simulate API call
        await asyncio.sleep(0.5)
        
        return {
            'success': True,
            'delivery_id': f"delivery_{datetime.now().timestamp()}",
            'message': 'Work delivered successfully'
        }
    
    async def _collect_payments(self):
        """Collect payments for completed jobs."""
        completed_jobs = [
            (job_id, job_data) for job_id, job_data in self.active_jobs.items()
            if job_data['status'] == JobStatus.COMPLETED.value
        ]
        
        if not completed_jobs:
            return
        
        logger.info(f"💰 Collecting payments for {len(completed_jobs)} job(s)...")
        
        for job_id, job_data in completed_jobs:
            # Process payment
            payment_result = self.payment_handler.process_payment({
                'job_id': job_id,
                'amount': job_data['bid_amount'],
                'platform': job_data['platform']
            })
            
            if payment_result.get('status') == 'received':
                job_data['status'] = JobStatus.PAID.value
                job_data['paid_at'] = datetime.now().isoformat()
                
                # Update revenue
                self.statistics['total_revenue'] += job_data['bid_amount']
                
                logger.info(f"💰 Payment received: ${job_data['bid_amount']:.2f} for {job_data['job'].get('title')}")
                
                # Remove from active jobs
                del self.active_jobs[job_id]
    
    def _update_statistics(self):
        """Update performance statistics."""
        if self.statistics['bids_placed'] > 0:
            self.statistics['success_rate'] = (
                self.statistics['jobs_won'] / self.statistics['bids_placed'] * 100
            )
    
    async def _shutdown(self):
        """Graceful shutdown."""
        logger.info("📊 Final Statistics:")
        logger.info(f"  Jobs Discovered: {self.statistics['jobs_discovered']}")
        logger.info(f"  Bids Placed: {self.statistics['bids_placed']}")
        logger.info(f"  Jobs Won: {self.statistics['jobs_won']}")
        logger.info(f"  Jobs Completed: {self.statistics['jobs_completed']}")
        logger.info(f"  Total Revenue: ${self.statistics['total_revenue']:.2f}")
        logger.info(f"  Success Rate: {self.statistics['success_rate']:.1f}%")
        
        logger.info("👋 Freelance Orchestrator shut down")
    
    def get_status(self) -> Dict:
        """Get current orchestrator status."""
        return {
            'active_jobs': len(self.active_jobs),
            'queued_jobs': len(self.job_queue),
            'statistics': self.statistics,
            'config': self.config
        }


async def main():
    """Main entry point for orchestrator."""
    config = {
        'profitability_threshold': 100.0,
        'job_confidence_threshold': 0.75,
        'scan_interval': 300,
        'max_concurrent_jobs': 3,
        'auto_bid': True,
        'auto_execute': False,  # Safety: requires approval
        'platforms': ['upwork', 'freelancer', 'fiverr']
    }
    
    orchestrator = FreelanceOrchestrator(config=config)
    await orchestrator.start()


if __name__ == '__main__':
    asyncio.run(main())
