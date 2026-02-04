import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os

class MiniGraphyteEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.model_path = f"{data_dir}/risk_model.pkl"
        self.vectorizer_path = f"{data_dir}/vectorizer.pkl"
        
        # Load or train model
        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        except:
            print("Model not found. Training new model...")
            self.train_model()
            
        # Load article database
        self.articles_df = pd.read_csv(f"{data_dir}/article_db.csv")
        
    def normalize_name(self, name):
        """
        Simple entity resolution normalization.
        - Lowercase
        - Remove punctuation
        - Remove legal suffixes (Ltd, LLC, Inc)
        """
        name = name.lower()
        name = re.sub(r'[^\w\s]', '', name)
        
        suffixes = [" ltd", " llc", " inc", " corp", " limited", " holdings", " group"]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:len(name)-len(suffix)]
        
        return name.strip()

    def train_model(self):
        """
        Trains a TF-IDF + Logistic Regression model on the synthetic training data.
        """
        train_path = f"{self.data_dir}/training_data.csv"
        if not os.path.exists(train_path):
            raise FileNotFoundError(f"Training data not found at {train_path}")
            
        df = pd.read_csv(train_path)
        
        # Create Pipeline
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        X = self.vectorizer.fit_transform(df['text'])
        y = df['label']
        
        self.model = LogisticRegression(class_weight='balanced')
        self.model.fit(X, y)
        
        # Save
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        print("Model trained and saved.")

    def calculate_risk_score(self, evidence):
        """
        Calculates risk score (0-100) based on evidence.
        Formula: avg_risk_confidence * 0.5 + log(article_count + 1) * 0.3 + recency_score * 0.2
        (Simplified implementation)
        """
        if not evidence:
            return 0
            
        # 1. Avg Risk Confidence (for non-neutral articles)
        risk_articles = [e for e in evidence if e['predicted_risk'] != 'neutral']
        
        if not risk_articles:
            return 0 # All news is neutral
            
        avg_conf = np.mean([e['confidence'] for e in risk_articles])
        
        # 2. Volume Score
        # Logarithmic scale for volume: log(count+1). Let's maximize it at ~10 articles -> score 1.0
        # log(11) is ~2.4. So divide by 2.5 to normalize roughly.
        count = len(risk_articles)
        volume_score = min(np.log(count + 1) / 2.5, 1.0)
        
        # 3. Recency (Not fully implemented in synthetic data dates accurately, so we'll mock it or use 1.0 for now)
        # In a real system, decay score based on date.
        recency_score = 0.8 
        
        # Weighted sum
        # Weights: Confidence (50%), Volume (30%), Recency (20%)
        # Result is 0-1 float.
        raw_score = (avg_conf * 0.5) + (volume_score * 0.3) + (recency_score * 0.2)
        
        return int(min(raw_score * 100, 100))

    def analyze_entity(self, entity_name):
        """
        Core pipeline:
        1. Resolve Entity
        2. Fetch Articles
        3. Classify Risks
        4. Score
        """
        normalized_query = self.normalize_name(entity_name)
        
        # 1. Search (Simulated Entity Resolution)
        # We look for partial matches in the mock DB 'entity_name' column
        # In a real Graphyte demo, this is the complex part. Here we keep it robust but simple.
        matches = self.articles_df[self.articles_df['entity_name'].apply(lambda x: self.normalize_name(x)) == normalized_query]
        
        if matches.empty:
            # Fallback fuzzy search or just return empty
            # Let's try matching if query is substring of db entity
            matches = self.articles_df[self.articles_df['entity_name'].apply(lambda x: normalized_query in self.normalize_name(x))]
        
        if matches.empty:
            return {
                "entity": entity_name,
                "risk_score": 0,
                "typologies": [],
                "evidence": [],
                "summary": "No adverse media found."
            }
            
        # 2. Classify Articles
        evidence_list = []
        typology_counts = {}
        
        tfidf_features = self.vectorizer.transform(matches['snippet'])
        predictions = self.model.predict(tfidf_features)
        probs = self.model.predict_proba(tfidf_features)
        
        classes = self.model.classes_
        
        for idx, row in matches.reset_index().iterrows():
            pred_label = predictions[idx]
            confidence = np.max(probs[idx])
            
            # Map neutral to 0 risk effectively, but we still store it
            
            evidence_item = {
                "headline": row['headline'],
                "snippet": row['snippet'],
                "source": row['source'],
                "date": row['date'],
                "predicted_risk": pred_label,
                "confidence": round(confidence, 2)
            }
            evidence_list.append(evidence_item)
            
            if pred_label != 'neutral':
                typology_counts[pred_label] = typology_counts.get(pred_label, 0) + 1

        # 3. Score
        risk_score = self.calculate_risk_score(evidence_list)
        
        # 4. Top Typologies
        sorted_typologies = sorted(typology_counts.items(), key=lambda x: x[1], reverse=True)
        top_typologies = [t[0] for t in sorted_typologies]
        
        return {
            "entity": matches.iloc[0]['entity_name'], # Return the resolved name
            "risk_score": risk_score,
            "top_typologies": top_typologies,
            "evidence": evidence_list,
            "summary": f"Found {len(matches)} articles. Primary risks: {', '.join(top_typologies[:2])}" if top_typologies else "No significant risks detected."
        }
