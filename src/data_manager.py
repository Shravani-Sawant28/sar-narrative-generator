import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

class DataManager:
    def __init__(self):
        # Ensure deterministic data generation
        Faker.seed(42)
        random.seed(42)
        self.customers = self._generate_mock_customers()
        self.transactions = self._generate_mock_transactions()

    def _generate_mock_customers(self, count=5):
        customers = []
        # specific hardcoded customer for the demo scenario
        customers.append({
            "customer_id": "CUST-998877",
            "name": "Rajesh Kumar",
            "risk_rating": "High",
            "occupation": "Import/Export Trader",
            "kyc_status": "Verified",
            "tenure_years": 4
        })
        
        for _ in range(count - 1):
            customers.append({
                "customer_id": f"CUST-{random.randint(10000, 99999)}",
                "name": fake.name(),
                "risk_rating": random.choice(["Low", "Medium", "High"]),
                "occupation": fake.job(),
                "kyc_status": "Verified",
                "tenure_years": random.randint(1, 15)
            })
        return pd.DataFrame(customers)

    def _generate_mock_transactions(self):
        # Scenario: 50 Lakhs from 47 accounts in one week, then transfer abroad
        transactions = []
        # Fixed base date for static data
        base_date = datetime(2025, 2, 1)
        
        # Incoming structuring
        for i in range(47):
            amount = round(random.uniform(90000, 110000), 2) # ~1 Lakh each
            transactions.append({
                "transaction_id": f"TXN-{random.randint(100000, 999999)}",
                "customer_id": "CUST-998877",
                "date": (base_date + timedelta(days=random.randint(0, 4))).strftime("%Y-%m-%d"),
                "type": "Credit",
                "amount": amount,
                "counterparty": fake.name(),
                "description": "Domestic Transfer",
            })
            
        # Outgoing massive transfer
        transactions.append({
            "transaction_id": f"TXN-INT-{random.randint(100000, 999999)}",
            "customer_id": "CUST-998877",
            "date": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "type": "Debit",
            "amount": 4800000.00,
            "counterparty": "Offshore Holdings Ltd (Cayman)",
            "description": "International Wire Transfer",
        })
        
        return pd.DataFrame(transactions)

    def get_customer(self, customer_id):
        customer = self.customers[self.customers['customer_id'] == customer_id]
        if not customer.empty:
            return customer.iloc[0].to_dict()
        return None

    def get_transactions(self, customer_id):
        return self.transactions[self.transactions['customer_id'] == customer_id]

    def get_all_transactions(self):
        """Returns all transactions for analytics."""
        return self.transactions

    def get_customer_stats(self):
        """Returns aggregated customer statistics."""
        return {
            "total_customers": len(self.customers),
            "high_risk_count": len(self.customers[self.customers['risk_rating'] == 'High']),
            "medium_risk_count": len(self.customers[self.customers['risk_rating'] == 'Medium']),
            "low_risk_count": len(self.customers[self.customers['risk_rating'] == 'Low']),
            "risk_distribution": self.customers['risk_rating'].value_counts().to_dict(),
            # New Metrics
            "total_alerts": 245,
            "rejected_alerts": 12,
            "suspicious_alerts": len(self.customers[self.customers['risk_rating'] == 'High']), # Same as high risk subjects
            "approved_files": 180
        }
    
    def get_sar_analytics(self, timeline='Month-wise'):
        """Returns SAR analytics data for processed and disseminated SARs."""
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate mock SAR data based on timeline
        if timeline == "Day-wise":
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            # SAR Processed: higher counts
            sar_processed = np.random.randint(3, 12, size=30)
            # SAR Disseminated: slightly lower (some are still in process)
            sar_disseminated = [max(0, processed - np.random.randint(0, 3)) for processed in sar_processed]
        elif timeline == "Month-wise":
            dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
            sar_processed = np.random.randint(25, 85, size=12)
            sar_disseminated = [max(0, processed - np.random.randint(5, 15)) for processed in sar_processed]
        else:  # Year-wise
            dates = pd.date_range(end=datetime.now(), periods=5, freq='Y')
            sar_processed = np.random.randint(200, 600, size=5)
            sar_disseminated = [max(0, processed - np.random.randint(20, 80)) for processed in sar_processed]
        
        return pd.DataFrame({
            'date': dates,
            'sar_processed': sar_processed,
            'sar_disseminated': sar_disseminated
        })

