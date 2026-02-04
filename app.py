import streamlit as st
import pandas as pd
from src.engine import MiniGraphyteEngine
import time

# Page Config
st.set_page_config(
    page_title="Mini Graphyte | Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for that "Premium" feel
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #0f172a; 
        font-family: 'Inter', sans-serif;
    }
    .risk-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8em;
    }
    .risk-high { background-color: #fee2e2; color: #991b1b; }
    .risk-med { background-color: #fef3c7; color: #92400e; }
    .risk-low { background-color: #d1fae5; color: #065f46; }
</style>
""", unsafe_allow_html=True)

# sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9322/9322127.png", width=50) # Generic shield icon
    st.title("Mini Graphyte")
    st.caption("Adverse Media Risk Engine")
    
    st.divider()
    
    st.subheader("Analyst Controls")
    min_confidence = st.slider("Min. Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    filter_typologies = st.multiselect(
        "Filter Typologies",
        ["sanctions", "fraud", "money_laundering", "corruption", "human_trafficking", "financial_distress"],
        default=[]
    )
    
    st.divider()
    st.info("Demo v1.0.0\nEvaluating Entity Risk via Open Source Intelligence (OSINT)")

# Main Content
st.title("Entity Risk Intelligence")
st.markdown("Search across global adverse media to resolve entities and classify risk typologies.")

# Search
col1, col2 = st.columns([3, 1])
with col1:
    entity_query = st.text_input("Enter Person or Company Name", placeholder="e.g. Northstar Logistics Ltd")
with col2:
    st.write("") # Spacer
    st.write("")
    analyze_btn = st.button("Analyze Risk", type="primary", use_container_width=True)

# Helper to load engine
@st.cache_resource
def get_engine():
    return MiniGraphyteEngine()

engine = get_engine()

if analyze_btn and entity_query:
    with st.spinner(f"Resolving entity '{entity_query}' and scanning sources..."):
        # Fake delay for "system processing" feel
        time.sleep(0.8)
        result = engine.analyze_entity(entity_query)
    
    if not result:
        st.warning("No entity found matching that name.")
    else:
        # Results Dashboard
        
        # 1. Header Metrics
        st.subheader(f"Risk Profile: {result['entity']}")
        
        m1, m2, m3 = st.columns(3)
        
        score = result['risk_score']
        score_color = "normal"
        if score > 75: score_color = "off" # Streamlit doesn't support generic color, but we can visually cue
        
        m1.metric("Overall Risk Score", f"{score}/100", delta=None, help="Composite score based on evidence volume, severity, and confidence.")
        m2.metric("Primary Risk Typology", result['top_typologies'][0].title() if result['top_typologies'] else "None", 
                  # Delta color based on risk
                  delta="Critical" if result['top_typologies'] and result['top_typologies'][0] in ['sanctions', 'money_laundering'] else "Normal",
                  delta_color="inverse")
        m3.metric("Evidence Count", len([e for e in result['evidence'] if e['predicted_risk'] != 'neutral']))

        # 2. Evidence Locker
        st.divider()
        st.subheader("Audit Trail & Evidence")
        
        evidence = result['evidence']
        
        # Filter Logic
        filtered_evidence = [
            e for e in evidence 
            if e['confidence'] >= min_confidence
        ]
        if filter_typologies:
            filtered_evidence = [e for e in filtered_evidence if e['predicted_risk'] in filter_typologies]
            
        if not filtered_evidence:
            st.info("No evidence meets the current filter criteria.")
        
        for item in filtered_evidence:
            risk_label = item['predicted_risk']
            
            # Styling card
            if risk_label == 'neutral':
                border_color = "#e5e7eb"
                badge_class = "risk-low"
            elif risk_label in ['sanctions', 'money_laundering', 'corruption']:
                border_color = "#fca5a5"
                badge_class = "risk-high"
            else:
                border_color = "#fcd34d"
                badge_class = "risk-med"
                
            with st.container():
                st.markdown(f"""
                <div style="border-left: 5px solid {border_color}; padding: 10px 15px; background: white; margin-bottom: 10px; border-radius: 0 5px 5px 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 600; font-size: 1.1em;">{item['headline']}</span>
                        <span class="risk-badge {badge_class}">{risk_label.upper()}</span>
                    </div>
                    <div style="color: #64748b; font-size: 0.9em; margin-top: 5px;">
                        {item['source']} • {item['date']} • <b>Confidence: {int(item['confidence']*100)}%</b>
                    </div>
                    <div style="margin-top: 8px; font-style: italic; color: #334155;">
                        "{item['snippet']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif analyze_btn:
    st.warning("Please enter an entity name to search.")

# Footer
st.markdown("---")
st.caption("Mini Graphyte Risk Engine Demo | Generated for Quantifind Review")
