# Mini Graphyte Build Plan

## Phase 1: Setup & Data
- [ ] Create project structure `[DONE]`
- [ ] Create synthetic dataset generator (`src/data_generator.py`) to create training data and "live" articles.
- [ ] Generate initial datasets (`data/training_data.csv`, `data/article_db.csv`).

## Phase 2: Core Engine (`src/engine.py`)
- [ ] **Entity Resolution**: Implement robust normalization (case, punc, legal suffix removal).
- [ ] **Risk Typology Classifier**: Implement TF-IDF + Logistic Regression pipeline. Train on synthetic data.
- [ ] **Risk Scoring**: Implement the specific formula: `risk_score = (avg_risk_confidence * 0.5 + log(article_count + 1) * 0.3 + recency_score * 0.2)`.

## Phase 3: Application (`app.py`)
- [ ] Build Streamlit UI.
    - [ ] Search bar for Entity.
    - [ ] Dashboard view of Risk Score.
    - [ ] Top Typologies breakdown.
    - [ ] "Audit Trail" / Evidence list (Headlines, Snippets, Confidence).
    - [ ] Analyst features (filters).

## Phase 4: Documentation
- [ ] Write a professional, VP-facing README.
    - [ ] Problem Statement.
    - [ ] Architecture.
    - [ ] "Why this matters".
