import pandas as pd
import numpy as np
import pickle
from sklearn.decomposition import TruncatedSVD
from app import create_app, db
from app.models import Product
import os

app = create_app()

def train_svd():
    with app.app_context():
        # 1. Fetch Real Products
        products = Product.query.all()
        if not products:
            print("No products found! Run seed_products.py first.")
            return

        product_ids = [p.id for p in products]
        print(f"Found {len(products)} products.")

        # 2. Generate Synthetic Interactions
        # Create a matrix of zeros (User ID x Product ID)
        num_users = 100
        num_products = len(products)
        
        # Initialize zero matrix
        interaction_matrix = np.zeros((num_users, num_products))
        
        # Randomly fill 10% of the cells with '1'
        # We'll do this by iterating or using random indices, but let's do it simply
        # while respecting the bias requirements.
        
        # First, apply random noise (10% fill rate base)
        # We'll just iterate through users to apply logic
        
        for user_id in range(num_users):
            # Determine user profile based on ID
            # Users 0-30: Safe profiles
            # Users 70-100: Risky profiles
            # Others: Random/Mixed
            
            for i, product in enumerate(products):
                # Base probability
                prob = 0.10 
                
                # Apply Bias
                is_savings = 'Savings' in product.category or (product.tags and 'Savings' in product.tags)
                is_crypto = 'Crypto' in product.category or (product.tags and 'Crypto' in product.tags)
                is_etf = 'ETF' in product.category or (product.tags and 'ETF' in product.tags)
                
                if 0 <= user_id <= 30: # Safe profiles
                    if is_savings:
                        prob = 0.80 # High chance for savings
                    elif is_crypto or is_etf:
                        prob = 0.01 # Very low chance for risky
                        
                elif 70 <= user_id < 100: # Risky profiles
                    if is_crypto or is_etf:
                        prob = 0.80 # High chance for risky
                    elif is_savings:
                        prob = 0.05 # Low chance for savings
                
                # Assign interaction based on probability
                if np.random.rand() < prob:
                    interaction_matrix[user_id, i] = 1

        # Create DataFrame
        df = pd.DataFrame(interaction_matrix, columns=product_ids)
        print(f"Generated Interaction Matrix: {df.shape}")

        # 3. Train the Model
        print("Training TruncatedSVD...")
        n_components = 12
        # Ensure n_components is valid
        if num_products <= n_components:
             n_components = num_products - 1
             
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        user_factors = svd.fit_transform(df)
        
        explained_variance = svd.explained_variance_ratio_.sum()
        print(f"Explained Variance: {explained_variance:.2f}")

        # 4. Serialize
        # Save to backend/svd_model.pkl
        output_path = os.path.join(os.path.dirname(__file__), 'svd_model.pkl')
        
        model_data = {
            'svd_model': svd,
            'product_columns': product_ids, # List of Product IDs
            'user_factors': user_factors
        }

        with open(output_path, 'wb') as f:
            pickle.dump(model_data, f)

        print('Model trained and saved successfully.')

if __name__ == '__main__':
    train_svd()
