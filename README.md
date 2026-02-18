# NeuralLedger: Automated SAR Narrative Generator

**NeuralLedger** is an intelligent, end-to-end framework designed to modernize Anti-Money Laundering (AML) compliance by automating the creation of **Suspicious Activity Reports (SAR)**. Developed for the **Barclays Hack-O-Hire** , this system integrates Machine Learning (ML) triage with a **Retrieval-Augmented Generation (RAG)** architecture to transform manual, time-consuming compliance processes into a scalable, technology-driven workflow.

---

## ## Features

| Area | Capability |
| --- | --- |
| **Smart Classification** | Dual-layer engine combining rule-based validation and ML-driven risk scoring (XGBoost, Isolation Forest).

 |
| **SAR Generation** | Automated FinCEN-format report generation using RAG to ensure regulatory alignment.

 |
| **Hallucination Control** | Cross-checks AI-written numbers against actual database records to prevent "faked" data.

 |
| **Deduplication** | Time-window and event-matching rules to link related alerts to existing SARs instead of filing redundant ones.

 |
| **Audit & Transparency** | "Glass Box" approach providing transaction-level evidence and regulatory citations for every claim.

 |
| **Immutable Logs** | "Write Once, Read Many" (WORM) storage policy ensures audit trails cannot be altered.

 |

---

## ## Architecture

NeuralLedger is built on a cloud-native AWS stack, ensuring modularity, scalability, and banking-grade security.

### ### Core Components

* 
**Orchestration**: **AWS Step Functions** manages the investigation lifecycle and coordinates automated tasks from data fetching to AI generation.


* 
**Processing Layer**: **AWS Lambda** executes modular business logic for Data Enrichment, Rule-Based Triage, and PII Redaction.


* 
**Generative AI**: **Amazon Bedrock** provides private, secure API access to **Claude 3.5 Sonnet** and **Llama 3.1 70B** for high-fidelity narrative generation.


* **Storage & Vector DB**:
* 
**Amazon RDS**: Securely manages customer profiles and active transaction data.


* 
**Amazon S3**: Acts as the secure vault for raw evidence and final reports using Object Lock technology.


* 
**Amazon OpenSearch**: Stores fraud detection rules and regulatory embeddings to provide relevant context to the AI model.





---

## ## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Streamlit 

 |
| **Data Processing** | Pandas, NumPy 

 |
| **Machine Learning** | XGBoost, Isolation Forest 

 |
| **AI / LLM** | Amazon Bedrock, Claude 3.5 Sonnet, Llama 3.1 70B 

 |
| **Orchestration** | AWS Step Functions, AWS Lambda 

 |
| **Database/Storage** | Amazon RDS, Amazon S3, Amazon OpenSearch 

 |

---

## ## System Performance

The system demonstrates high predictive power and efficiency based on validation against ground truth data:

* 
**Recall**: **91.2%** — Successfully identifies the vast majority of suspicious actors.


* 
**Precision**: **87.4%** — Nearly 9 out of 10 filed SARs are legitimate hits.


* 
**False Positive Rate**: **0.52%** — Minimizes manual overhead and maintains customer trust.


* 
**ROC AUC**: **0.9734**.


* 
**Time Savings**: Reduced investigative time from 3–6 hours down to **1–2 hours**.



---

## ## Security & Compliance

* 
**PII Redaction**: All customer names are replaced with anonymous tokens before processing to ensure the LLM never sees real client data.


* 
**Data Encryption**: All data is encrypted at rest using **AWS KMS**.


* 
**Access Control**: Role-Based Access Control (RBAC) ensures analysts can only view and edit, while supervisors approve and file.


* 
**Network Isolation**: Databases and AI models are deployed inside a private isolated VPC, unreachable by external attackers.



---

## ## Getting Started

### ### Prerequisites

* AWS Account with access to Bedrock, Lambda, and RDS.
* Python 3.9+
* Streamlit

### ### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Shravani-Sawant28/sar-narrative-generator.git
cd sar-narrative-generator

```


2. **Install dependencies**:
```bash
pip install -r requirements.txt

```


3. **Run the application**:
```bash
streamlit run app.py

```



---

## ## Project Structure

```text
Hack-o-Hire/
├── app.py              # Main Streamlit application
├── src/                # Backend modules (data_manager, generator, audit)
├── Datasets/           # Synthetic CSV datasets (Customers, Transactions, Alerts)
├── data/               # Persistent storage (Audit logs, shared reports)
└── README.md           # Project documentation

```

---

## ## License

This project was developed for the **Barclays Hack-o-Hire** hackathon. All datasets used are **fully synthetic**; no real customer data is included.

---

**NeuralLedger** · Advanced AML Monitoring System
Built with ❤️ using Streamlit, AWS, and Python.

Would you like me to help you generate a `requirements.txt` file or more specific documentation for the `src/` modules?
