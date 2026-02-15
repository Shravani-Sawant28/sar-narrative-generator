import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        """Initialize DataManager by loading real CSV data from Datasets folder."""
        self.datasets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Datasets')
        self.customers = None
        self.transactions = None
        self.alerts = None
        self._load_csv_data()

    def _load_csv_data(self):
        """Load all CSV files from the Datasets folder."""
        try:
            # Load customers
            customers_path = os.path.join(self.datasets_path, 'CUSTOMERS_TRAINING.csv')
            customers_df = pd.read_csv(customers_path)
            
            # Map customer columns to expected format - include ALL fields
            self.customers = pd.DataFrame({
                'customer_id': customers_df['customer_id'],
                'name': customers_df['full_name'],
                'risk_rating': customers_df['kyc_risk_rating'].str.upper(),  # LOW, MEDIUM, HIGH
                'occupation': customers_df['occupation'],
                'kyc_status': 'Verified',  # All customers in training data are verified
                'tenure_years': self._calculate_tenure(customers_df['account_opened']),
                'account_opened': customers_df['account_opened'],
                'yearly_income': customers_df['yearly_income'],
                'customer_segment': customers_df['customer_segment'],
                'country': customers_df['country'],
                'credit_score': customers_df['credit_score'],
                'is_pep': customers_df['is_pep'],
                'is_fatf_black': customers_df['is_fatf_black'],
                'is_fatf_grey': customers_df['is_fatf_grey'],
                'is_fca_high_risk': customers_df['is_fca_high_risk']
            })
            
            # Load transactions
            transactions_path = os.path.join(self.datasets_path, 'TRANSACTIONS_TRAINING.csv')
            transactions_df = pd.read_csv(transactions_path)
            
            # Map transaction columns to expected format
            self.transactions = pd.DataFrame({
                'transaction_id': transactions_df['transaction_id'],
                'customer_id': transactions_df['customer_id'],
                'date': pd.to_datetime(transactions_df['timestamp']).dt.strftime('%Y-%m-%d'),
                'type': transactions_df['txn_type'].str.title(),  # CREDIT -> Credit, DEBIT -> Debit
                'channel': transactions_df['channel'],
                'amount': transactions_df['amount'],
                'counterparty': transactions_df['receiver_id'],  # Using receiver_id as counterparty
                'description': transactions_df['channel'] + ' - ' + transactions_df['txn_type'],
                'currency': transactions_df['currency'],
                'country_dest': transactions_df['country_dest'],
                'amount_gbp': transactions_df['amount_gbp']
            })
            
            # Load alerts
            alerts_path = os.path.join(self.datasets_path, 'ALERTS_TRAINING.csv')
            self.alerts = pd.read_csv(alerts_path)
            self.alerts['alert_date'] = pd.to_datetime(self.alerts['alert_date'])
            
            print(f"✓ Loaded {len(self.customers)} customers")
            print(f"✓ Loaded {len(self.transactions)} transactions")
            print(f"✓ Loaded {len(self.alerts)} alerts")
            
        except FileNotFoundError as e:
            print(f"Error: Could not find CSV file - {e}")
            # Initialize empty DataFrames as fallback
            self.customers = pd.DataFrame()
            self.transactions = pd.DataFrame()
            self.alerts = pd.DataFrame()
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            self.customers = pd.DataFrame()
            self.transactions = pd.DataFrame()
            self.alerts = pd.DataFrame()

    def _calculate_tenure(self, account_opened_series):
        """Calculate tenure in years from account_opened date."""
        try:
            account_dates = pd.to_datetime(account_opened_series)
            current_date = datetime.now()
            tenure_days = (current_date - account_dates).dt.days
            return (tenure_days / 365).round().astype(int)
        except:
            return pd.Series([0] * len(account_opened_series))

    def get_customer(self, customer_id):
        """Get customer details by customer_id."""
        if self.customers is None or self.customers.empty:
            return None
        
        customer = self.customers[self.customers['customer_id'] == customer_id]
        if not customer.empty:
            return customer.iloc[0].to_dict()
        return None

    def get_transactions(self, customer_id):
        """Get all transactions for a specific customer."""
        if self.transactions is None or self.transactions.empty:
            return pd.DataFrame()
        
        return self.transactions[self.transactions['customer_id'] == customer_id]

    def get_alerts(self, customer_id):
        """Get all alerts for a specific customer."""
        if self.alerts is None or self.alerts.empty:
            return pd.DataFrame()
        
        return self.alerts[self.alerts['customer_id'] == customer_id]

    def get_all_transactions(self):
        """Returns all transactions for analytics."""
        return self.transactions if self.transactions is not None else pd.DataFrame()

    def get_customer_stats(self):
        """Returns aggregated customer statistics."""
        if self.customers is None or self.customers.empty:
            return {
                "total_customers": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "risk_distribution": {},
                "total_alerts": 0,
                "rejected_alerts": 0,
                "suspicious_alerts": 0,
                "approved_files": 0
            }
        
        # Calculate alert statistics
        total_alerts = len(self.alerts) if self.alerts is not None else 0
        high_severity_alerts = len(self.alerts[self.alerts['severity'] == 'HIGH']) if self.alerts is not None and not self.alerts.empty else 0
        critical_alerts = len(self.alerts[self.alerts['severity'] == 'CRITICAL']) if self.alerts is not None and not self.alerts.empty else 0
        
        return {
            "total_customers": len(self.customers),
            "high_risk_count": len(self.customers[self.customers['risk_rating'] == 'HIGH']),
            "medium_risk_count": len(self.customers[self.customers['risk_rating'] == 'MEDIUM']),
            "low_risk_count": len(self.customers[self.customers['risk_rating'] == 'LOW']),
            "risk_distribution": self.customers['risk_rating'].value_counts().to_dict(),
            # Alert Metrics from real data
            "total_alerts": total_alerts,
            "rejected_alerts": len(self.alerts[self.alerts['severity'] == 'LOW']) if self.alerts is not None and not self.alerts.empty else 0,
            "suspicious_alerts": high_severity_alerts + critical_alerts,
            "approved_files": len(self.alerts[self.alerts['severity'].isin(['HIGH', 'CRITICAL'])]) if self.alerts is not None and not self.alerts.empty else 0
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

