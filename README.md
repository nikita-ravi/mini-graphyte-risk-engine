# Mini Graphyte: Adverse Media Risk Intelligence Engine

> A lightweight, explainable system for automated AML risk detection, entity resolution, and auditable risk scoring.

## 🎯 Problem Statement
Financial crime compliance teams are drowning in false positives. Traditional keyword matching systems flag every "John Smith" who appears in a news article, burying analysts in irrelevant alerts. 

**The Solution:** An intelligent risk engine that doesn't just match names, but understands **context**, classifies specific **risk typologies** (e.g., Sanctions vs. Fraud), and provides clear, quantitative **risk scores** to prioritize the most dangerous entities.

This project is a functional prototype of such a system, built to demonstrate the core architectural principles behind modern Risk Intelligence platforms like Graphyte.


| Feature | Traditional Search | Mini Graphyte (This Demo) |
|:---|:---|:---|
| **Resolution** | Boolean/String Match | Entity-Centric Normalization |
| **Detection** | Keyword hits | ML-driven Risk Typology Classification |
| **Scoring** | Count of hits | Multi-factor Risk Score (Volume + Severity + Recency) |
| **Output** | List of links | Explainable Audit Trail |

## 🧩 Technical Architecture

This engine operates as a real-time OSINT (Open Source Intelligence) pipeline. It does not rely on a static database but instead acts as a search-engine wrapper that applies a "Risk Layer" on top of live web results.

```mermaid
graph TD
    A[User Input: "Sam Bankman-Fried"] -->|DuckDuckGo Search| B[Live Web Index]
    B -->|Fetch 10 Latest News| C[Raw Snippet Ingestion]
    C -->|Vectorize (TF-IDF)| D[Inference Engine]
    D -->|Logistic Regression| E[Risk Classification]
    E -->|Scoring Algorithm| F[Final Risk Profile]
```

### 1. Data Ingestion (Real-Time)
- **Source**: DuckDuckGo Instant Answers API (via `duckduckgo_search`).
- **Logic**: The system queries `"{ENTITY_NAME} news"` to retrieve the most recent 10-20 indexed articles.
- **Privacy**: No API keys or login required; fully stateless execution.

### 2. The Machine Learning Core
The model is a **Logistic Regression** classifier trained on a proprietary synthetic dataset of 1,000+ AML-specific sentences.
- **Vectorization**: `TfidfVectorizer` (vocabulary size: 1,000) captures high-signal tokens like *"indicted"*, *"sanctioned"*, *"bribes"*, while ignoring noise.
- **Explainability**: Unlike Neural Networks, we can inspect the model coefficients to see *strictly* why a sentence was flagged (e.g., the token "cartel" adds +2.4 log-odds to the "Money Laundering" class).
- **Classes**:
    - `Critical`: Sanctions, Money Laundering
    - `High`: Fraud, Corruption, Human Trafficking
    - `Medium`: Financial Distress
    - `Low`: Neutral (Business news, Hiring, etc.)

### 3. Risk Scoring Algorithm
We use a composite score (0-100) to assist analysts in prioritization. It is **not** a black-box average.

$$ Score = (Confidence_{avg} \times 0.5) + (log(Volume) \times 0.3) + (Recency \times 0.2) $$

- **Confidence Priority**: A low-confidence hit (e.g., rumor) contributes less than a high-confidence match (e.g., DOJ Press Release).
- **Volume Dampening**: We use a logarithmic scale for article count so that a viral story with 1,000 links doesn't break the scale compared to a story with 10 links.

## 🏭 Production Data Flow (Conceptual)
While this demo runs in-memory with Python, a production implementation at Graphyte scale would utilize distributed compute:

1.  **Ingestion**: Spark Streaming jobs ingest daily article batches (GDELT / NewsAPI).
2.  **Filtering**: SQL logic filters candidate entities based on Watchlist matches.
3.  **Enrichment**: A Spark UDF applies the `MiniGraphyteEngine` vectorization and inference logic in parallel.
4.  **Aggregation**: Risk scores are aggregated at the `EntityID` level and written to a high-throughput store (e.g., ElasticSearch) for analyst retrieval.

## 🧠 LLMs vs Classical NLP in Regulated Environments
This project deliberately chooses **TF-IDF + Logistic Regression** over Large Language Models (LLMs) for the core classification task.

| Feature | TF-IDF + Logistic Regression | LLM (GPT-4 / Llama) |
|:---|:---|:---|
| **Explainability** | **High** (Exact feature coefficients) | Low (Black box attention weights) |
| **Auditability** | **Full** (Deterministic output) | Low (Non-deterministic) |
| **Speed/Cost** | Microseconds / Free | Seconds / Expensive |
| **Hallucination** | **Zero** (Cannot invent text) | Risk of fabrication |

*LLMs are reserved here for simpler tasks like summarization or generating synthetic training data, not for the critical path of risk decisioning.*

## 🚀 Getting Started locally

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   *Note: The first run will check for the pre-trained `data/risk_model.pkl`. If missing, it will auto-regenerate it using the built-in synthetic trainer.*


## ⚖️ Limitations & Scaling
This is a prototype. In a production environment (like Graphyte), the following upgrades would apply:
- **Data Ingestion**: Replace synthetic DB with live pipelines (GDELT, NewsAPI).
- **Resolution**: Upgrade to graph-based entity linking (network analysis).
- **Model**: Fine-tune a BERT-based transformer for higher semantic understanding of complex sentences, while maintaining an explanation layer (LIME/SHAP).

## 💡 Why This Matters for Regulated Environments
Models are easy; **Trust** is hard. By prioritizing explainability ("Why is this risk score 82?") and entity-centric aggregation over simple article retrieval, this system respects the operational reality of AML analysts who need to make defensible decisions fast.
