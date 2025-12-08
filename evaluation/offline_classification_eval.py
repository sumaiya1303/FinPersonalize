import argparse
import pandas as pd
import sys
import os

# Ensure the parent directory is in the path to import evaluation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.metrics_core import calculate_classification_metrics, get_confusion_matrix_df

def main():
    parser = argparse.ArgumentParser(description='Offline Classification Evaluation')
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the prediction CSV file')
    parser.add_argument('--true_col', type=str, required=True, help='Column name for true labels')
    parser.add_argument('--pred_col', type=str, required=True, help='Column name for predicted labels')
    
    args = parser.parse_args()
    
    try:
        df = pd.read_csv(args.csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {args.csv_path}")
        sys.exit(1)
        
    print(f"Loading data from {args.csv_path}...")
    print(f"Evaluating Classification Metrics (True: '{args.true_col}', Pred: '{args.pred_col}')")
    
    try:
        y_true = df[args.true_col].tolist()
        y_pred = df[args.pred_col].tolist()
    except KeyError as e:
        print(f"Error: Column {e} not found in CSV.")
        sys.exit(1)
        
    metrics = calculate_classification_metrics(y_true, y_pred)
    cm_df = get_confusion_matrix_df(y_true, y_pred)
    
    print("\n" + "="*60)
    print(f"Overall Accuracy: {metrics['accuracy']:.4f}")
    print("-" * 60)
    print("Per-Class Metrics:")
    print(f"{'Class':<15} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 60)
    
    for label, scores in metrics['per_class'].items():
        print(f"{label:<15} | {scores['precision']:<10.4f} | {scores['recall']:<10.4f} | {scores['f1']:<10.4f}")
        
    print("="*60)
    print("\nConfusion Matrix:")
    print(cm_df)
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
