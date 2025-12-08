import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split as sklearn_train_test_split

def generate_synthetic_data(n_users=1000, n_items=50):
    """
    Generates a synthetic interaction matrix.
    Logic:
    - Users 0-500 prefer items 0-25 (Prob 0.15)
    - Users 500-1000 prefer items 25-50 (Prob 0.15)
    - Background noise (Prob 0.01)
    """
    np.random.seed(42)
    matrix = np.zeros((n_users, n_items))
    
    for u in range(n_users):
        for i in range(n_items):
            prob = 0.01 # Base noise
            
            # Add Bias
            if u < 500 and i < 25:
                prob = 0.15
            elif u >= 500 and i >= 25:
                prob = 0.15
                
            if np.random.rand() < prob:
                matrix[u, i] = 1
                
    return matrix

def train_test_split_matrix(interaction_matrix):
    """
    Masks 20% of the 1s as Test Set.
    Returns: Train Matrix (with 0s for test items), Test Dictionary {user_idx: {item_indices}}
    """
    np.random.seed(42)
    train_matrix = interaction_matrix.copy()
    test_set = {}
    
    users, items = np.nonzero(interaction_matrix)
    
    # We will pick 20% of these interactions to hide
    total_interactions = len(users)
    n_test = int(total_interactions * 0.2)
    
    # Randomly choose indices
    test_indices = np.random.choice(range(total_interactions), n_test, replace=False)
    
    for idx in test_indices:
        u, i = users[idx], items[idx]
        train_matrix[u, i] = 0 # Hide it
        
        if u not in test_set:
            test_set[u] = set()
        test_set[u].add(i)
        
    return train_matrix, test_set

def evaluate_recommender():
    # 1. Generate Data
    n_users = 1000
    n_items = 50
    interactions = generate_synthetic_data(n_users, n_items)
    
    # 2. Split
    train_matrix, test_dict = train_test_split_matrix(interactions)
    
    # 3. Train SVD
    # We use a modest number of components
    svd = TruncatedSVD(n_components=20, random_state=42)
    svd.fit(train_matrix)
    
    # 4. Predict & Evaluate
    p3_sum, r3_sum = 0, 0
    p5_sum, r5_sum = 0, 0
    all_recs_set = set() # For coverage
    
    # Pre-calculate user factors to speed up (approx) or just transform all
    user_factors = svd.transform(train_matrix)
    item_factors = svd.components_
    
    # Evaluated users count (only those with test items)
    eval_users_count = len(test_dict)
    
    for u_idx, hidden_items in test_dict.items():
        # Predict scores for THIS user
        # Dot product of this user's latent factors and all item factors
        u_vector = user_factors[u_idx]
        scores = np.dot(u_vector, item_factors)
        
        # We must filter out items already in TRAIN so we don't recommend what is already known
        # Set train items score to -inf
        known_items = np.where(train_matrix[u_idx] > 0)[0]
        scores[known_items] = -np.inf
        
        # Get Top-5 indices
        top_5 = scores.argsort()[::-1][:5]
        top_3 = top_5[:3]
        
        all_recs_set.update(top_5)
        
        # -- Metrics @ 3 --
        hits_3 = len(set(top_3) & hidden_items)
        p3_sum += hits_3 / 3.0
        r3_sum += hits_3 / len(hidden_items)
        
        # -- Metrics @ 5 --
        hits_5 = len(set(top_5) & hidden_items)
        p5_sum += hits_5 / 5.0
        r5_sum += hits_5 / len(hidden_items)
    
    # 5. Aggregate
    avg_p3 = p3_sum / eval_users_count
    avg_r3 = r3_sum / eval_users_count
    avg_p5 = p5_sum / eval_users_count
    avg_r5 = r5_sum / eval_users_count
    
    coverage = len(all_recs_set) / n_items
    
    # 6. Output
    print(f"===================================================")
    print(f"SYNTHETIC RECOMMENDER PERFORMANCE ({n_users} Users)")
    print(f"===================================================")
    print(f"| Metric        | Score  | Description            |")
    print(f"|---------------|--------|------------------------|")
    print(f"| Precision@3   | {avg_p3:.4f} | Relevant items in Top-3|")
    print(f"| Recall@3      | {avg_r3:.4f} | % of items found       |")
    print(f"| Precision@5   | {avg_p5:.4f} | Relevant items in Top-5|")
    print(f"| Recall@5      | {avg_r5:.4f} | % of items found       |")
    print(f"| Coverage      | {coverage:.4f} | % Catalog Recommended  |")
    print(f"===================================================")

if __name__ == "__main__":
    evaluate_recommender()
