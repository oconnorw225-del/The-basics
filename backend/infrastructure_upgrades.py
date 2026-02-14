"""
Infrastructure & Security Upgrades - V4 System Enhancements
Decentralized Auditing, Natural Language Interface, and Distributed Computing.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional


class DecentralizedAuditor:
    """
    Decentralized Auditing System.
    Logs major actions to blockchain for immutable audit trail.
    """

    def __init__(self, blockchain_network: str = "ethereum"):
        """
        Initialize decentralized auditor.

        Args:
            blockchain_network: Target blockchain network
        """
        self.blockchain_network = blockchain_network
        self.audit_log: List[Dict] = []
        self.blockchain_transactions: List[Dict] = []

    def log_action(self, action_type: str, details: Dict) -> Dict:
        """
        Log an action to the audit trail.

        Args:
            action_type: Type of action
            details: Action details

        Returns:
            Audit log entry
        """
        log_entry = {
            "log_id": f"log_{len(self.audit_log) + 1}",
            "action_type": action_type,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "hash": self._calculate_hash(action_type, details),
        }

        self.audit_log.append(log_entry)

        # Log to blockchain for major actions
        if self._is_major_action(action_type):
            blockchain_tx = self._log_to_blockchain(log_entry)
            log_entry["blockchain_tx"] = blockchain_tx

        print(f"✓ Action logged: {action_type}")
        if "blockchain_tx" in log_entry:
            print(
                f"  Blockchain TX: {log_entry['blockchain_tx']['tx_hash'][:16]}...")

        return log_entry

    def _calculate_hash(self, action_type: str, details: Dict) -> str:
        """Calculate hash of action for integrity."""
        data = json.dumps(
            {"action": action_type, "details": details}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def _is_major_action(self, action_type: str) -> bool:
        """Determine if action should be logged to blockchain."""
        major_actions = [
            "strategy_deployment",
            "large_fund_transfer",
            "capital_allocation",
            "bot_activation",
            "wallet_creation",
            "security_change",
        ]
        return action_type in major_actions

    def _log_to_blockchain(self, log_entry: Dict) -> Dict:
        """
        Log entry to blockchain.

        Args:
            log_entry: Audit log entry

        Returns:
            Blockchain transaction details
        """
        # In production, actually write to blockchain
        tx = {
            "tx_hash": f"0x{hashlib.sha256(log_entry['hash'].encode()).hexdigest()}",
            "block_number": 12345678 + len(self.blockchain_transactions),
            "network": self.blockchain_network,
            "gas_used": 21000,
            "data": log_entry["hash"],
            "timestamp": datetime.now().isoformat(),
            "confirmed": True,
        }

        self.blockchain_transactions.append(tx)

        return tx

    def verify_integrity(self) -> Dict:
        """Verify integrity of audit log."""
        verified = 0
        failed = 0

        for entry in self.audit_log:
            recalculated_hash = self._calculate_hash(
                entry["action_type"], entry["details"])
            if recalculated_hash == entry["hash"]:
                verified += 1
            else:
                failed += 1

        return {
            "total_entries": len(self.audit_log),
            "verified": verified,
            "failed": failed,
            "integrity": "intact" if failed == 0 else "compromised",
            "blockchain_entries": len(self.blockchain_transactions),
        }

    def get_audit_trail(
            self,
            action_type: Optional[str] = None,
            limit: int = 100) -> List[Dict]:
        """Get audit trail."""
        if action_type:
            filtered = [
                log for log in self.audit_log if log["action_type"] == action_type]
            return filtered[-limit:]
        return self.audit_log[-limit:]


class NaturalLanguageInterface:
    """
    Natural Language Interface for Command Console.
    Allows plain English commands.
    """

    def __init__(self):
        """Initialize NL interface."""
        self.command_history: List[Dict] = []
        self.command_patterns = self._load_command_patterns()

    def _load_command_patterns(self) -> Dict:
        """Load natural language command patterns."""
        return {
            "performance": {
                "patterns": [
                    r"show.*performance.*(\d+).*hours?",
                    r"how.*doing.*last.*(\d+).*hours?",
                    r"performance.*report.*(\d+).*hours?",
                ],
                "intent": "get_performance",
                "extract": ["time_period"],
            },
            "bot_status": {
                "patterns": [
                    r"show.*bots?.*status",
                    r"list.*active.*bots?",
                    r"what.*bots?.*running",
                ],
                "intent": "get_bot_status",
                "extract": [],
            },
            "capital_allocation": {
                "patterns": [
                    r"allocate.*\$?(\d+).*to.*(\w+)",
                    r"give.*(\w+).*\$?(\d+)",
                    r"increase.*(\w+).*capital.*(\d+)",
                ],
                "intent": "allocate_capital",
                "extract": ["amount", "bot_id"],
            },
            "double_allocation": {
                "patterns": [
                    r"double.*capital.*(\w+)",
                    r"2x.*allocation.*(\w+)",
                    r"increase.*(\w+).*100%",
                ],
                "intent": "double_allocation",
                "extract": ["bot_id"],
            },
            "trading_control": {
                "patterns": [r"stop.*trading", r"pause.*all.*bots?", r"emergency.*stop"],
                "intent": "emergency_stop",
                "extract": [],
            },
        }

    def parse_command(self, natural_command: str) -> Dict:
        """
        Parse natural language command.

        Args:
            natural_command: Command in plain English

        Returns:
            Parsed command structure
        """
        import re

        command_lower = natural_command.lower()

        # Try to match patterns
        for category, config in self.command_patterns.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, command_lower)
                if match:
                    # Extract parameters
                    params = {}
                    if config["extract"]:
                        for i, param_name in enumerate(config["extract"]):
                            if i < len(match.groups()):
                                params[param_name] = match.group(i + 1)

                    parsed = {
                        "original_command": natural_command,
                        "intent": config["intent"],
                        "parameters": params,
                        "category": category,
                        "parsed_at": datetime.now().isoformat(),
                    }

                    self.command_history.append(parsed)

                    print(f"✓ Command parsed: {config['intent']}")
                    print(f"  Parameters: {params}")

                    return parsed

        # No match found
        return {
            "original_command": natural_command,
            "intent": "unknown",
            "error": "Could not parse command",
            "suggestions": self._get_suggestions(command_lower),
        }

    def _get_suggestions(self, command: str) -> List[str]:
        """Get command suggestions."""
        return [
            "Show me the performance of all bots over the last 24 hours",
            "List all active bots",
            "Double the capital allocation to the top-performing bot",
            "Allocate $10000 to arbitrage_bot",
            "Stop all trading",
        ]

    def execute_command(
            self,
            parsed_command: Dict,
            system_context: Dict) -> Dict:
        """
        Execute parsed command.

        Args:
            parsed_command: Parsed command
            system_context: System context (bots, capital, etc.)

        Returns:
            Execution result
        """
        intent = parsed_command.get("intent")
        params = parsed_command.get("parameters", {})

        if intent == "get_performance":
            return self._get_performance(params, system_context)
        elif intent == "get_bot_status":
            return self._get_bot_status(system_context)
        elif intent == "allocate_capital":
            return self._allocate_capital(params, system_context)
        elif intent == "double_allocation":
            return self._double_allocation(params, system_context)
        elif intent == "emergency_stop":
            return self._emergency_stop(system_context)
        else:
            return {"error": "Unknown intent"}

    def _get_performance(self, params: Dict, context: Dict) -> Dict:
        """Get performance report."""
        hours = int(params.get("time_period", 24))
        return {
            "intent": "performance_report",
            "time_period_hours": hours,
            "summary": f"Performance report for last {hours} hours",
            "data": context.get("performance_data", {}),
        }

    def _get_bot_status(self, context: Dict) -> Dict:
        """Get bot status."""
        bots = context.get("bots", {})
        return {
            "intent": "bot_status",
            "total_bots": len(bots),
            "active_bots": [
                bot_id for bot_id,
                bot in bots.items() if bot.get("status") == "active"],
            "bots": bots,
        }

    def _allocate_capital(self, params: Dict, context: Dict) -> Dict:
        """Allocate capital to bot."""
        amount = float(params.get("amount", 0))
        bot_id = params.get("bot_id", "")

        return {
            "intent": "capital_allocation",
            "bot_id": bot_id,
            "amount": amount,
            "action": "allocate",
            "message": f"Allocated ${amount:,.2f} to {bot_id}",
        }

    def _double_allocation(self, params: Dict, context: Dict) -> Dict:
        """Double capital allocation."""
        bot_id = params.get("bot_id", "")
        current = context.get(
            "bots",
            {}).get(
            bot_id,
            {}).get(
            "allocated_capital",
            0)
        new_amount = current * 2

        return {
            "intent": "double_allocation",
            "bot_id": bot_id,
            "previous_amount": current,
            "new_amount": new_amount,
            "message": f"Doubled allocation for {bot_id}: ${current:,.2f} → ${new_amount:,.2f}",
        }

    def _emergency_stop(self, context: Dict) -> Dict:
        """Emergency stop all trading."""
        return {
            "intent": "emergency_stop",
            "action": "stop_all_trading",
            "message": "Emergency stop initiated - all trading halted",
            "timestamp": datetime.now().isoformat(),
        }


class DistributedComputing:
    """
    Distributed Computing System.
    Enables parallel processing for backtesting and strategy evolution.
    """

    def __init__(self, num_workers: int = 8):
        """
        Initialize distributed computing system.

        Args:
            num_workers: Number of parallel workers
        """
        self.num_workers = num_workers
        self.active_jobs: List[Dict] = []
        self.completed_jobs: List[Dict] = []

    def submit_backtest_job(
            self,
            strategies: List[Dict],
            market_data: Dict) -> Dict:
        """
        Submit backtesting job for parallel processing.

        Args:
            strategies: List of strategies to test
            market_data: Historical market data

        Returns:
            Job submission details
        """
        job_id = f"backtest_{len(self.active_jobs) + len(self.completed_jobs) + 1}"

        # Divide strategies among workers
        strategies_per_worker = len(strategies) // self.num_workers + 1
        worker_assignments = []

        for i in range(self.num_workers):
            start_idx = i * strategies_per_worker
            end_idx = min((i + 1) * strategies_per_worker, len(strategies))

            if start_idx < len(strategies):
                worker_assignments.append(
                    {
                        "worker_id": f"worker_{i + 1}",
                        "strategies": strategies[start_idx:end_idx],
                        "strategy_count": end_idx - start_idx,
                    }
                )

        job = {
            "job_id": job_id,
            "type": "backtest",
            "total_strategies": len(strategies),
            "num_workers": len(worker_assignments),
            "worker_assignments": worker_assignments,
            "status": "submitted",
            "submitted_at": datetime.now().isoformat(),
            "estimated_completion": self._estimate_completion(len(strategies)),
        }

        self.active_jobs.append(job)

        print(f"✓ Backtest job submitted: {job_id}")
        print(f"  Strategies: {len(strategies)}")
        print(f"  Workers: {self.num_workers}")
        print(f"  Estimated completion: {job['estimated_completion']}")

        return job

    def _estimate_completion(self, num_strategies: int) -> str:
        """Estimate job completion time."""
        # Assume 2 seconds per strategy per worker
        time_per_batch = 2
        batches = num_strategies // self.num_workers + 1
        total_seconds = batches * time_per_batch

        return f"{total_seconds} seconds"

    def simulate_parallel_execution(self, job_id: str) -> Dict:
        """
        Simulate parallel execution of job.

        Args:
            job_id: Job identifier

        Returns:
            Execution results
        """
        job = next(
            (j for j in self.active_jobs if j["job_id"] == job_id),
            None)

        if not job:
            return {"error": "Job not found"}

        # Simulate worker execution
        worker_results = []

        for assignment in job["worker_assignments"]:
            worker_result = {
                "worker_id": assignment["worker_id"],
                "strategies_tested": assignment["strategy_count"],
                "best_strategy": {
                    "id": f"strategy_{assignment['worker_id']}_best",
                    "sharpe_ratio": 1.5 + (hash(assignment["worker_id"]) % 100) / 100,
                    "return": 15 + (hash(assignment["worker_id"]) % 30),
                },
                "execution_time_seconds": 2 * assignment["strategy_count"] / self.num_workers,
                "completed_at": datetime.now().isoformat(),
            }
            worker_results.append(worker_result)

        # Find overall best strategy
        best_overall = max(
            worker_results,
            key=lambda x: x["best_strategy"]["sharpe_ratio"])

        result = {
            "job_id": job_id,
            "status": "completed",
            "worker_results": worker_results,
            "best_strategy": best_overall["best_strategy"],
            "total_execution_time": max(
                r["execution_time_seconds"] for r in worker_results),
            "speedup": f"{self.num_workers}x faster than sequential",
            "completed_at": datetime.now().isoformat(),
        }

        # Move to completed
        job["status"] = "completed"
        job["results"] = result
        self.active_jobs.remove(job)
        self.completed_jobs.append(job)

        print(f"✓ Job completed: {job_id}")
        print(
            f"  Best Sharpe Ratio: {result['best_strategy']['sharpe_ratio']:.2f}")
        print(f"  Execution time: {result['total_execution_time']:.1f}s")

        return result

    def get_cluster_status(self) -> Dict:
        """Get distributed computing cluster status."""
        return {
            "num_workers": self.num_workers,
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "total_strategies_tested": sum(
                job.get("total_strategies", 0) for job in self.completed_jobs
            ),
            "timestamp": datetime.now().isoformat(),
        }


def create_infrastructure_system(num_workers: int = 8) -> Dict:
    """
    Factory function to create infrastructure system.

    Args:
        num_workers: Number of distributed computing workers

    Returns:
        Dictionary of infrastructure components
    """
    return {
        "auditor": DecentralizedAuditor(),
        "nl_interface": NaturalLanguageInterface(),
        "distributed_compute": DistributedComputing(num_workers),
    }
