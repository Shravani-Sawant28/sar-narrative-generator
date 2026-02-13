import pandas as pd
from datetime import datetime

class SARGenerator:
    def __init__(self):
        pass

    def generate(self, customer_data, transactions):
        """
        Generates a Suspicious Transaction Report (STR) based on FIU-IND format.
        Returns a dictionary with 'narrative_text' (the report) and 'audit_trace'.
        """
        
        # 1. Analyze Patterns (Mock Logic)
        total_credit = transactions[transactions['type'] == 'Credit']['amount'].sum()
        total_debit = transactions[transactions['type'] == 'Debit']['amount'].sum()
        
        credits = transactions[transactions['type'] == 'Credit']
        debits = transactions[transactions['type'] == 'Debit']
        
        high_value_credits = credits[credits['amount'] > 50000]
        international_debits = debits[debits['description'].str.contains('International', case=False, na=False)]
        
        audit_trace = []
        report_parts = []
        
        # --- PART 1: DETAILS OF REPORT ---
        report_parts.append("SUSPICIOUS TRANSACTION REPORT (STR) - FIU-IND FORMAT")
        report_parts.append("="*60)
        report_parts.append("PART 1: DETAILS OF REPORT")
        report_parts.append(f"1.1 Date of sending report: {datetime.now().strftime('%d/%m/%Y')}")
        report_parts.append("1.2 Replacement to earlier report? NO")
        report_parts.append("-" * 60)
        
        audit_trace.append({"step": "Report Initialization", "source": "System Date", "reasoning": "Standard STR Header extraction."})

        # --- PART 2: DETAILS OF PRINCIPAL OFFICER ---
        report_parts.append("PART 2: DETAILS OF PRINCIPAL OFFICER")
        report_parts.append("2.1 Name of Bank: HACK-O-HIRE BANK LTD") # Mock Bank Name
        report_parts.append("2.5 Principal Officer: Mr. Ankit Sharma") # Mock PO
        report_parts.append("2.6 Designation: Chief Compliance Officer")
        report_parts.append("2.15 E-mail: compliance@hackohire.bank")
        report_parts.append("-" * 60)

         # --- PART 3: DETAILS OF REPORTING BRANCH ---
        report_parts.append("PART 3: DETAILS OF REPORTING BRANCH")
        report_parts.append("3.1 Name of Branch: Main Branch, Mumbai") 
        report_parts.append("3.2 BSR Code: 1234567")
        report_parts.append("-" * 60)
        
        # --- PART 4: DETAILS OF INDIVIDUALS LINKED TO TRANSACTIONS ---
        report_parts.append("PART 4: LIST OF INDIVIDUALS LINKED TO TRANSACTIONS")
        report_parts.append(f"Name: {customer_data.get('name', 'Unknown')}")
        report_parts.append(f"Customer ID: {customer_data.get('customer_id', 'N/A')}")
        report_parts.append(f"Occupation: {customer_data.get('occupation', 'N/A')}")
        report_parts.append(f"Risk Rating: {customer_data.get('risk_rating', 'N/A')}")
        report_parts.append("-" * 60)
        
        audit_trace.append({"step": "Subject Identification", "source": "Customer Profile", "reasoning": "Extracted subject details for Part 4."})

        # --- PART 6: DETAILS OF ACCOUNTS IS IMPLIED, BUT WE FOCUS ON TRANSACTIONS ---
        
        # --- PART 7: DETAILS OF SUSPICIOUS TRANSACTION ---
        report_parts.append("PART 7: DETAILS OF SUSPICIOUS TRANSACTION")
        
        report_parts.append("7.1 Reasons for suspicion:")
        suspicion_reasons = []
        if not international_debits.empty:
            suspicion_reasons.append("- Value inconsistent with client's apparent financial standing")
            suspicion_reasons.append("- Unusual or unjustified complexity")
            suspicion_reasons.append("- Appears to have no economic rationale")
        else:
            suspicion_reasons.append("- Unexplained transfers between multiple accounts")
            
        for reason in suspicion_reasons:
            report_parts.append(reason)
            
        report_parts.append("\n7.2 Grounds of Suspicion (Summary):")
        
        intro = (f"The account held by {customer_data.get('name')} ({customer_data.get('customer_id')}) "
                 f"shows activity inconsistent with the declared profile of '{customer_data.get('occupation')}'.")
        report_parts.append(intro)
        
        if not international_debits.empty and not credits.empty:
            structuring_text = (f"Analysis reveals a pattern of 'structuring' or 'layering'. "
                                f"Specifically, {len(credits)} domestic credit transactions totaling INR {total_credit:,.2f} "
                                f"were received in a short period. Shortly thereafter, "
                                f"funds totaling INR {float(international_debits.iloc[0]['amount']):,.2f} were transferred internationally "
                                f"to {international_debits.iloc[0]['counterparty']}. "
                                f"The rapid accumulation and immediate dissipation of funds to an offshore entity suggests an attempt to obscure the origin of funds.")
            report_parts.append(structuring_text)
            
            audit_trace.append({
                "step": "Transaction Analysis", 
                "source": "Transaction Logs", 
                "reasoning": f"Identified pattern: Small credits -> Large Int'l Debit. Matches ML typology 'Layering'."
            })
        else:
            report_parts.append("Unusual transaction volume detected relative to historical average.")

        report_parts.append("-" * 60)
        
        # --- PART 8: DETAILS OF ACTION TAKEN ---
        report_parts.append("PART 8: DETAILS OF ACTION TAKEN")
        report_parts.append("8.1 Action Taken: Account frozen, internal investigation initiated.")
        report_parts.append("-" * 60)
        
        audit_trace.append({"step": "Conclusion", "source": "System Logic", "reasoning": "Generated standard action taken based on high-risk flag."})
        
        return {
            "narrative_text": "\n".join(report_parts),
            "audit_trace": audit_trace
        }
