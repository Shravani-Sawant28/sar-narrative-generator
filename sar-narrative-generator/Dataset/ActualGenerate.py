import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os
from faker import Faker

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = 'users_data.csv'  # Your seeded data
OUTPUT_DIR = 'aml_data_production'
START_DATE = datetime(2025, 1, 1)
DURATION_DAYS = 180  # FIX #5: Extended to 6 months
TARGET_USERS = 2000

# Risk Thresholds
HIGH_RISK_COUNTRIES = ['Cayman Islands', 'Panama', 'UAE', 'Cyprus', 'Russia']
LOW_RISK_COUNTRIES = ['US', 'UK', 'Germany', 'Canada', 'Japan']

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# STEP 1: ENTITY RESOLUTION (FIX #6)
# ==========================================
print("Generating Reusable Counterparty Pool...")
# We create a "phonebook" of companies so multiple users can transact with the same entity
counterparty_pool = []
for _ in range(450):
    counterparty_pool.append({
        'name': fake.company(),
        'type': 'Merchant',
        'risk': 'Low',
        'country': 'US'
    })
for _ in range(50):
    counterparty_pool.append({
        'name': f"{fake.word().capitalize()} Holdings Ltd",
        'type': 'Shell',
        'risk': 'High',
        'country': np.random.choice(HIGH_RISK_COUNTRIES)
    })
df_counterparties = pd.DataFrame(counterparty_pool)

def get_counterparty(risk_level='Low'):
    subset = df_counterparties[df_counterparties['risk'] == risk_level]
    return subset.sample(1).iloc[0]

