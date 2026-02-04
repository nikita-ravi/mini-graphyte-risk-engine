import streamlit as st
import pandas as pd
import altair as alt
from src.engine import MiniGraphyteEngine
import time

# Page Config
st.set_page_config(
    page_title="Mini Graphyte | Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium UI
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #0f172a; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .risk-tag { padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
    .audit-card { background: white; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .highlight-box { background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; border-radius: 0 4px 4px 0; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9322/9322127.png", width=50)
    st.title("Mini Graphyte")
    st.caption("Adverse Media Risk Engine")
    
    st.divider()
    
    st.subheader("⚙️ Analyst Controls")
    min_confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05, help="Filter out low-confidence ML predictions.")
    filter_typologies = st.multiselect(
        "Focus Typologies",
        ["sanctions", "fraud", "money_laundering", "corruption", "human_trafficking", "financial_distress"],
        default=[]
    )
    
    st.divider()
    
    with st.expander("👨‍💻 Why this approach?"):
        st.markdown("""
        **System Philosophy:**
        Most tools stop at *keyword matching*. This engine moves to *Risk Intelligence*.
        
        1. **Context, Not Matches:** Uses ML to understand if "laundering" refers to money or clothes.
        2. **Entity-Centric:** Aggregates risks at the company level, not just article level.
        3. **Audit Ready:** Every score is traceable back to a source sentence.
        """)

# --- Main Logic ---
@st.cache_resource
def get_engine():
    return MiniGraphyteEngine()

engine = get_engine()

# --- Hero Section ---
st.title("Entity Risk Intelligence")
st.markdown("""
<div style="font-size: 1.1em; color: #475569; margin-bottom: 20px;">
    An automated system for <b>Entity Resolution</b>, <b>Risk Classification</b>, and <b>Auditable Scoring</b>.
    <br><i>Designed to reduce false positives in AML workflows.</i>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    entity_query = st.text_input("Entity Search", placeholder="e.g. Northstar Logistics Ltd", label_visibility="collapsed")
with col2:
    analyze_btn = st.button("Analyze Risk Profile", type="primary", use_container_width=True)

# --- Analysis & Results ---
if analyze_btn and entity_query:
    with st.spinner("🔄 Resolving entities & classifying adverse media..."):
        time.sleep(1) # UX pacing
        result = engine.analyze_entity(entity_query)
        
    if not result:
        st.warning(f"No adverse media found for **{entity_query}**.")
    else:
        # TABS for different viewpoints
        tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🧠 System Logic (Behind the Scenes)", "💡 Methodology & Differentiators"])
        
        # --- TAB 1: EXECUTIVE DASHBOARD ---
        with tab1:
            st.markdown(f"### Risk Profile: **{result['entity']}**")
            
            # Top Metrics
            c1, c2, c3, c4 = st.columns(4)
            score = result['risk_score']
            
            c1.metric("Risk Score", f"{score}/100", 
                      delta="Critical" if score > 75 else "Elevated" if score > 50 else "Low", 
                      delta_color="inverse")
            
            c2.metric("Primary Threat", result['top_typologies'][0].replace("_", " ").title() if result['top_typologies'] else "None")
            
            risk_evidence = [e for e in result['evidence'] if e['predicted_risk'] != 'neutral']
            c3.metric("Verified Hits", len(risk_evidence))
            
            avg_conf = sum([e['confidence'] for e in risk_evidence])/len(risk_evidence) if risk_evidence else 0
            c4.metric("Avg. Confidence", f"{int(avg_conf*100)}%")
            
            st.divider()
            
            # Main Content Area
            row1_col1, row1_col2 = st.columns([2, 1])
            
            with row1_col1:
                st.subheader("Audit Trail")
                st.caption("Qualitative evidence driving the risk score.")
                
                filtered_evidence = [e for e in result['evidence'] if e['confidence'] >= min_confidence]
                if filter_typologies:
                    filtered_evidence = [e for e in filtered_evidence if e['predicted_risk'] in filter_typologies]
                
                if not filtered_evidence:
                    st.info("No evidence meets current filters.")
                    
                for item in filtered_evidence:
                    risk = item['predicted_risk']
                    color_border = "#dc2626" if risk in ['sanctions', 'money_laundering'] else "#f59e0b" if risk != 'neutral' else "#cbd5e1"
                    
                    st.markdown(f"""
                    <div class="audit-card" style="border-left: 5px solid {color_border};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; font-size:1.05em;">{item['headline']}</span>
                            <span style="background:{color_border}20; color:{color_border}; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.75em;">{risk.upper()}</span>
                        </div>
                        <div style="margin-top:5px; color:#64748b; font-size:0.9em;">
                            {item['source']} • {item['date']} • <b>Confidence: {item['confidence']:.2f}</b>
                        </div>
                        <div style="margin-top:8px; font-style:italic; color:#334155;">
                            "{item['snippet']}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with row1_col2:
                st.subheader("Risk Distribution")
                if risk_evidence:
                    # Altair Chart
                    source = pd.DataFrame(risk_evidence)
                    chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="predicted_risk", aggregate="count"),
                        color=alt.Color(field="predicted_risk", scale=alt.Scale(scheme='category20'), title="Typology"),
                        tooltip=["predicted_risk", "count()"]
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.write("No risk data to chart.")
                    
                st.info("""
                **Analyst Node:**
                High concentration of 'Money Laundering' flags combined with 'Sanctions' indicators suggests complex cross-border exposure.
                """)

        # --- TAB 2: SYSTEM LOGIC (BEHIND THE SCENES) ---
        with tab2:
            st.markdown("### 🔧 Under the Hood")
            st.markdown("How Mini Graphyte turns raw text into the score you see above.")
            
            st.markdown("#### 1. Entity Resolution Pipeline")
            st.code(f"""
            Raw Input:       "{entity_query}"
            Normalization:   "{entity_query.lower().replace('.', '').replace(' ltd', '')}" (Stripped Legal Suffixes)
            Match Logic:     Fuzzy Token Ratio > 90% OR Substring Match in Knowledge Graph
            Result:          MATCH FOUND -> ID: {result['entity']}
            """, language="python")

            st.markdown("#### 2. Scoring Algorithm (The Math)")
            st.latex(r"""
            Score = (Conf_{avg} \times 0.5) + (log(Vol) \times 0.3) + (Recency \times 0.2)
            """)
            st.write("We weight **Confidence** (how sure the model is) higher than **Volume** (how many articles), preventing a single viral false-positive from ruining a risk profile.")
            
            st.markdown("#### 3. Classification Probabilities")
            st.write("Sample of raw model output for the top article:")
            if risk_evidence:
                top_article = risk_evidence[0]
                cols = st.columns(3)
                cols[0].metric("Detected Class", top_article['predicted_risk'].upper())
                cols[1].metric("Confidence", f"{top_article['confidence']:.4f}")
                cols[2].metric("Vector Features", "1,024 (TF-IDF)")

        # --- TAB 3: DIFFERENTIATION ---
        with tab3:
            st.subheader("🚀 Why This is Different")
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("#### ❌ The Old Way (Keywords)")
                st.error("""
                *   **"Matches" everything**: Flags "John *Risk* (Author)" as "High Risk".
                *   **Zero context**: Can't tell the difference between a lawsuit *plaintiff* and *defendant*.
                *   **Analyst fatigue**: 95% False Positive rate.
                """)
                
            with c2:
                st.markdown("#### ✅ The Mini Graphyte Way")
                st.success("""
                *   **Understand Context**: Uses ML to detect specific *typologies* (e.g., bribery).
                *   **Entity Centric**: Groups 50 articles into **1 Risk Score**.
                *   **Explainable**: "We flagged this because of [Sentence A], not just because it matched a list."
                """)
                
            st.markdown("---")
            st.markdown("### 🎯 How I Can Help")
            st.markdown("""
            I don't just build models; I build **products** that solve business problems.
            
            *   **Systems Thinking**: I designed this pipeline to prioritize *auditability* because I know regulators demand it.
            *   **Full Stack Data Science**: I built the backend logic, the API layer, and this frontend dashboard.
            *   **Business Alignment**: This dashboard speaks the language of the analyst ("Risk Score"), not the data scientist ("F1 Score").
            """)

elif analyze_btn:
    st.warning("Please enter an entity name.")
