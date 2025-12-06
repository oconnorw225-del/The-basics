"""
Invoicing & Payment Handler - V4 Freelance Engine
Handles invoice generation and payment processing for completed work.
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"


class Currency(Enum):
    """Supported currencies."""
    USD = "usd"
    EUR = "eur"
    BTC = "btc"
    ETH = "eth"
    USDT = "usdt"


class PaymentHandler:
    """
    Handles invoicing and payment processing for freelance work.
    Integrates with Chimera Treasury system.
    """
    
    def __init__(self, treasury_wallet_address: Optional[str] = None):
        """
        Initialize payment handler.
        
        Args:
            treasury_wallet_address: Chimera Treasury inflow wallet address
        """
        self.treasury_wallet = treasury_wallet_address or "chimera_inflow_wallet_default"
        self.invoices: List[Dict] = []
        self.payments: List[Dict] = []
        
    def generate_invoice(self, job_data: Dict, work_completed: Dict) -> Dict:
        """
        Generate an invoice for completed work.
        
        Args:
            job_data: Original job/bid information
            work_completed: Work completion details
            
        Returns:
            Generated invoice
        """
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{len(self.invoices) + 1:04d}"
        
        # Calculate totals
        hours_worked = work_completed.get("hours_worked", job_data.get("estimated_hours", 0))
        hourly_rate = job_data.get("hourly_rate", 75)
        
        if job_data.get("budget_type") == "fixed":
            subtotal = job_data.get("bid_amount", 0)
        else:
            subtotal = hours_worked * hourly_rate
        
        # Platform fee (typically 10-20%)
        platform_fee_rate = work_completed.get("platform_fee_rate", 0.10)
        platform_fee = subtotal * platform_fee_rate
        
        # Net amount after platform fee
        net_amount = subtotal - platform_fee
        
        invoice = {
            "invoice_number": invoice_number,
            "job_id": job_data.get("job_id"),
            "job_title": job_data.get("job_title"),
            "client_info": job_data.get("client", {}),
            "platform": job_data.get("platform"),
            "line_items": [
                {
                    "description": job_data.get("job_title"),
                    "hours": hours_worked,
                    "rate": hourly_rate,
                    "amount": subtotal
                }
            ],
            "subtotal": subtotal,
            "platform_fee": platform_fee,
            "platform_fee_rate": platform_fee_rate,
            "net_amount": net_amount,
            "currency": job_data.get("currency", "USD"),
            "issued_date": datetime.now().isoformat(),
            "due_date": self._calculate_due_date(),
            "payment_status": PaymentStatus.PENDING.value,
            "payment_terms": "Net 14 days",
            "notes": work_completed.get("completion_notes", "")
        }
        
        self.invoices.append(invoice)
        
        print(f"✓ Invoice generated: {invoice_number}")
        print(f"  Amount: ${subtotal:.2f}")
        print(f"  Net (after fees): ${net_amount:.2f}")
        
        return invoice
    
    def _calculate_due_date(self, days: int = 14) -> str:
        """Calculate invoice due date."""
        from datetime import timedelta
        due = datetime.now() + timedelta(days=days)
        return due.isoformat()
    
    def submit_invoice(self, invoice: Dict, platform_api: Optional[Dict] = None) -> Dict:
        """
        Submit invoice through platform API.
        
        Args:
            invoice: Invoice to submit
            platform_api: Platform API credentials/config
            
        Returns:
            Submission result
        """
        # In production, this would call actual platform APIs
        # (e.g., Upwork API, Freelancer API, etc.)
        
        submission = {
            "invoice_number": invoice["invoice_number"],
            "platform": invoice["platform"],
            "submitted_at": datetime.now().isoformat(),
            "submission_status": "success",
            "platform_invoice_id": f"platform_{invoice['invoice_number']}",
            "message": "Invoice submitted successfully"
        }
        
        # Update invoice status
        invoice["platform_invoice_id"] = submission["platform_invoice_id"]
        invoice["submitted_at"] = submission["submitted_at"]
        
        print(f"✓ Invoice submitted to {invoice['platform']}: {invoice['invoice_number']}")
        
        return submission
    
    def monitor_payment(self, invoice_number: str) -> Dict:
        """
        Monitor payment status for an invoice.
        
        Args:
            invoice_number: Invoice number to monitor
            
        Returns:
            Payment status information
        """
        # Find invoice
        invoice = next((inv for inv in self.invoices if inv["invoice_number"] == invoice_number), None)
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        # In production, query platform API for payment status
        status = {
            "invoice_number": invoice_number,
            "payment_status": invoice.get("payment_status"),
            "amount_paid": 0,
            "amount_due": invoice["net_amount"],
            "checked_at": datetime.now().isoformat()
        }
        
        return status
    
    def process_payment_received(self, invoice_number: str, payment_data: Dict) -> Dict:
        """
        Process a received payment.
        
        Args:
            invoice_number: Invoice number
            payment_data: Payment information from platform
            
        Returns:
            Payment processing result
        """
        # Find invoice
        invoice = next((inv for inv in self.invoices if inv["invoice_number"] == invoice_number), None)
        
        if not invoice:
            return {"error": "Invoice not found"}
        
        # Extract payment details
        amount = payment_data.get("amount", invoice["net_amount"])
        currency = payment_data.get("currency", invoice["currency"])
        payment_method = payment_data.get("payment_method", "platform_escrow")
        
        # Create payment record
        payment = {
            "payment_id": f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "invoice_number": invoice_number,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "received_at": datetime.now().isoformat(),
            "status": PaymentStatus.PROCESSING.value,
            "treasury_transfer_status": "pending"
        }
        
        self.payments.append(payment)
        
        # Update invoice
        invoice["payment_status"] = PaymentStatus.PROCESSING.value
        invoice["payment_received_at"] = payment["received_at"]
        
        print(f"✓ Payment received: {payment['payment_id']}")
        print(f"  Amount: {amount} {currency}")
        print(f"  Invoice: {invoice_number}")
        
        # Transfer to treasury
        transfer_result = self.transfer_to_treasury(payment)
        
        if transfer_result["success"]:
            payment["status"] = PaymentStatus.COMPLETED.value
            payment["treasury_transfer_status"] = "completed"
            invoice["payment_status"] = PaymentStatus.COMPLETED.value
        
        return {
            "success": True,
            "payment": payment,
            "treasury_transfer": transfer_result
        }
    
    def transfer_to_treasury(self, payment: Dict) -> Dict:
        """
        Transfer payment to Chimera Treasury inflow wallet.
        
        Args:
            payment: Payment information
            
        Returns:
            Transfer result
        """
        # In production, execute actual crypto transfer
        transfer = {
            "transfer_id": f"TXF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "payment_id": payment["payment_id"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "from": "platform_escrow",
            "to": self.treasury_wallet,
            "status": "completed",
            "transaction_hash": f"0x{hash(payment['payment_id']) % (10 ** 64):064x}",
            "transferred_at": datetime.now().isoformat(),
            "success": True
        }
        
        print(f"✓ Transferred to Treasury: {transfer['transfer_id']}")
        print(f"  Amount: {transfer['amount']} {transfer['currency']}")
        print(f"  Wallet: {self.treasury_wallet}")
        print(f"  TX Hash: {transfer['transaction_hash'][:16]}...")
        
        # Log to treasury system
        self._log_to_treasury(transfer)
        
        return transfer
    
    def _log_to_treasury(self, transfer: Dict):
        """
        Log income to Chimera Treasury system.
        
        Args:
            transfer: Transfer information
        """
        # In production, integrate with actual Treasury module
        treasury_log = {
            "source": "freelance_engine",
            "type": "income",
            "amount": transfer["amount"],
            "currency": transfer["currency"],
            "transaction_id": transfer["transfer_id"],
            "timestamp": transfer["transferred_at"]
        }
        
        print(f"  → Logged to Treasury: Freelance income recorded")
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        """
        Convert currency (for crypto payments).
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Conversion result
        """
        # In production, use actual exchange rates API
        # Placeholder exchange rates
        rates = {
            "USD_BTC": 0.000025,
            "USD_ETH": 0.00040,
            "USD_USDT": 1.0,
            "BTC_USD": 40000,
            "ETH_USD": 2500,
            "USDT_USD": 1.0
        }
        
        rate_key = f"{from_currency}_{to_currency}"
        rate = rates.get(rate_key, 1.0)
        
        converted_amount = amount * rate
        
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "converted_amount": converted_amount,
            "target_currency": to_currency,
            "exchange_rate": rate,
            "converted_at": datetime.now().isoformat()
        }
    
    def get_income_summary(self, period: str = "all") -> Dict:
        """
        Get summary of income from freelance work.
        
        Args:
            period: Time period ("all", "month", "week", "day")
            
        Returns:
            Income summary
        """
        completed_payments = [p for p in self.payments if p["status"] == PaymentStatus.COMPLETED.value]
        
        total_earned = sum(p["amount"] for p in completed_payments)
        total_invoices = len(self.invoices)
        paid_invoices = sum(1 for inv in self.invoices if inv["payment_status"] == PaymentStatus.COMPLETED.value)
        pending_invoices = sum(1 for inv in self.invoices if inv["payment_status"] == PaymentStatus.PENDING.value)
        
        return {
            "period": period,
            "total_earned": total_earned,
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "pending_invoices": pending_invoices,
            "payment_rate": (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0,
            "treasury_wallet": self.treasury_wallet,
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def get_pending_payments(self) -> List[Dict]:
        """Get all pending payments."""
        return [inv for inv in self.invoices if inv["payment_status"] == PaymentStatus.PENDING.value]


def create_payment_handler(treasury_wallet: Optional[str] = None) -> PaymentHandler:
    """
    Factory function to create payment handler.
    
    Args:
        treasury_wallet: Treasury wallet address
        
    Returns:
        PaymentHandler instance
    """
    return PaymentHandler(treasury_wallet)
