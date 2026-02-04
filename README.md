# Mini Graphyte: Adverse Media Risk Intelligence Engine

> A lightweight, explainable system for automated AML risk detection, entity resolution, and auditable risk scoring.

## 🎯 Problem Statement
Financial crime compliance teams are drowning in false positives. Traditional keyword matching systems flag every "John Smith" who appears in a news article, burying analysts in irrelevant alerts. 

**The Solution:** An intelligent risk engine that doesn't just match names, but understands **context**, classifies specific **risk typologies** (e.g., Sanctions vs. Fraud), and provides clear, quantitative **risk scores** to prioritize the most dangerous entities.

This project is a functional prototype of such a system, built to demonstrate the core architectural principles behind modern Risk Intelligence platforms like Graphyte.

## 🔍 How This Mirrors Graphyte
This demo was built to align with Quantifind’s philosophy: **Accuracy > Hype**.

| Feature | Traditional Search | Mini Graphyte (This Demo) |
|:---|:---|:---|
| **Resolution** | Boolean/String Match | Entity-Centric Normalization |
| **Detection** | Keyword hits | ML-driven Risk Typology Classification |
| **Scoring** | Count of hits | Multi-factor Risk Score (Volume + Severity + Recency) |
| **Output** | List of links | Explainable Audit Trail |

## 🧩 Architecture

```mermaid
graph TD
    A[User Input: Entity Name] --> B{Entity Resolution Layer}
    B -->|Normalize & Dedup| C[Adverse Media Collection]
    C -->|Extract Snippets| D[ML Classification Engine]
    D -->|TF-IDF + LogReg| E[Risk Typology Detection]
    E --> F[Scoring Algorithm]
    F --> G[Analyst Dashboard (Streamlit)]
```

### 1. Entity Resolution
Includes a normalization layer that handles:
- Case sensitivity & Punctuation
- Legal entity suffix removal (`Ltd`, `LLC`, `Corp`) for fuzzier matching
- Name variation handling

### 2. Risk Typology Classification
Instead of a "black box" LLM, this system uses a **TF-IDF + Logistic Regression** pipeline.
- **Why?** In regulated environments (AML/KYC), explainability is non-negotiable. We need to know *exactly* which tokens triggered a "Money Laundering" flag to satisfy auditors.
- **Classes:** `Sanctions`, `Fraud`, `Money Laundering`, `Corruption`, `Human Trafficking`, `Financial Distress`, `Neutral`.

### 3. Risk Scoring Factors
The final risk score (0-100) is calculated using a transparent formula prioritizing confidence and severity:

$$ Score = (Confidence_{avg} \times 0.5) + (log(Volume) \times 0.3) + (Recency \times 0.2) $$

## 🛠️ Project Structure

```
mini-graphyte-risk-intelligence/
├── data/                  # Synthetic Article Database & Training Data
├── src/
│   ├── engine.py          # Core logic: Resolution, Inference, Scoring
│   └── data_generator.py  # Utility to simulate open-source media environment
├── app.py                 # Streamlit Analyst Dashboard
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Data & Train Model**
   (First run only - creates synthetic OSINT database)
   ```bash
   python src/data_generator.py
   ```

3. **Launch Analyst Dashboard**
   ```bash
   streamlit run app.py
   ```

## ⚖️ Limitations & Scaling
This is a prototype. In a production environment (like Graphyte), the following upgrades would apply:
- **Data Ingestion**: Replace synthetic DB with live pipelines (GDELT, NewsAPI).
- **Resolution**: Upgrade to graph-based entity linking (network analysis).
- **Model**: Fine-tune a BERT-based transformer for higher semantic understanding of complex sentences, while maintaining an explanation layer (LIME/SHAP).

## 💡 Why This Matters for Regulated Environments
Models are easy; **Trust** is hard. By prioritizing explainability ("Why is this risk score 82?") and entity-centric aggregation over simple article retrieval, this system respects the operational reality of AML analysts who need to make defensible decisions fast.
