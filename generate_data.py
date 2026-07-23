import pandas as pd
from faker import Faker
import random
import os

# Initialize Faker with an Indian locale for realistic names and cities
fake = Faker('en_IN')

def generate_synthetic_data(num_profiles=200):
    data = []
    
    for _ in range(num_profiles):
        # 1. Basic Demographics
        user_id = fake.uuid4()
        name = fake.name()
        city = fake.city()
        age = random.randint(18, 55)
        monthly_income = random.randint(10000, 50000) # Target audience: gig workers, small merchants
        
        # 2. Alternative Digital Trust Signals
        avg_mobile_recharge = random.choice([199, 299, 499, 699, 999])
        recharge_frequency_days = random.randint(20, 35)
        
        # Utility payment delays (in days) - lower is better
        utility_payment_delay_days = random.randint(0, 45) 
        
        # E-commerce transaction volume (monthly)
        ecom_transaction_volume = random.randint(500, 10000)
        
        # E-commerce return rate (percentage) - lower is better
        ecom_return_rate = round(random.uniform(0, 0.4), 2)
        
        # 3. Target Variable: credit_reliability (0 to 100)
        # We engineer this so the ML model has logical patterns to learn.
        # Start with a baseline score of 80
        base_score = 80
        
        # Penalize for late utility payments
        delay_penalty = (utility_payment_delay_days / 45) * 30 
        
        # Penalize for high e-commerce return rates
        return_penalty = (ecom_return_rate / 0.4) * 20
        
        # Reward consistent, timely recharges (closer to 28-30 days is standard)
        if 25 <= recharge_frequency_days <= 31:
            recharge_bonus = 10
        else:
            recharge_bonus = 0
            
        # Calculate final target score
        credit_reliability = round(base_score - delay_penalty - return_penalty + recharge_bonus)
        
        # Cap the score between 0 and 100
        credit_reliability = max(0, min(100, credit_reliability))
        
        data.append({
            "user_id": user_id,
            "name": name,
            "city": city,
            "age": age,
            "monthly_income": monthly_income,
            "avg_mobile_recharge": avg_mobile_recharge,
            "recharge_frequency_days": recharge_frequency_days,
            "utility_payment_delay_days": utility_payment_delay_days,
            "ecom_transaction_volume": ecom_transaction_volume,
            "ecom_return_rate": ecom_return_rate,
            "credit_reliability": credit_reliability
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating synthetic data for FinLens AI...")
    
    # Generate 200 profiles as required
    df = generate_synthetic_data(200)
    
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save as JSON to match your MVP architecture
    output_path = "data/mockData.json"
    df.to_json(output_path, orient="records", indent=4)
    
    # Also save as CSV for easier ML model training later
    df.to_csv("data/mockData.csv", index=False)
    
    print(f"Success! Generated {len(df)} user profiles.")
    print(f"Data saved to {output_path} and data/mockData.csv")