#!/usr/bin/env python3
"""
AWS Cost Calculator for Chimera System
Estimates monthly AWS costs based on configuration
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List


class AWSCostCalculator:
    """Calculate estimated AWS costs for Chimera deployment"""
    
    # Pricing (us-east-1, as of January 2025, approximate - verify current pricing)
    PRICES = {
        'ecs_fargate_cpu_per_vcpu_hour': 0.04048,
        'ecs_fargate_memory_per_gb_hour': 0.004445,
        'alb_hour': 0.0225,
        'alb_lcu_hour': 0.008,
        'ecr_storage_gb_month': 0.10,
        'cloudwatch_logs_gb': 0.50,
        'cloudwatch_metrics': 0.30,  # per metric per month
        'data_transfer_out_gb': 0.09,
        'rds_db_t3_micro_hour': 0.017,
        'rds_db_t3_small_hour': 0.034,
        'rds_storage_gb_month': 0.115,
        'elasticache_t3_micro_hour': 0.017,
        'elasticache_t3_small_hour': 0.034,
    }
    
    def __init__(self, config: Dict = None):
        """Initialize calculator with configuration"""
        self.config = config or self.default_config()
        
    @staticmethod
    def default_config() -> Dict:
        """Default configuration for minimal deployment"""
        return {
            'ecs_tasks': 2,
            'cpu_per_task': 0.5,  # vCPU
            'memory_per_task': 1.0,  # GB
            'hours_per_month': 730,
            'alb_enabled': True,
            'alb_lcu_hours': 730,
            'ecr_storage_gb': 5,
            'cloudwatch_logs_gb': 10,
            'cloudwatch_metrics_count': 20,
            'data_transfer_gb': 50,
            'rds_enabled': False,
            'rds_instance_type': 't3.micro',
            'rds_storage_gb': 20,
            'elasticache_enabled': False,
            'elasticache_instance_type': 't3.micro',
        }
    
    def calculate_ecs_cost(self) -> Dict:
        """Calculate ECS Fargate costs"""
        cpu_hours = (self.config['ecs_tasks'] * 
                    self.config['cpu_per_task'] * 
                    self.config['hours_per_month'])
        
        memory_hours = (self.config['ecs_tasks'] * 
                       self.config['memory_per_task'] * 
                       self.config['hours_per_month'])
        
        cpu_cost = cpu_hours * self.PRICES['ecs_fargate_cpu_per_vcpu_hour']
        memory_cost = memory_hours * self.PRICES['ecs_fargate_memory_per_gb_hour']
        
        total = cpu_cost + memory_cost
        
        return {
            'cpu_cost': cpu_cost,
            'memory_cost': memory_cost,
            'total': total,
            'details': {
                'tasks': self.config['ecs_tasks'],
                'cpu_per_task': self.config['cpu_per_task'],
                'memory_per_task': self.config['memory_per_task'],
                'cpu_hours': cpu_hours,
                'memory_hours': memory_hours,
            }
        }
    
    def calculate_alb_cost(self) -> Dict:
        """Calculate Application Load Balancer costs"""
        if not self.config['alb_enabled']:
            return {'total': 0, 'details': 'disabled'}
        
        hourly_cost = self.config['hours_per_month'] * self.PRICES['alb_hour']
        lcu_cost = self.config['alb_lcu_hours'] * self.PRICES['alb_lcu_hour']
        
        total = hourly_cost + lcu_cost
        
        return {
            'hourly_cost': hourly_cost,
            'lcu_cost': lcu_cost,
            'total': total,
        }
    
    def calculate_ecr_cost(self) -> Dict:
        """Calculate ECR storage costs"""
        total = self.config['ecr_storage_gb'] * self.PRICES['ecr_storage_gb_month']
        
        return {
            'total': total,
            'storage_gb': self.config['ecr_storage_gb'],
        }
    
    def calculate_cloudwatch_cost(self) -> Dict:
        """Calculate CloudWatch costs"""
        logs_cost = (self.config['cloudwatch_logs_gb'] * 
                    self.PRICES['cloudwatch_logs_gb'])
        
        metrics_cost = (self.config['cloudwatch_metrics_count'] * 
                       self.PRICES['cloudwatch_metrics'])
        
        total = logs_cost + metrics_cost
        
        return {
            'logs_cost': logs_cost,
            'metrics_cost': metrics_cost,
            'total': total,
        }
    
    def calculate_data_transfer_cost(self) -> Dict:
        """Calculate data transfer costs"""
        # First 1GB is free, then charged per GB
        billable_gb = max(0, self.config['data_transfer_gb'] - 1)
        total = billable_gb * self.PRICES['data_transfer_out_gb']
        
        return {
            'total': total,
            'transfer_gb': self.config['data_transfer_gb'],
            'billable_gb': billable_gb,
        }
    
    def calculate_rds_cost(self) -> Dict:
        """Calculate RDS costs"""
        if not self.config['rds_enabled']:
            return {'total': 0, 'details': 'disabled'}
        
        instance_type = self.config['rds_instance_type']
        price_key = f"rds_db_{instance_type.replace('.', '_')}_hour"
        
        instance_cost = (self.config['hours_per_month'] * 
                        self.PRICES.get(price_key, 0.034))
        
        storage_cost = (self.config['rds_storage_gb'] * 
                       self.PRICES['rds_storage_gb_month'])
        
        total = instance_cost + storage_cost
        
        return {
            'instance_cost': instance_cost,
            'storage_cost': storage_cost,
            'total': total,
            'instance_type': instance_type,
            'storage_gb': self.config['rds_storage_gb'],
        }
    
    def calculate_elasticache_cost(self) -> Dict:
        """Calculate ElastiCache costs"""
        if not self.config['elasticache_enabled']:
            return {'total': 0, 'details': 'disabled'}
        
        instance_type = self.config['elasticache_instance_type']
        price_key = f"elasticache_{instance_type.replace('.', '_')}_hour"
        
        total = (self.config['hours_per_month'] * 
                self.PRICES.get(price_key, 0.034))
        
        return {
            'total': total,
            'instance_type': instance_type,
        }
    
    def calculate_total(self) -> Dict:
        """Calculate total estimated costs"""
        ecs = self.calculate_ecs_cost()
        alb = self.calculate_alb_cost()
        ecr = self.calculate_ecr_cost()
        cloudwatch = self.calculate_cloudwatch_cost()
        data_transfer = self.calculate_data_transfer_cost()
        rds = self.calculate_rds_cost()
        elasticache = self.calculate_elasticache_cost()
        
        total = (ecs['total'] + alb['total'] + ecr['total'] + 
                cloudwatch['total'] + data_transfer['total'] + 
                rds['total'] + elasticache['total'])
        
        return {
            'breakdown': {
                'ecs_fargate': ecs,
                'load_balancer': alb,
                'ecr_storage': ecr,
                'cloudwatch': cloudwatch,
                'data_transfer': data_transfer,
                'rds_database': rds,
                'elasticache': elasticache,
            },
            'total_monthly': total,
            'total_yearly': total * 12,
            'calculated_at': datetime.utcnow().isoformat(),
            'configuration': self.config,
        }


def format_currency(amount: float) -> str:
    """Format amount as USD currency"""
    return f"${amount:.2f}"


def print_cost_report(costs: Dict, verbose: bool = False):
    """Print formatted cost report"""
    print("\n" + "="*60)
    print("AWS COST ESTIMATE - Chimera System")
    print("="*60)
    
    print("\n📊 COST BREAKDOWN:\n")
    
    breakdown = costs['breakdown']
    
    # ECS Fargate
    ecs = breakdown['ecs_fargate']
    print(f"ECS Fargate:")
    print(f"  CPU:              {format_currency(ecs['cpu_cost'])}")
    print(f"  Memory:           {format_currency(ecs['memory_cost'])}")
    print(f"  Subtotal:         {format_currency(ecs['total'])}")
    if verbose:
        print(f"    ({ecs['details']['tasks']} tasks × "
              f"{ecs['details']['cpu_per_task']} vCPU × "
              f"{ecs['details']['memory_per_task']} GB)")
    
    # Load Balancer
    alb = breakdown['load_balancer']
    if alb['total'] > 0:
        print(f"\nLoad Balancer:")
        print(f"  Hourly:           {format_currency(alb['hourly_cost'])}")
        print(f"  LCU:              {format_currency(alb['lcu_cost'])}")
        print(f"  Subtotal:         {format_currency(alb['total'])}")
    
    # ECR
    ecr = breakdown['ecr_storage']
    print(f"\nECR Storage:")
    print(f"  {ecr['storage_gb']} GB:         {format_currency(ecr['total'])}")
    
    # CloudWatch
    cw = breakdown['cloudwatch']
    print(f"\nCloudWatch:")
    print(f"  Logs:             {format_currency(cw['logs_cost'])}")
    print(f"  Metrics:          {format_currency(cw['metrics_cost'])}")
    print(f"  Subtotal:         {format_currency(cw['total'])}")
    
    # Data Transfer
    dt = breakdown['data_transfer']
    print(f"\nData Transfer:")
    print(f"  {dt['transfer_gb']} GB out:       {format_currency(dt['total'])}")
    
    # RDS
    rds = breakdown['rds_database']
    if rds['total'] > 0:
        print(f"\nRDS Database:")
        print(f"  Instance:         {format_currency(rds['instance_cost'])}")
        print(f"  Storage:          {format_currency(rds['storage_cost'])}")
        print(f"  Subtotal:         {format_currency(rds['total'])}")
    
    # ElastiCache
    ec = breakdown['elasticache']
    if ec['total'] > 0:
        print(f"\nElastiCache:")
        print(f"  Instance:         {format_currency(ec['total'])}")
    
    # Total
    print("\n" + "-"*60)
    print(f"💰 TOTAL MONTHLY:   {format_currency(costs['total_monthly'])}")
    print(f"📅 TOTAL YEARLY:    {format_currency(costs['total_yearly'])}")
    print("-"*60)
    
    print("\n💡 COST OPTIMIZATION TIPS:")
    print("  • Use Fargate Spot for up to 70% savings on compute")
    print("  • Scale down tasks during off-peak hours")
    print("  • Use RDS Reserved Instances for long-term deployments")
    print("  • Enable S3 lifecycle policies for old logs")
    print("  • Monitor and optimize data transfer patterns")
    
    print("\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Calculate AWS costs for Chimera deployment'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed breakdown'
    )
    parser.add_argument(
        '--with-database',
        action='store_true',
        help='Include RDS database in estimate'
    )
    parser.add_argument(
        '--with-cache',
        action='store_true',
        help='Include ElastiCache in estimate'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = AWSCostCalculator.default_config()
        
        # Apply command-line options
        if args.with_database:
            config['rds_enabled'] = True
        if args.with_cache:
            config['elasticache_enabled'] = True
    
    # Calculate costs
    calculator = AWSCostCalculator(config)
    costs = calculator.calculate_total()
    
    # Output results
    if args.output == 'json':
        print(json.dumps(costs, indent=2))
    else:
        print_cost_report(costs, verbose=args.verbose)


if __name__ == '__main__':
    main()
