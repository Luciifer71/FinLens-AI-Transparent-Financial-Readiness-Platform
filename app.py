import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="FinLens AI - Transparent Readiness & Guidance",
    page_icon="💡",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

# --- Custom Styling for Hackathon Polish ---
st.markdown("""
    <style>
    .main-header { font-size: 2.3rem; font-weight: 700; color: #1E293B; }
    .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 1rem; }
    .card { background-color: #F8FAFC; border-radius: 10px; padding: 15px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

# --- Mandatory Legal Disclaimer Banner ---
st.warning(
    "⚠️ **Educational Notice:** FinLens AI does **not** generate an official CIBIL/credit score "
    "and does **not** provide regulated financial advice. Designed solely for transparent financial education."
)

st.markdown('<div class="main-header">💡 FinLens AI Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Transparent Credit Readiness, Explainable AI (SHAP), & Micro-Investment Simulator</div>', unsafe_allow_html=True)

# --- Fetch Sample Users ---
@st.cache_data
def load_mock_users():
    try:
        res = requests.get(f"{BACKEND_URL}/api/users")
        if res.status_code == 200:
            return res.json()
    except Exception:
        return []
    return []

users = load_mock_users()

if not users:
    st.error("⚠️ Backend API is offline. Make sure `uvicorn main:app --reload` is running in terminal!")
    st.stop()

# --- Sidebar: User Profile Selection & Raw Signals ---
st.sidebar.header("👤 Select User Profile")
user_names = [f"{u['name']} ({u['city']})" for u in users]
selected_idx = st.sidebar.selectbox("Choose sample profile:", range(len(user_names)), format_func=lambda x: user_names[x])
user = users[selected_idx]

st.sidebar.markdown("---")
st.sidebar.subheader("📱 Digital Footprint Signals")
st.sidebar.metric("Monthly Income", f"₹{user['monthly_income']:,}")
st.sidebar.write(f"• **Mobile Recharge:** ₹{user['avg_mobile_recharge']} / {user['recharge_frequency_days']} days")
st.sidebar.write(f"• **Utility Delay:** {user['utility_payment_delay_days']} days")
st.sidebar.write(f"• **E-Commerce Volume:** ₹{user['ecom_transaction_volume']:,}/mo")
st.sidebar.write(f"• **Return Rate:** {int(user['ecom_return_rate']*100)}%")

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs([
    "📊 Financial Readiness Gauge & SHAP", 
    "🎛️ Live 'What-If' Score Simulator", 
    "🧭 Risk Profiler & Growth Simulator"
])

# Evaluate baseline profile
eval_payload = {
    "monthly_income": user["monthly_income"],
    "avg_mobile_recharge": user["avg_mobile_recharge"],
    "recharge_frequency_days": user["recharge_frequency_days"],
    "utility_payment_delay_days": user["utility_payment_delay_days"],
    "ecom_transaction_volume": user["ecom_transaction_volume"],
    "ecom_return_rate": user["ecom_return_rate"]
}

base_response = requests.post(f"{BACKEND_URL}/api/evaluate-readiness", json=eval_payload)
base_data = base_response.json() if base_response.status_code == 200 else {}


# ==========================================
# TAB 1: READINESS GAUGE & SHAP VISUALS
# ==========================================
with tab1:
    st.header(f"Financial Readiness Analysis for {user['name']}")
    
    if base_data:
        score = base_data["financial_readiness_index"]
        explanations = base_data["explainability"]
        
        col_gauge, col_shap = st.columns([1, 1.4])
        
        # 1. Gauge Chart
        with col_gauge:
            st.subheader("Financial Readiness Index (FRI)")
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "#1E3A8A"},
                    'steps': [
                        {'range': [0, 45], 'color': "#FEE2E2"},
                        {'range': [45, 70], 'color': "#FEF3C7"},
                        {'range': [70, 100], 'color': "#D1FAE5"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 3},
                        'thickness': 0.75,
                        'value': score
                    }
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            if score >= 70:
                st.success("🟢 High Readiness: Qualified for standard micro-investment & credit products.")
            elif score >= 50:
                st.warning("🟡 Moderate Readiness: Minor improvements needed to unlock optimal tiers.")
            else:
                st.error("🔴 Building Phase: Focus on utility bill consistency & reducing returns.")

        # 2. Visual SHAP Bar Chart
        with col_shap:
            st.subheader("🔍 Explainable AI (SHAP Impact Breakdown)")
            
            df_shap = pd.DataFrame(explanations)
            df_shap['color'] = df_shap['type'].apply(lambda x: '#10B981' if x == 'Positive' else '#EF4444')
            
            fig_bar = go.Figure(go.Bar(
                x=df_shap['impact_value'],
                y=df_shap['feature'],
                orientation='h',
                marker=dict(color=df_shap['color']),
                text=df_shap['impact_value'],
                textposition='auto'
            ))
            fig_bar.update_layout(
                title="Top 3 Factor Impacts (+ Boost / - Drag)",
                xaxis_title="Score Impact Points",
                yaxis=dict(autorange="reversed"),
                height=260,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        
        # 3. Gamified Improvement Roadmap
        st.subheader("🎯 Actionable Score Optimization Plan")
        cols_actions = st.columns(3)
        for i, factor in enumerate(explanations):
            with cols_actions[i]:
                icon = "✨" if factor['type'] == 'Positive' else "⚡"
                st.info(f"{icon} **{factor['feature'].replace('_', ' ').title()}**\n\n{factor['plain_text_explanation']}")

# ==========================================
# TAB 2: LIVE "WHAT-IF" SIMULATOR (JUDGE FAVORITE)
# ==========================================
with tab2:
    st.header("🎛️ Real-Time Behavioral 'What-If' Simulator")
    st.write("Adjust user habit parameters below to observe how ML score predictions update live!")
    
    col_sim_inputs, col_sim_output = st.columns([1.2, 1])
    
    with col_sim_inputs:
        sim_delay = st.slider("Utility Payment Delay (Days):", 0, 30, int(user["utility_payment_delay_days"]))
        sim_returns = st.slider("E-Commerce Return Rate (%):", 0, 50, int(user["ecom_return_rate"] * 100)) / 100.0
        sim_recharge_freq = st.slider("Recharge Frequency (Days):", 5, 45, int(user["recharge_frequency_days"]))
        sim_income = st.number_input("Monthly Income (₹):", min_value=5000, max_value=200000, value=int(user["monthly_income"]), step=5000)
        
    with col_sim_output:
        sim_payload = {
            "monthly_income": sim_income,
            "avg_mobile_recharge": user["avg_mobile_recharge"],
            "recharge_frequency_days": sim_recharge_freq,
            "utility_payment_delay_days": sim_delay,
            "ecom_transaction_volume": user["ecom_transaction_volume"],
            "ecom_return_rate": sim_returns
        }
        
        sim_res = requests.post(f"{BACKEND_URL}/api/evaluate-readiness", json=sim_payload)
        if sim_res.status_code == 200:
            sim_score = sim_res.json()["financial_readiness_index"]
            original_score = base_data.get("financial_readiness_index", sim_score)
            delta = sim_score - original_score
            
            st.metric(
                label="Simulated Financial Readiness Score", 
                value=f"{sim_score} / 100", 
                delta=f"{delta} points from original" if delta != 0 else "Unchanged"
            )
            
            if delta > 0:
                st.success(f"🎉 **Impact:** By improving these habits, {user['name']} could gain **+{delta} points**!")
            elif delta < 0:
                st.error(f"⚠️ **Warning:** Increased delays/returns reduce score by **{delta} points**.")

# ==========================================
# TAB 3: RISK PROFILER & GROWTH SIMULATOR
# ==========================================
with tab3:
    st.header("🧭 Investment Readiness Gate & Growth Simulator")
    
    col_input, col_sim = st.columns([1, 1.8])
    
    with col_input:
        st.subheader("Financial Gate Checks")
        has_debt = st.checkbox("Active high-interest debt?", value=False)
        emergency_months = st.slider("Emergency fund buffer (months):", 0, 6, 2)
        
        st.subheader("Investment Preference")
        monthly_inv = st.number_input("Monthly Investment Amount (₹):", min_value=500, max_value=50000, value=2000, step=500)
        horizon = st.slider("Investment Horizon (Years):", 1, 5, 3)
        loss_tolerance = st.radio("Risk Reaction:", ["Low (Capital Preservation)", "Medium (Balanced Growth)", "High (Maximum Yield)"])
        
        tolerance_key = "low" if "Low" in loss_tolerance else "medium" if "Medium" in loss_tolerance else "high"
        
    with col_sim:
        risk_payload = {
            "has_high_interest_debt": has_debt,
            "emergency_fund_months": emergency_months,
            "investment_horizon_years": horizon,
            "loss_tolerance": tolerance_key,
            "monthly_investment_amount": monthly_inv
        }
        
        risk_res = requests.post(f"{BACKEND_URL}/api/assess-risk", json=risk_payload)
        
        if risk_res.status_code == 200:
            risk_data = risk_res.json()
            gate_status = risk_data.get("gate_status")
            
            if gate_status == "BLOCKED":
                st.error("🚫 **Financial Readiness Gate: High-Interest Debt Detected**")
                st.write(f"**Action:** {risk_data['primary_recommendation']}")
                st.info(risk_data['explanation'])
            elif gate_status == "CAUTION":
                st.warning("⚠️ **Financial Readiness Gate: Low Emergency Reserve**")
                st.write(f"**Action:** {risk_data['primary_recommendation']}")
                st.info(risk_data['explanation'])
            else:
                st.success(f"🧬 **Financial Strategy:** {risk_data['financial_dna']}")
                st.write(f"**Educational Category:** `{risk_data['category_recommendation']}`")
                
                projections = risk_data["projections"]
                proj_df = pd.DataFrame(projections)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=proj_df['year'], y=proj_df['total_invested'], mode='lines+markers', name='Total Invested', line=dict(dash='dash', color='gray')))
                fig.add_trace(go.Scatter(x=proj_df['year'], y=proj_df['base_scenario'], mode='lines+markers', name='Base Case', line=dict(color='#2563EB', width=3)))
                fig.add_trace(go.Scatter(x=proj_df['year'], y=proj_df['bull_scenario'], mode='lines+markers', name='Bull Market (+3%)', line=dict(color='#10B981')))
                fig.add_trace(go.Scatter(x=proj_df['year'], y=proj_df['bear_scenario'], mode='lines+markers', name='Bear Market (-3%)', line=dict(color='#EF4444')))
                
                fig.update_layout(
                    title=f"Illustrative {horizon}-Year Growth Scenarios (₹{monthly_inv:,}/mo)",
                    xaxis_title="Timeline (Years)",
                    yaxis_title="Portfolio Value (₹)",
                    hovermode="x unified",
                    height=380
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"ℹ️ {risk_data['disclaimer']}")