import argparse
import pandas as pd
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Advice Scenarios Evaluation')
    parser.add_argument(
        '--csv_path', 
        type=str, 
        default=os.path.join('data', 'evaluation_samples', 'advice_ratings.csv'),
        help='Path to the ratings CSV file'
    )
    
    args = parser.parse_args()
    
    try:
        df = pd.read_csv(args.csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {args.csv_path}")
        sys.exit(1)
        
    print(f"Loading ratings from {args.csv_path}...")
    
    expected_cols = ['scenario_id', 'correctness_score', 'personalization_score', 'actionability_score']
    if not all(col in df.columns for col in expected_cols):
        print(f"Error: CSV must contain columns: {expected_cols}")
        print(f"Found: {list(df.columns)}")
        sys.exit(1)
        
    # Group by scenario_id and calculate average scores
    scenario_metrics = df.groupby('scenario_id')[['correctness_score', 'personalization_score', 'actionability_score']].mean()
    
    # Calculate Global Average
    global_metrics = df[['correctness_score', 'personalization_score', 'actionability_score']].mean()
    
    print("\n" + "="*60)
    print("ADVICE SCENARIOS EVALUATION REPORT")
    print("="*60)
    
    print("\nGlobal Averages:")
    print("-" * 60)
    print(f"Overall Correctness Score:      {global_metrics['correctness_score']:.2f}/5")
    print(f"Overall Personalization Score:  {global_metrics['personalization_score']:.2f}/5")
    print(f"Overall Actionability Score:    {global_metrics['actionability_score']:.2f}/5")
    
    print("\n" + "-" * 60)
    print("Per-Scenario Analysis:")
    print("-" * 60)
    print(f"{'Scenario ID':<15} | {'Correct':<8} | {'Personal':<8} | {'Action':<8}")
    print("-" * 60)
    
    for scenario_id, row in scenario_metrics.iterrows():
        print(f"{scenario_id:<15} | {row['correctness_score']:<8.2f} | {row['personalization_score']:<8.2f} | {row['actionability_score']:<8.2f}")
        
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
