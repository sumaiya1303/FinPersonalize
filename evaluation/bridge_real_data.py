import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import create_app, db
from app.models import Transaction

def get_date_range(base_date):
    """
    Determine Test Month and Train Window based on the base_date (latest transaction).
    Test Month: Full month of base_date.
    Train Window: 3 months prior to Test Month.
    """
    # Test Month: 1st day of the month of base_date to the last day
    test_start = base_date.replace(day=1)
    test_end = test_start + relativedelta(months=1) - timedelta(days=1)
    
    # Train Window: 3 months before test_start
    train_start = test_start - relativedelta(months=3)
    train_end = test_start - timedelta(days=1)
    
    return train_start, train_end, test_start, test_end

def main():
    app = create_app()
    with app.app_context():
        # 1. Find Anchor Date (Max Date)
        max_date_query = db.session.query(func.max(Transaction.date)).scalar()
        
        if not max_date_query:
            print("Error: No data found in Transaction table.")
            sys.exit(1)
            
        # Ensure max_date is a datetime object. It might be a string or date depending on DB.
        if isinstance(max_date_query, str):
            max_date = datetime.strptime(max_date_query, '%Y-%m-%d').date()
        else:
            max_date = max_date_query
            
        print(f"Latest Transaction Date: {max_date}")
        
        # 2. Define Windows
        train_start, train_end, test_start, test_end = get_date_range(max_date)
        
        print(f"Test Window:  {test_start} to {test_end}")
        print(f"Train Window: {train_start} to {train_end}")
        
        # 3. Validation: Check if history exists
        min_date_query = db.session.query(func.min(Transaction.date)).scalar()
        if isinstance(min_date_query, str):
            min_date = datetime.strptime(min_date_query, '%Y-%m-%d').date()
        else:
            min_date = min_date_query
            
        if min_date > train_start:
            print(f"Warning: Not enough history to run forecasting test.")
            print(f"Required Start: {train_start}, Available Start: {min_date}")
            sys.exit(0)
            
        # 4. Fetch Data
        query = db.session.query(Transaction.date, Transaction.amount, Transaction.category)
        results = query.all()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=['date', 'amount', 'category'])
        
        # specific handling if dates in df are strings
        df['date'] = pd.to_datetime(df['date'])
        
        # Convert boundaries to pandas Timestamp for comparison
        train_start_ts = pd.to_datetime(train_start)
        train_end_ts = pd.to_datetime(train_end)
        test_start_ts = pd.to_datetime(test_start)
        test_end_ts = pd.to_datetime(test_end)
        
        train_df = df[(df['date'] >= train_start_ts) & (df['date'] <= train_end_ts)]
        test_df = df[(df['date'] >= test_start_ts) & (df['date'] <= test_end_ts)]
        
        print(f"Train Records: {len(train_df)}")
        print(f"Test Records:  {len(test_df)}")
        
        if train_df.empty:
            print("Error: Train set is empty despite date validation.")
            sys.exit(1)
            
        if test_df.empty:
            print("Error: Test set is empty.")
            # This is possible if max_date exists but the month is otherwise empty? 
            # Or if max_date is the only record?
            # We proceed anyway if we derived windows from max_date, likely there is at least one record.
            sys.exit(1)

        # 5. Execute Forecast Logic
        # Calculate monthly average spending per category in Train Set
        # First, sum per month per category
        train_df['month'] = pd.to_datetime(train_df['date']).dt.to_period('M')
        monthly_spend = train_df.groupby(['category', 'month'])['amount'].sum().reset_index()
        
        # Then average across the 3 months (dividing by 3 assumes we want specific monthly average. 
        # Or we can just take the mean of the sums we found. 
        # If a category appears in only 1 month, should we div by 3 or 1?
        # Requirement: "Calculate avg_spend per category from the Train Set."
        # Standard aproach: Average monthly spend.
        avg_forecast = monthly_spend.groupby('category')['amount'].mean().reset_index()
        avg_forecast.rename(columns={'amount': 'predicted_spending'}, inplace=True)
        
        # Actual spend in Test Set (Sum for the whole month)
        actual_spend = test_df.groupby('category')['amount'].sum().reset_index()
        actual_spend.rename(columns={'amount': 'actual_spending'}, inplace=True)
        
        # Merge
        comparison = pd.merge(actual_spend, avg_forecast, on='category', how='outer').fillna(0)
        
        # 6. Export
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'evaluation_samples')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'real_spending_forecast.csv')
        
        comparison.to_csv(output_path, index=False)
        print(f"\nForecast exported to: {output_path}")
        print("\nSample Results:")
        print(comparison.head())

if __name__ == "__main__":
    main()
