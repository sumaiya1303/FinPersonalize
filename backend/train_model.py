import pandas as pd
import numpy as np
import pickle
from sklearn.decomposition import TruncatedSVD

# 1. Create Mock Interaction Matrix (Users x Products)
# Rows: Users (0-4), Cols: Products
products = [
    'High Yield Savings', 'Debt Consolidation', 'Budgeting Tool', 
    'Index Fund ETF', 'Crypto Wallet', 'Robo-Advisor', 
    'Credit Builder Card', 'Emergency Fund Account'
]

# 0 = No interaction, 1 = Viewed/Used
data = [
    [1, 0, 1, 0, 0, 0, 0, 1], # User 0 (Saver)
    [0, 1, 1, 0, 0, 0, 1, 0], # User 1 (Debtor)
    [1, 0, 0, 1, 1, 1, 0, 0], # User 2 (Investor - High Risk)
    [1, 0, 1, 1, 0, 1, 0, 1], # User 3 (Balanced)
    [0, 0, 0, 0, 1, 0, 0, 0]  # User 4 (Crypto only)
]

df = pd.DataFrame(data, columns=products)

print("Training SVD Model...")
# 2. Train SVD Model
svd = TruncatedSVD(n_components=3, random_state=42)
user_features = svd.fit_transform(df)

# 3. Save Model and Product List
model_data = {
    'svd_model': svd,
    'products': products,
    'user_features': user_features, # In real app, we'd re-compute this for the active user
    'interaction_matrix': df
}

with open('svd_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("Model saved to svd_model.pkl")
