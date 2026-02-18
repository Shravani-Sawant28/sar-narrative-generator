# SAR Narrative Generator

> **Advanced Anti-Money Laundering (AML) Monitoring & Suspicious Activity Report Generation System**

A full-featured **Streamlit** web application that enables compliance teams to monitor financial transactions, manage customer risk profiles, generate **FinCEN-format Suspicious Activity Reports (SARs)**, and maintain a complete audit trail — all from a sleek, dark-themed admin dashboard.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Dataset Schema](#dataset-schema)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
  - [Authentication & Roles](#authentication--roles)
  - [Admin Dashboard](#admin-dashboard)
  - [User Management](#user-management)
  - [Customer Detail View](#customer-detail-view)
  - [SAR Generation & Editor](#sar-generation--editor)
  - [Audit Logs](#audit-logs)
  - [Shareable Report Links](#shareable-report-links)
- [Configuration](#configuration)
- [Module Reference](#module-reference)

---

## Features

| Area | Capability |
|---|---|
| **Authentication** | Role-based login (Analyst, Supervisor, Compliance Officer) with session management |
| **Admin Dashboard** | KPI metric cards, SAR analytics charts (day/month/year), risk distribution donut, recent flagged transactions |
| **User Management** | Paginated customer registry with search, risk-rating filters, and drill-down detail views |
| **Customer Profiles** | Personal info, financial data (income, credit score), compliance flags (PEP, FATF, FCA), transaction history, transaction pattern visualization, alert history |
| **SAR Generation** | Automated FinCEN-format report generation based on customer transaction patterns |
| **SAR Editor** | Two-stage workflow — Initial Report → AI-assisted edits → Final Report with comparison view |
| **Report Actions** | Save Draft as PDF, Proceed for Review, Escalate to Regulatory SAR, Dismiss Internal SAR |
| **Shareable Links** | Generate unique URLs to share SAR reports across the team |
| **Audit Trail** | Immutable JSON-based event log with filtering, JSON download, and PDF export |
| **Dark Theme** | Professional dark UI with custom CSS, hover animations, and glassmorphism cards |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Streamlit Frontend                 │
│           (app.py — Pages & UI Components)           │
├──────────────┬──────────────────┬────────────────────┤
│  DataManager │  SARGenerator    │    AuditLogger     │
│  (src/)      │  (src/)          │    (src/)          │
├──────────────┴──────────────────┴────────────────────┤
│              CSV Datasets (Datasets/)                │
│   CUSTOMERS_TRAINING · TRANSACTIONS_TRAINING · ALERTS│
├──────────────────────────────────────────────────────┤
│          Persistent Storage (data/)                  │
│      audit_log.json  ·  shared_reports/              │
└──────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| Data Processing | [Pandas](https://pandas.pydata.org/) |
| Visualizations | [Plotly](https://plotly.com/python/) (Express + Graph Objects) |
| PDF Generation | [ReportLab](https://www.reportlab.com/) |
| Language | Python 3.9+ |
| Storage | CSV files (source data), JSON (audit log, shared reports) |

---

## Project Structure

```
Hack-o-Hire/
│
├── app.py                          # Main Streamlit application (all pages & routing)
│
├── src/                            # Core backend modules
│   ├── __init__.py
│   ├── data_manager.py             # Loads CSVs, provides data access & analytics
│   ├── generator.py                # Generates FinCEN-format SAR narratives
│   └── audit.py                    # Immutable JSON audit event logger
│
├── Datasets/                       # Source training data (synthetic)
│   ├── CUSTOMERS_TRAINING.csv      # Customer profiles & KYC data
│   ├── TRANSACTIONS_TRAINING.csv   # Transaction records
│   ├── ALERTS_TRAINING.csv         # AML alert records
│   └── DATA_SCHEMA.json            # Column definitions for all datasets
│
├── data/                           # Runtime persistent storage
│   ├── audit_log.json              # Audit trail entries
│   └── shared_reports/             # JSON files for shareable SAR links
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
│
├── Fincen SAR formata...BEFORE.pdf # Reference SAR template (before edits)
├── Fincen SAR formata...Final.pdf  # Reference SAR template (after edits)
├── extract_pdf.py                  # Utility to extract text from PDF templates
├── str_content.txt                 # Extracted SAR format reference text
├── logo.jpg                        # Application logo
├── pageheader.png                  # Page header image / favicon
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Dataset Schema

All datasets are **fully synthetic** — no real customer data is used.

### CUSTOMERS_TRAINING.csv

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `full_name` | Customer full name |
| `yearly_income` | Annual income |
| `occupation` | Customer's occupation |
| `customer_segment` | Segment classification |
| `country` | Country of residence |
| `account_opened` | Date account was opened |
| `credit_score` | Numerical credit score |
| `is_pep` | Politically Exposed Person flag |
| `kyc_risk_rating` | KYC risk level (LOW / MEDIUM / HIGH) |
| `is_fatf_black` | FATF blacklist country flag |
| `is_fatf_grey` | FATF grey-list country flag |
| `is_fca_high_risk` | FCA high-risk jurisdiction flag |

### TRANSACTIONS_TRAINING.csv

| Column | Description |
|---|---|
| `transaction_id` | Unique transaction identifier |
| `customer_id` | Owning customer |
| `timestamp` | Transaction date/time |
| `amount` | Transaction amount (original currency) |
| `txn_type` | CREDIT / DEBIT |
| `channel` | Transaction channel |
| `sender_id` / `receiver_id` | Counterparties |
| `currency` | Original currency code |
| `country_dest` | Destination country |
| `fx_rate` | Foreign exchange rate applied |
| `amount_gbp` | Amount converted to GBP |
| `is_high_risk_dest` | High-risk destination flag |
| `is_fatf_black_dest` | FATF blacklist destination flag |

### ALERTS_TRAINING.csv

| Column | Description |
|---|---|
| `alert_id` | Unique alert identifier |
| `customer_id` | Associated customer |
| `alert_date` | Date alert was raised |
| `alert_type` | Type of AML alert |
| `severity` | LOW / HIGH / CRITICAL |
| `rule_triggered` | Rule that triggered the alert |
| `sev_numeric` | Numeric severity score |

---

## Getting Started

### Prerequisites

- **Python 3.9+** installed
- **pip** package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Shravani-Sawant28/sar-narrative-generator.git
   cd sar-narrative-generator
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
streamlit run app.py
```

The app will open in your default browser at **http://localhost:8501**.

---

## Usage Guide

### Authentication & Roles

The application uses role-based access. Use the credentials below on the login page:

| Role | Username | Password |
|---|---|---|
| **Analyst** | `analyst` | `analyst123` |
| **Supervisor** | `supervisor` | `super123` |
| **Compliance Officer** | `compliance` | `compliance123` |

> Credentials are also displayed in a collapsible section on the login page for convenience.

### Admin Dashboard

After login, the dashboard provides:

- **KPI Metric Cards** — Total Alerts, Rejected Alerts, Suspicious Alerts, Approved Files
- **SAR Analytics Chart** — Grouped bar chart of SARs Processed vs. Disseminated (toggle Day / Month / Year)
- **Risk Distribution** — Interactive donut chart showing customer risk breakdown (HIGH / MEDIUM / LOW)
- **Recent Flagged Transactions** — Table of the 25 latest high-severity/critical transactions with alert metadata

### User Management

- **Customer Registry** — Paginated list (20 per page) of all customers
- **Sidebar Filters** — Filter by risk rating (HIGH, MEDIUM, LOW)
- **Search** — Search customers by name or ID
- **Drill-Down** — Click **View →** on any customer to open their full profile

### Customer Detail View

A rich profile page displaying:

| Section | Details |
|---|---|
| Profile Header | Name, risk badge, customer ID |
| Personal & Account | Name, country, occupation, account opened date, tenure, customer segment, KYC status |
| Financial Information | Yearly income, credit score (color-coded), total transaction volume |
| Compliance Flags | PEP status, FATF black/grey list, FCA high-risk indicators |
| Transaction History | Filterable table of all transactions with amount, type, channel, destination |
| Transaction Patterns | Interactive chart showing transaction flow aggregated by day/month/year |
| Alert History | AML alerts with severity, type, and rule triggered |
| SAR Generation | **Generate SAR** button to create a FinCEN-format report for the customer |

### SAR Generation & Editor

The SAR workflow follows a **two-stage process**:

1. **Stage 1 — Initial Report**
   - Auto-generated SAR in FinCEN format based on customer profile and transaction analysis
   - Embedded PDF preview of the initial report
   - AI Assistant chat panel for requesting edits

2. **Stage 2 — Final Report**
   - Incorporates analyst edits
   - Side-by-side comparison view (Initial vs. Final)
   - Action buttons:
     - 📄 **Save Draft as PDF**
     - ✅ **Proceed for Review** (marks report as under review)
     - ⚠️ **Escalate to Regulatory SAR**
     - ❌ **Dismiss Internal SAR**
   - 🔗 **Share** — Generates a unique URL to share the report

#### FinCEN SAR Format

The generated report follows the standard FinCEN SAR structure:

| Part | Content |
|---|---|
| Part 1 | Details of Report (date, replacement flag) |
| Part 2 | Details of Principal Officer (bank name, compliance officer) |
| Part 3 | Details of Reporting Branch |
| Part 4 | Individuals Linked to Transactions (subject identification) |
| Part 7 | Details of Suspicious Transaction (reasons, grounds of suspicion, pattern analysis) |
| Part 8 | Details of Action Taken |

### Audit Logs

- **Complete Event Trail** — Every system action is logged (profile views, SAR generation, edits, approvals)
- **Statistics** — Total events, event types, latest event timestamp
- **Filtering** — Filter logs by event type
- **Export** — Download logs as **JSON** or generate a branded **PDF** with the organization logo

### Shareable Report Links

- Reports can be shared via unique URLs (e.g., `?share_id=<uuid>`)
- Shared reports are persisted as JSON in `data/shared_reports/`
- Opening a shared link auto-loads the full report context into the viewer

---

## Configuration

### Streamlit Theme (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#3696FC"
backgroundColor = "#161B2F"
secondaryBackgroundColor = "#3696FC"
textColor = "#FFFFFF"
font = "sans serif"
```

The application also uses extensive custom CSS for metric cards, profile cards, buttons, and dark-mode polishing.

---

## Module Reference

### `src/data_manager.py` — `DataManager`

| Method | Description |
|---|---|
| `_load_csv_data()` | Loads all three CSVs from `Datasets/` and maps columns |
| `get_customer(id)` | Returns a single customer's profile as a dictionary |
| `get_transactions(id)` | Returns all transactions for a customer |
| `get_alerts(id)` | Returns all alerts for a customer |
| `get_all_transactions()` | Returns the complete transactions DataFrame |
| `get_customer_stats()` | Aggregated statistics: risk counts, alert metrics |
| `get_sar_analytics(timeline)` | SAR processed/disseminated data for charts (Day/Month/Year) |

### `src/generator.py` — `SARGenerator`

| Method | Description |
|---|---|
| `generate(customer_data, transactions)` | Produces a FinCEN-format SAR narrative with audit trace. Analyzes credit/debit patterns, identifies structuring/layering typologies. |

### `src/audit.py` — `AuditLogger`

| Method | Description |
|---|---|
| `log_event(event_type, user, details)` | Appends an event to `data/audit_log.json` with timestamp |
| `get_logs()` | Returns all logged events as a list of dictionaries |

---

## License

This project was developed as part of the **Hack-o-Hire** hackathon. All datasets are **fully synthetic** — no real customer data is used.

---

<p align="center">
  <strong>SAR Narrative Generator</strong> · Advanced AML Monitoring System<br/>
  Built with ❤️ using Streamlit & Python
</p>