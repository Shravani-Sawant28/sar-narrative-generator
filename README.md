# NeuralLedger
### AI-Powered SAR Narrative Generator with Audit Trail

NeuralLedger is an end-to-end intelligent compliance system that automates Suspicious Activity Report (SAR) generation using:

1. Machine Learning (alert triage)

2. Retrieval-Augmented Generation (RAG)

3. Explainable AI with citations

4. Human-in-the-loop validation

It transforms SAR workflows from manual, slow, and error-prone → automated, scalable, and audit-ready.

### Challenges of traditonal SAR systems

Financial institutions today struggle with:

1. 90%+ false positive alerts

2. SAR creation taking 2–6 hours per case

3. Analyst fatigue → risk of missing real fraud

4. Fragmented data across systems

5. Duplicate SAR filings for same customer

6. Lack of explainability in AI outputs

### Our Solution

NeuralLedger introduces a smart compliance pipeline:

1. ML models classify alerts (False vs Genuine)

2. RAG retrieves regulatory + transaction context

3. LLM generates structured SAR narratives

4. Deduplication engine avoids redundant filings

5. Validation layer prevents hallucinations

6. Analysts review before final submission


### Architecture Overview

1. Processing Layer → Enrichment, Triage, PII Redaction

2. AI Layer → Claude (via Amazon Bedrock)

3. Vector DB → OpenSearch

4. Storage → AWS RDS + S3 (WORM enabled)

5. APIs → FastAPI + API Gateway

6. Queue System → AWS SQS

### Architecture Diagram

<img width="400" height="300" alt="Screenshot 2026-02-23 092906" src="https://github.com/user-attachments/assets/9632dbbc-d382-45f0-be95-76ac603f804f" />


### Tech Stack
1. ML Models	Isolation Forest, XGBoost
2. LLM	Claude (Amazon Bedrock)
3. Backend	FastAPI
4. Frontend	Streamlit
5. Vector DB	OpenSearch
6. Cloud	AWS (S3, RDS, SQS, KMS)
7. DevOps	Docker

   
### Security & Compliance

1. PII Redaction before AI processing

2. Encryption using AWS KMS

3. Role-Based Access Control (RBAC)

4. Private VPC deployment

5. LLM Guardrails (prevents misuse & hallucination)

6. Immutable audit logs (WORM storage)


### Core Innovations

1. Smart alert prioritization (File / Monitor / Close)

2. SAR deduplication using time-window logic

3. Hallucination firewall (auto-validation + regeneration)

4. Explainable AI with transaction-level citations

5. Audit-ready SAR reports with traceability

### Model Performance
Metric	Value
ROC AUC	0.9734
Recall	91.2%
Precision	87.4%
False Positive Rate	0.52%



