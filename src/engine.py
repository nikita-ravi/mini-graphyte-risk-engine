import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os
from duckduckgo_search import DDGS

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
            
        # We NO LONGER load a static article_db.csv for live search
        # We only use the training data to teach the model what "risk" looks like
        
    def normalize_name(self, name):
        """
        Simple entity resolution normalization.
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
            raise FileNotFoundError(f"Training data not found at {train_path}. Please run data_generator.py first.")
            
        df = pd.read_csv(train_path)
        
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        X = self.vectorizer.fit_transform(df['text'])
        y = df['label']
        
        self.model = LogisticRegression(class_weight='balanced')
        self.model.fit(X, y)
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        print("Model trained and saved.")

    def fetch_live_news(self, entity_name, limit=10):
        """
        searches DuckDuckGo for live news about the entity.
        Returns a list of dicts: {'headline', 'snippet', 'source', 'date', 'url'}
        """
        # Search query: "Entity Name" + typical risk keywords to cast a wide net
        # We don't assume risk, but we want to see if any exist.
        query = f'"{entity_name}" news' 
        
        results = []
        try:
            with DDGS() as ddgs:
                ddgs_news = list(ddgs.news(query, max_results=limit))
                
                for r in ddgs_news:
                    results.append({
                        "headline": r.get('title', ''),
                        "snippet": r.get('body', ''), # snippet
                        "source": r.get('source', 'Web'),
                        "date": r.get('date', 'Recent'),
                        "url": r.get('url', '#')
                    })
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
            
        return results

    def calculate_risk_score(self, evidence):
        """
        Calculates risk score (0-100) based on evidence.
        """
        if not evidence:
            return 0
            
        risk_articles = [e for e in evidence if e['predicted_risk'] != 'neutral']
        
        if not risk_articles:
            return 0 
            
        avg_conf = np.mean([e['confidence'] for e in risk_articles])
        count = len(risk_articles)
        volume_score = min(np.log(count + 1) / 2.5, 1.0)
        recency_score = 0.8 # Placeholder for live parsing
        
        raw_score = (avg_conf * 0.5) + (volume_score * 0.3) + (recency_score * 0.2)
        return int(min(raw_score * 100, 100))

    def analyze_entity(self, entity_name):
        """
        Core pipeline:
        1. Live Web Search (OSINT)
        2. Classify Risks (Inference)
        3. Score
        """
        # 1. Fetch Live Data
        raw_articles = self.fetch_live_news(entity_name)
        
        if not raw_articles:
            return {
                "entity": entity_name,
                "risk_score": 0,
                "top_typologies": [],
                "evidence": [],
                "summary": "No recent news found."
            }
            
        # 2. Classify Articles
        evidence_list = []
        typology_counts = {}
        
        if not raw_articles:
             return None

        snippets = [a['snippet'] + " " + a['headline'] for a in raw_articles]
        tfidf_features = self.vectorizer.transform(snippets)
        predictions = self.model.predict(tfidf_features)
        probs = self.model.predict_proba(tfidf_features)
        
        for idx, article in enumerate(raw_articles):
            pred_label = predictions[idx]
            confidence = np.max(probs[idx])
            
            # Simple heuristic to reduce false positives from generic training data
            # If confidence is low, classify as neutral
            if confidence < 0.55:
                pred_label = 'neutral'
            
            evidence_item = {
                "headline": article['headline'],
                "snippet": article['snippet'][:200] + "...",
                "source": article['source'],
                "date": article['date'],
                "url": article['url'],
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
            "entity": entity_name,
            "risk_score": risk_score,
            "top_typologies": top_typologies,
            "evidence": evidence_list,
            "summary": f"Analyzed {len(raw_articles)} articles."
        }

        """
        Returns classification report and confusion matrix on training data.
        """
        train_path = f"{self.data_dir}/training_data.csv"
        df = pd.read_csv(train_path)
        
        X = self.vectorizer.transform(df['text'])
        y_true = df['label']
        y_pred = self.model.predict(X)
        
        from sklearn.metrics import classification_report, confusion_matrix
        report = classification_report(y_true, y_pred, output_dict=True)
        cm = confusion_matrix(y_true, y_pred, labels=self.model.classes_)
        
        return report, cm, self.model.classes_

    def explain_prediction(self, text_snippet, predicted_class):
        """
        Returns the top 5 contributing tokens for a specific prediction using coefficients.
        Simple 'LIME-lite' for linear models.
        """
        if predicted_class == 'neutral':
            return []
            
        class_idx = list(self.model.classes_).index(predicted_class)
        # Get coefficients for this class: shape (n_features,)
        # Logic: We multiply the coeff by the tf-idf value of the token in this specific doc
        
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        coefs = self.model.coef_[class_idx]
        
        # Transform just this text
        tfidf_vector = self.vectorizer.transform([text_snippet]).toarray()[0]
        
        # Element-wise multiplication to see contribution of each word in THIS document
        contributions = coefs * tfidf_vector
        
        # Get top indices
        top_indices = contributions.argsort()[::-1][:4] # Top 4 words
        
        explanations = []
        for idx in top_indices:
            if contributions[idx] > 0: # Only positive contributors
                explanations.append(f"{feature_names[idx]} (+{contributions[idx]:.2f})")
                
        return explanations
