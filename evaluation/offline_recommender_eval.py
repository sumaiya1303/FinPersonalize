import argparse
import pandas as pd
import sys
import os
from collections import defaultdict

# Ensure the parent directory is in the path to import evaluation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.metrics_core import batch_recommender_metrics

def main():
    parser = argparse.ArgumentParser(description='Offline Recommender Evaluation')
    parser.add_argument('--interactions_csv', type=str, required=True, help='Path to interactions CSV (user_id, product_id, relevant)')
    parser.add_argument('--recommendations_csv', type=str, required=True, help='Path to recommendations CSV (user_id, product_id, rank)')
    parser.add_argument('--k', type=int, default=5, help='Top K items to evaluate (default: 5)')
    
    args = parser.parse_args()
    
    # Load Data
    try:
        interactions_df = pd.read_csv(args.interactions_csv)
        recommendations_df = pd.read_csv(args.recommendations_csv)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Loading interactions from {args.interactions_csv}...")
    print(f"Loading recommendations from {args.recommendations_csv}...")
    
    # Process Interactions (Ground Truth)
    # Filter for relevant items only (relevant == 1)
    relevant_df = interactions_df[interactions_df['relevant'] == 1]
    ground_truth = defaultdict(set)
    for _, row in relevant_df.iterrows():
        ground_truth[row['user_id']].add(row['product_id'])
        
    # Process Recommendations
    # Sort by rank and group by user
    recommendations_df = recommendations_df.sort_values(by=['user_id', 'rank'])
    recommendations = defaultdict(list)
    for _, row in recommendations_df.iterrows():
        recommendations[row['user_id']].append(row['product_id'])
        
    # Calculate Metrics
    print(f"Evaluating Recommender Metrics @ K={args.k}")
    metrics = batch_recommender_metrics(recommendations, ground_truth, k=args.k)
    
    print("\n" + "="*40)
    print(f"{'Metric':<20} | {'Value':<15}")
    print("-" * 40)
    for metric, value in metrics.items():
        print(f"{metric:<20} | {value:<15.4f}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
