import argparse
import pandas as pd
import sys
import os

# Ensure the parent directory is in the path to import evaluation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.metrics_core import calculate_regression_metrics

def main():
    parser = argparse.ArgumentParser(description='Offline Regression Evaluation')
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the prediction CSV file')
    parser.add_argument('--true_col', type=str, required=True, help='Column name for actual values')
    parser.add_argument('--pred_col', type=str, required=True, help='Column name for predicted values')
    
    args = parser.parse_args()
    
    try:
        df = pd.read_csv(args.csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {args.csv_path}")
        sys.exit(1)
        
    print(f"Loading data from {args.csv_path}...")
    print(f"Evaluating Regression Metrics (True: '{args.true_col}', Pred: '{args.pred_col}')")
    
    try:
        y_true = df[args.true_col].values
        y_pred = df[args.pred_col].values
    except KeyError as e:
        print(f"Error: Column {e} not found in CSV.")
        sys.exit(1)
        
    metrics = calculate_regression_metrics(y_true, y_pred)
    
    print("\n" + "="*40)
    print(f"{'Metric':<20} | {'Value':<15}")
    print("-" * 40)
    for metric, value in metrics.items():
        print(f"{metric:<20} | {value:<15.4f}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
