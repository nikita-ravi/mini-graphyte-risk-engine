import pandas as pd
import random
from faker import Faker
import datetime

fake = Faker()

TYPOLOGIES = [
    "sanctions",
    "fraud",
    "money_laundering",
    "corruption",
    "human_trafficking",
    "financial_distress",
    "neutral"
]

KEYWORDS = {
    "sanctions": ["OFAC", "sanctioned", "embargo", "export controls", "blocked entity", "SDN list", "trade blacklist"],
    "fraud": ["Ponzi scheme", "embezzlement", "securities fraud", "wire fraud", "accounting irregularities", "defrauded investors", "fake accounts"],
    "money_laundering": ["money laundering", "shell company", "offshore accounts", "smurfing", "illicit funds", "cartel money", "unexplained wealth"],
    "corruption": ["bribery", "bribes", "kickbacks", "corrupt official", "foreign corrupt practices", "FCPA", "pay-to-play"],
    "human_trafficking": ["human trafficking", "forced labor", "modern slavery", "sex trafficking", "migrant exploitation", "child labor", "smuggling ring"],
    "financial_distress": ["bankruptcy", "insolvency", "defaulted", "liquidation", "chapter 11", "missed payments", "debt restructuring"],
    "neutral": ["quarterly earnings", "new product launch", "hiring spree", "stock update", "merger talks", "expansion plans", "charity event", "award winner", "partnership announcement"]
}

ENTITIES = [
    "Northstar Logistics Ltd",
    "Silverline Holdings LLC",
    "Vertex Global Corp",
    "Ivan Petrov",
    "Juan Carlos Mendoza",
    "Golden Gate Ventures",
    "Alpha Omega Solutions",
    "Chen Wei Trading"
]

SOURCES = ["Reuters", "Bloomberg", "Financial Times", "The Wall Street Journal", "Local News Daily", "Global Watch"]

def generate_snippet(typology, entity_name=None):
    if not entity_name:
        entity_name = fake.company()
    
    base_keywords = KEYWORDS[typology]
    keyword = random.choice(base_keywords)
    
    templates = [
        f"Reports indicate that {entity_name} was involved in significant {keyword} activities.",
        f"Authorities are investigating {entity_name} regarding allegations of {keyword}.",
        f"New evidence suggests {entity_name} played a key role in a {keyword} scandal.",
        f"{entity_name} denies all accusations related to {keyword} found in the recent leak.",
        f"The {keyword} investigation into {entity_name} has widened to include international partners."
    ]
    
    if typology == "neutral":
        templates = [
            f"{entity_name} announced record breaking numbers in their recent {keyword}.",
            f"The CEO of {entity_name} discussed the new {keyword} at the summit.",
            f"Analysts are optimistic about {entity_name} following the {keyword}.",
            f"{entity_name} continues to show growth with its latest {keyword}.",
        ]

    return random.choice(templates)

def generate_training_data(n=500):
    data = []
    for _ in range(n):
        typology = random.choice(TYPOLOGIES)
        text = generate_snippet(typology)
        data.append({"text": text, "label": typology})
    return pd.DataFrame(data)

def generate_article_db(entities=ENTITIES, articles_per_entity=5):
    data = []
    for entity in entities:
        # Assign a primary risk profile to each entity
        if "Northstar" in entity:
            profile = ["sanctions", "money_laundering"] * 3 + ["neutral"]
        elif "Silverline" in entity:
            profile = ["fraud"] * 4 + ["neutral"]
        elif "Ivan" in entity:
            profile = ["corruption", "human_trafficking"]
        elif "Golden" in entity:
            profile = ["neutral"] * 5 # Clean entity
        else:
            profile = random.choices(TYPOLOGIES, k=5)
            
        for _ in range(articles_per_entity):
            typology = random.choice(profile)
            text = generate_snippet(typology, entity)
            headline = f"{entity} linked to {random.choice(KEYWORDS[typology])}" if typology != "neutral" else f"{entity} news update: {random.choice(KEYWORDS[typology])}"
            
            data.append({
                "entity_name": entity,
                "headline": headline,
                "snippet": text,
                "source": random.choice(SOURCES),
                "date": fake.date_between(start_date='-2y', end_date='today').isoformat(),
                "url": fake.url(),
                "typology_gt": typology # Ground truth for checking, but model should predict
            })
            
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating training data...")
    df_train = generate_training_data(1000)
    df_train.to_csv("data/training_data.csv", index=False)
    print("Saved data/training_data.csv")
    
    print("Generating article database...")
    df_articles = generate_article_db(ENTITIES + [fake.company() for _ in range(10)])
    df_articles.to_csv("data/article_db.csv", index=False)
    print("Saved data/article_db.csv")
