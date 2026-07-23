from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import json
import os

# 1. Initialize FastAPI App
app = FastAPI(
    title="FinLens AI Engine API",
    description="Transparent Credit Scoring & Micro-Investment Advisor Platform",
    version="1.0.0"
)

# Enable CORS for Frontend communication (React / Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load ML Models and Datasets
MODEL_PATH = "models/credit_model.pkl"
EXPLAINER_PATH = "models/shap_explainer.pkl"
DATA_PATH = "data/mockData.json"

if os.path.exists(MODEL_PATH) and os.path.exists(EXPLAINER_PATH):
    model = joblib.load(MODEL_PATH)
    explainer = joblib.load(EXPLAINER_PATH)
else:
    model = None
    explainer = None

feature_cols = [
    "monthly_income",
    "avg_mobile_recharge",
    "recharge_frequency_days",
    "utility_payment_delay_days",
    "ecom_transaction_volume",
    "ecom_return_rate"
]

# 3. Request Schemas
class UserEvaluationRequest(BaseModel):
    monthly_income: float
    avg_mobile_recharge: float
    recharge_frequency_days: int
    utility_payment_delay_days: int
    ecom_transaction_volume: float
    ecom_return_rate: float

class RiskProfileRequest(BaseModel):
    has_high_interest_debt: bool
    emergency_fund_months: float
    investment_horizon_years: int
    loss_tolerance: str # "low", "medium", "high"
    monthly_investment_amount: float

# 4. API Endpoints

@app.get("/")
def root():
    return {
        "status": "online",
        "platform": "FinLens AI",
        "disclaimer": "For educational purposes only. Not regulated financial advice."
    }

@app.get("/api/users")
def get_all_users():
    """Returns sample mock user profiles for frontend evaluation."""
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=404, detail="Mock data file not found.")
    with open(DATA_PATH, "r") as f:
        users = json.load(f)
    return users[:10]  # Return top 10 profiles for dashboard demo

@app.post("/api/evaluate-readiness")
def evaluate_readiness(user: UserEvaluationRequest):
    """Calculates Financial Readiness Index and generates SHAP Explainability."""
    if not model or not explainer:
        raise HTTPException(status_code=500, detail="ML Model not loaded.")
    
    input_data = user.model_dump()
    input_df = pd.DataFrame([input_data])[feature_cols]
    
    # Predict Score
    predicted_score = int(round(model.predict(input_df)[0]))
    
    # SHAP Explanations
    shap_values = explainer(input_df)
    values = shap_values.values[0]
    
    feature_impacts = []
    for name, impact in zip(feature_cols, values):
        feature_impacts.append({"feature": name, "impact": float(impact)})
        
    feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
    top_3 = feature_impacts[:3]
    
    feedback_rules = {
        "utility_payment_delay_days": {
            "pos": "Consistent utility payments support your digital trust profile.",
            "neg": "Utility payment delays reduce your score. On-time payments will boost it."
        },
        "ecom_return_rate": {
            "pos": "Low return rates demonstrate active consumer discipline.",
            "neg": "High return rates reduce digital trust signals."
        },
        "recharge_frequency_days": {
            "pos": "Regular mobile recharge patterns show routine financial discipline.",
            "neg": "Irregular recharge cycles lower routine stability signals."
        },
        "avg_mobile_recharge": {
            "pos": "Consistent mobile spend shows active digital participation.",
            "neg": "Lower mobile transaction history provides fewer trust data points."
        },
        "ecom_transaction_volume": {
            "pos": "Active digital transaction volume demonstrates digital readiness.",
            "neg": "Limited digital transaction volume provides fewer trust data points."
        },
        "monthly_income": {
            "pos": "Healthy income stability supports overall financial resilience.",
            "neg": "Income level limits maximum credit-readiness capacity."
        }
    }
    
    explanations = []
    for item in top_3:
        feat = item["feature"]
        imp = item["impact"]
        direction = "pos" if imp >= 0 else "neg"
        explanation = feedback_rules.get(feat, {}).get(direction, f"{feat} impacted your score.")
        
        explanations.append({
            "feature": feat,
            "impact_value": round(imp, 2),
            "type": "Positive" if imp >= 0 else "Negative",
            "plain_text_explanation": explanation
        })
        
    return {
        "financial_readiness_index": predicted_score,
        "explainability": explanations
    }

@app.post("/api/assess-risk")
def assess_risk(data: RiskProfileRequest):
    """
    Evaluates Financial Readiness Gate and provides Educational Investment Category Recommendations.
    """
    # 1. Financial Readiness Gate Checks
    if data.has_high_interest_debt:
        return {
            "gate_status": "BLOCKED",
            "primary_recommendation": "Debt Repayment Priority",
            "explanation": "Pay off high-interest debt before allocating funds to investments to maximize net return.",
            "category_recommendation": "High-Interest Debt Repayment"
        }
        
    if data.emergency_fund_months < 3:
        return {
            "gate_status": "CAUTION",
            "primary_recommendation": "Build Emergency Savings Buffer",
            "explanation": f"You currently have {data.emergency_fund_months} months of emergency funds. Aim for 3-6 months in liquid savings.",
            "category_recommendation": "Liquid Funds / High-Yield Savings"
        }
        
    # 2. Risk Bucket Logic
    if data.loss_tolerance == "low":
        risk_bucket = "Conservative"
        recommended_category = "Government Securities / Debt Mutual Funds"
        expected_annual_return = 0.07
    elif data.loss_tolerance == "medium":
        risk_bucket = "Balanced"
        recommended_category = "Balanced Advantage Funds / Gold ETFs"
        expected_annual_return = 0.095
    else:
        risk_bucket = "Growth Explorer"
        recommended_category = "Broad Market Index Funds (e.g., Nifty 50)"
        expected_annual_return = 0.12

    # 3. Growth Projections (1 to 5 years compound growth)
    monthly_p = data.monthly_investment_amount
    projections = []
    
    for year in range(1, data.investment_horizon_years + 1):
        n_months = year * 12
        # Future value formula for monthly recurring investment
        r_monthly = expected_annual_return / 12
        
        # Base Scenario
        fv_base = monthly_p * (((1 + r_monthly)**n_months - 1) / r_monthly) * (1 + r_monthly)
        # Bull Scenario (+3% annual return)
        r_bull = (expected_annual_return + 0.03) / 12
        fv_bull = monthly_p * (((1 + r_bull)**n_months - 1) / r_bull) * (1 + r_bull)
        # Bear Scenario (-3% annual return)
        r_bear = max(0.02, (expected_annual_return - 0.03)) / 12
        fv_bear = monthly_p * (((1 + r_bear)**n_months - 1) / r_bear) * (1 + r_bear)
        
        projections.append({
            "year": year,
            "total_invested": round(monthly_p * n_months),
            "base_scenario": round(fv_base),
            "bull_scenario": round(fv_bull),
            "bear_scenario": round(fv_bear)
        })

    return {
        "gate_status": "READY",
        "financial_dna": risk_bucket,
        "category_recommendation": recommended_category,
        "assumed_annual_return": f"{expected_annual_return * 100}%",
        "projections": projections,
        "disclaimer": "Illustrative scenario based on assumptions. Not a guaranteed return."
    }