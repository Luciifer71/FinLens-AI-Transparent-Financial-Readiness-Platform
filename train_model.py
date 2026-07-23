import pandas as pd
import numpy as np
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# 1. Load the synthetic dataset created in Phase 1
df = pd.read_csv("data/mockData.csv")

# 2. Define Features (X) and Target Variable (y)
feature_cols = [
    "monthly_income",
    "avg_mobile_recharge",
    "recharge_frequency_days",
    "utility_payment_delay_days",
    "ecom_transaction_volume",
    "ecom_return_rate"
]

X = df[feature_cols]
y = df["credit_reliability"]

# 3. Split into Training and Testing Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train Random Forest Regressor
print("Training Random Forest model for Credit Reliability Scoring...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model performance
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Model Accuracy (R² Score) -> Train: {train_score:.2f}, Test: {test_score:.2f}")

# 5. Save the trained model to disk
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/credit_model.pkl")
print("Model saved to models/credit_model.pkl")

# 6. Initialize and Save SHAP TreeExplainer
explainer = shap.TreeExplainer(model)
joblib.dump(explainer, "models/shap_explainer.pkl")
print("SHAP Explainer saved to models/shap_explainer.pkl")


# 7. SHAP to Human Language Rule Engine
def explain_user_score(user_data_dict):
    """
    Takes a single user profile, calculates SHAP values, 
    and returns top 3 drivers in plain language.
    """
    input_df = pd.DataFrame([user_data_dict])[feature_cols]
    
    # Predict score
    predicted_score = round(model.predict(input_df)[0])
    
    # Compute SHAP values
    shap_values = explainer(input_df)
    values = shap_values.values[0]
    
    # Pair feature names with their exact SHAP impact
    feature_impacts = []
    for name, impact in zip(feature_cols, values):
        feature_impacts.append({"feature": name, "impact": impact})
        
    # Sort features by highest absolute impact
    feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
    top_3 = feature_impacts[:3]
    
    # Educational human-readable advice dictionary
    feedback_rules = {
        "utility_payment_delay_days": {
            "pos": "Consistent utility bill payments strongly support your digital trust profile.",
            "neg": "Utility payment delays are reducing your score. Paying on time for 2-3 months will boost it."
        },
        "ecom_return_rate": {
            "pos": "Low product return rates demonstrate consistent digital consumer discipline.",
            "neg": "High e-commerce return rates negatively impact trust signals. Reducing returns will improve this."
        },
        "recharge_frequency_days": {
            "pos": "Regular mobile recharge intervals show routine financial discipline.",
            "neg": "Irregular recharge patterns slightly lower your routine stability signals."
        },
        "avg_mobile_recharge": {
            "pos": "Consistent mobile spend reflects healthy economic participation.",
            "neg": "Lower mobile transaction history provides fewer trust data points."
        },
        "ecom_transaction_volume": {
            "pos": "Active digital transaction volume demonstrates digital readiness.",
            "neg": "Limited digital spending activity provides fewer trust signals."
        },
        "monthly_income": {
            "pos": "Healthy income stability supports overall financial buffer strength.",
            "neg": "Income capacity limits overall financial buffer potential."
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
        "predicted_score": predicted_score,
        "top_3_factors": explanations
    }


# Test script execution on a sample user
if __name__ == "__main__":
    test_user = X.iloc[0].to_dict()
    print("\n--- Testing SHAP Explainability Engine ---")
    result = explain_user_score(test_user)
    print(f"Predicted Credit Reliability Score: {result['predicted_score']}/100")
    print("\nTop 3 Driving Factors (Explainable AI):")
    for idx, factor in enumerate(result['top_3_factors'], 1):
        print(f"{idx}. [{factor['type']}] {factor['plain_text_explanation']} (Impact: {factor['impact_value']})")