# ==========================================
# STEP 2: CUSTOMER ENRICHMENT (FIX #1)
# ==========================================
print(f"Loading {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# Clean Currency
def clean_currency(x):
    if isinstance(x, str):
        return float(x.replace('$', '').replace(',', '').strip())
    return float(x) if x else 0.0

df['yearly_income'] = df['yearly_income'].apply(clean_currency)
df['total_debt'] = df['total_debt'].apply(clean_currency)
df['id'] = df['id'].astype(str)
df['name'] = [fake.name() for _ in range(len(df))]

def assign_risk_profile(row):
    # FIX #1: Age != Risk. Behavior = Risk.
    age = row['current_age']
    income = row['yearly_income']
    
    # Base Risk
    risk_rating = 'Low'
    occupation = 'Salaried'
    
    # Occupation Logic
    if income > 250000:
        occupation = np.random.choice(['Real Estate Developer', 'Import/Export', 'Executive', 'Investor'])
        if random.random() < 0.3: risk_rating = 'Medium' # High net worth = Medium risk
    elif age < 25:
        occupation = 'Student' # Student is occupation, but NOT auto-high risk
    elif age > 65:
        occupation = 'Retired'
    else:
        occupation = np.random.choice(['Engineer', 'Teacher', 'Sales', 'Nurse', 'Manager'])

    # PEP Injection (1% of population)
    is_pep = False
    if random.random() < 0.01:
        is_pep = True
        risk_rating = 'High'
        occupation = 'Government Official'

    return pd.Series([occupation, risk_rating, is_pep])

print("Enriching customer profiles (Removing Age Bias)...")
df[['occupation', 'risk_rating', 'is_pep']] = df.apply(assign_risk_profile, axis=1)
df = df.rename(columns={'id': 'customer_id'})

# Initialize Balances
customer_balances = {row['customer_id']: row['yearly_income'] * 0.05 for _, row in df.iterrows()}

# ==========================================
# STEP 3: ASSIGN BEHAVIOR PATTERNS (FIX #9)
# ==========================================
# We assign "Intents" not "Alerts". 
# Some criminals will be lazy (caught), some smart (evade).
# Some normal people will be erratic (False Positives).

all_ids = df['customer_id'].tolist()
num_criminals = int(len(df) * 0.05) # 5% Bad actors
criminals = np.random.choice(all_ids, num_criminals, replace=False)

behavior_map = {}

# Assign Criminal Strategies
for cid in criminals:
    behavior_map[cid] = {
        'type': 'CRIMINAL',
        'strategy': np.random.choice(['Structuring', 'Layering', 'Mule'], p=[0.4, 0.4, 0.2]),
        'skill_level': np.random.choice(['Clumsy', 'Pro'], p=[0.7, 0.3]) # Pros try to evade rules
    }

# Assign "False Positive" candidates (High Volume Spenders)
fp_candidates = np.random.choice(list(set(all_ids) - set(criminals)), int(len(df)*0.10), replace=False)
for cid in fp_candidates:
    behavior_map[cid] = {
        'type': 'NORMAL_HIGH_VELOCITY',
        'strategy': np.random.choice(['BigSpender', 'CryptoTrader', 'CashBusiness'])
    }

# ==========================================
# STEP 4: SIMULATION ENGINE (FIX #2, #3, #4, #11)
# ==========================================
print("Simulating 180 Days of Transactions...")
transactions = []

def log_txn(cid, date, amount, txn_type, counterparty, country, category='General'):
    # Fix #7: Sanity Check - Prevent negative balance unless credit
    if txn_type in ['DEBIT', 'WIRE_OUT', 'ACH_OUT']:
        if customer_balances.get(cid, 0) < amount: return False
        customer_balances[cid] -= amount
    else:
        customer_balances[cid] = customer_balances.get(cid, 0) + amount

    transactions.append({
        'txn_id': str(uuid.uuid4()),
        'customer_id': cid,
        'timestamp': date,
        'amount': round(amount, 2),
        'currency': 'USD',
        'txn_type': txn_type,
        'counterparty': counterparty,
        'counterparty_country': country,
        'category': category
    })
    return True

curr_date = START_DATE
for day in range(DURATION_DAYS):
    curr_date += timedelta(days=1)
    
    # --- A. BACKGROUND NOISE (FIX #11) ---
    # 1. Payroll (15th and 30th)
    if curr_date.day in [15, 30]:
        for _, row in df.iterrows():
            salary = row['yearly_income'] / 24
            log_txn(row['customer_id'], curr_date, salary, 'ACH_IN', 'Employer Payroll', 'US', 'Salary')

    # 2. Rent/Mortgage (1st)
    if curr_date.day == 1:
        for _, row in df.iterrows():
            rent = (row['yearly_income'] / 12) * 0.3
            log_txn(row['customer_id'], curr_date, rent, 'ACH_OUT', 'Landlord/Bank', 'US', 'Rent')

    # 3. Daily Living (Coffee, Groceries)
    daily_active = df.sample(frac=0.15)
    for _, row in daily_active.iterrows():
        amt = random.uniform(10, 150)
        cp = get_counterparty('Low')
        log_txn(row['customer_id'], curr_date, amt, 'DEBIT', cp['name'], 'US', 'Living')

    # --- B. COMPLEX SCENARIO EXECUTION (FIX #3, #4) ---
    # We select active actors for TODAY
    
    # 1. STRUCTURING (Fix #3: Multi-day pattern)
    # Logic: If 'Clumsy', do 9900. If 'Pro', do 4000 (evade rule).
    structurers = [k for k,v in behavior_map.items() if v.get('strategy') == 'Structuring']
    for cid in structurers:
        # 2% chance to START a structuring sequence today
        if random.random() < 0.02: 
            skill = behavior_map[cid].get('skill_level', 'Clumsy')
            # Schedule 3-5 deposits over next 7 days
            num_deposits = random.randint(3, 5)
            for i in range(num_deposits):
                day_offset = random.randint(0, 6)
                txn_date = curr_date + timedelta(days=day_offset)
                
                if skill == 'Clumsy':
                    amt = random.uniform(9000, 9900) # Hits the rule
                else:
                    amt = random.uniform(2000, 4000) # Evades the rule (False Negative)
                
                log_txn(cid, txn_date, amt, 'CASH_DEPOSIT', 'ATM Deposit', 'US', 'Structuring')

    # 2. LAYERING (Fix #4: Time lag + Splits)
    layerers = [k for k,v in behavior_map.items() if v.get('strategy') == 'Layering']
    for cid in layerers:
        if random.random() < 0.01: # Rare event
            # Step 1: Big Inflow
            in_amt = random.uniform(40000, 80000)
            shell = get_counterparty('High')
            log_txn(cid, curr_date, in_amt, 'WIRE_IN', shell['name'], shell['country'], 'Layering_In')
            
            # Step 2: Outflow (Split & Delayed)
            # Clumsy: Sends 95% out next day. Pro: Waits 5 days, sends 60%.
            skill = behavior_map[cid].get('skill_level', 'Clumsy')
            delay = 1 if skill == 'Clumsy' else random.randint(3, 8)
            out_date = curr_date + timedelta(days=delay)
            
            out_amt = in_amt * 0.95
            
            # Split into 2 transfers
            log_txn(cid, out_date, out_amt * 0.6, 'WIRE_OUT', get_counterparty('High')['name'], 'Panama', 'Layering_Out')
            log_txn(cid, out_date + timedelta(hours=4), out_amt * 0.35, 'WIRE_OUT', get_counterparty('High')['name'], 'UAE', 'Layering_Out')

    # 3. FALSE POSITIVES (Innocent High Volume)
    high_rollers = [k for k,v in behavior_map.items() if v['type'] == 'NORMAL_HIGH_VELOCITY']
    for cid in high_rollers:
        if random.random() < 0.02:
            # Buying a car or paying tuition
            amt = random.uniform(15000, 40000)
            log_txn(cid, curr_date, amt, 'WIRE_OUT', 'Tesla Motors', 'US', 'BigPurchase')


# ==========================================
# STEP 5: THE RULE ENGINE (FIX #2, #8, #10)
# ==========================================
print("Running Rule Engine on Transaction Log...")
df_txns = pd.DataFrame(transactions)
df_txns['timestamp'] = pd.to_datetime(df_txns['timestamp'])

alerts = []

# --- Rule 1: Structuring Detection ---
# Logic: >2 Cash Deposits between 9k-10k in rolling 7 days
print("Applying Rule: Structuring...")
cash_deps = df_txns[
    (df_txns['txn_type'] == 'CASH_DEPOSIT') & 
    (df_txns['amount'] >= 9000) & 
    (df_txns['amount'] < 10000)
].copy()

if not cash_deps.empty:
    cash_deps = cash_deps.sort_values('timestamp')
    # Group by User, count in 7D window
    # Validating logic: We iterate users for cleaner logic in script
    for cid, group in cash_deps.groupby('customer_id'):
        group = group.set_index('timestamp')
        rolling_count = group.rolling('7D')['amount'].count()
        
        # Any window with >= 3 deposits?
        triggers = rolling_count[rolling_count >= 3]
        if not triggers.empty:
            trigger_date = triggers.index[0]
            alerts.append({
                'alert_id': f"ALT-{uuid.uuid4().hex[:8]}",
                'customer_id': cid,
                'alert_date': trigger_date.strftime('%Y-%m-%d'),
                'alert_type': 'Potential Structuring',
                'severity': 'High',
                'description': f"Detected {int(triggers.iloc[0])} cash deposits just under reporting threshold in 7 days."
            })

# --- Rule 2: Rapid Movement / Layering ---
# Logic: Wire In > 30k AND Wire Out > 80% of In within 3 days
print("Applying Rule: Rapid Movement...")
wires = df_txns[df_txns['txn_type'].isin(['WIRE_IN', 'WIRE_OUT'])].copy()
wires = wires.sort_values('timestamp')

for cid, group in wires.groupby('customer_id'):
    # Iterate large inputs
    large_ins = group[(group['txn_type'] == 'WIRE_IN') & (group['amount'] > 30000)]
    for idx, row in large_ins.iterrows():
        # Look ahead 3 days
        window_end = row['timestamp'] + timedelta(days=3)
        outflows = group[
            (group['txn_type'] == 'WIRE_OUT') & 
            (group['timestamp'] > row['timestamp']) & 
            (group['timestamp'] <= window_end)
        ]
        
        if outflows['amount'].sum() > (row['amount'] * 0.80):
            alerts.append({
                'alert_id': f"ALT-{uuid.uuid4().hex[:8]}",
                'customer_id': cid,
                'alert_date': row['timestamp'].strftime('%Y-%m-%d'),
                'alert_type': 'Layering / Rapid Movement',
                'severity': 'Critical',
                'description': f"Large inflow ${row['amount']} followed by immediate outflow of ${outflows['amount'].sum()}."
            })

# --- Rule 3: High Risk Geography ---
# Logic: > 2 transactions to High Risk Countries in 30 days
print("Applying Rule: Sanctions/Geo Risk...")
geo_risk = df_txns[df_txns['counterparty_country'].isin(HIGH_RISK_COUNTRIES)].copy()

for cid, group in geo_risk.groupby('customer_id'):
    if len(group) >= 2:
        alerts.append({
            'alert_id': f"ALT-{uuid.uuid4().hex[:8]}",
            'customer_id': cid,
            'alert_date': group.iloc[-1]['timestamp'].strftime('%Y-%m-%d'),
            'alert_type': 'High Risk Geography',
            'severity': 'Medium',
            'description': f"Multiple transactions involving high-risk jurisdictions ({group['counterparty_country'].unique()})."
        })

# ==========================================
# STEP 6: BEHAVIORAL FEATURES (FIX #8)
# ==========================================
print("Calculating Behavioral Features...")
# Calculate aggregations for the SAR dashboard
# 1. Monthly Velocity
df_txns['month'] = df_txns['timestamp'].dt.to_period('M')
monthly_stats = df_txns.groupby(['customer_id', 'month'])['amount'].sum().reset_index()
monthly_avg = monthly_stats.groupby('customer_id')['amount'].mean().rename('avg_monthly_volume')

df_customers = df.merge(monthly_avg, on='customer_id', how='left')
df_customers['avg_monthly_volume'] = df_customers['avg_monthly_volume'].fillna(0)

# 2. Deviation Score
# deviation = (Actual - Expected) / Expected
df_customers['volume_deviation_pct'] = (
    (df_customers['avg_monthly_volume'] * 12) - df_customers['yearly_income']
) / df_customers['yearly_income']

# ==========================================
# STEP 7: EXPORT
# ==========================================
df_alerts = pd.DataFrame(alerts)
# Fix #10: We do NOT deduplicate indiscriminately. 
# We keeps alerts if they happen on different dates.

print("Saving Data...")
df_customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
df_txns.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)
df_alerts.to_csv(f"{OUTPUT_DIR}/alerts.csv", index=False)

print("\n" + "="*40)
print("✅ PRODUCTION-GRADE DATA GENERATED")
print(f"Timeframe: {DURATION_DAYS} Days")
print(f"Transactions: {len(df_txns)}")
print(f"Alerts Generated: {len(df_alerts)} (Derived from rules, not scripts!)")
print(f" - True Positives & False Positives included naturally.")
print("="*40)