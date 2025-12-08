import numpy as np
import pandas as pd
from evaluation.metrics_core import (
    calculate_regression_metrics,
    calculate_classification_metrics,
    get_confusion_matrix_df,
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
    batch_recommender_metrics
)

def test_regression():
    print("Testing Regression Metrics...")
    y_true = np.array([3, -0.5, 2, 7])
    y_pred = np.array([2.5, 0.0, 2, 8])
    metrics = calculate_regression_metrics(y_true, y_pred)
    print(metrics)
    # Expected: MAE=0.5, RMSE=0.612, MAPE should compute correctly

def test_classification():
    print("\nTesting Classification Metrics...")
    y_true = ["cat", "ant", "cat", "cat", "ant", "bird"]
    y_pred = ["ant", "ant", "cat", "cat", "ant", "cat"]
    metrics = calculate_classification_metrics(y_true, y_pred)
    print(metrics)
    cm = get_confusion_matrix_df(y_true, y_pred)
    print("Confusion Matrix:\n", cm)

def test_recommender():
    print("\nTesting Recommender Metrics...")
    recommended = ['a', 'b', 'c', 'd', 'e']
    relevant = {'a', 'c', 'x'}
    
    p3 = precision_at_k(recommended, relevant, 3) # a, b, c -> 2/3
    r3 = recall_at_k(recommended, relevant, 3)    # a, b, c -> 2/3 (relevant has 3)
    n3 = ndcg_at_k(recommended, relevant, 3)      # 1 + 0 + 1/log2(4) -> normalized
    
    print(f"P@3: {p3}, R@3: {r3}, NDCG@3: {n3}")
    
    # Test batch
    recs = {1: ['a', 'b'], 2: ['x', 'y']}
    rel = {1: {'a'}, 2: {'z'}}
    batch = batch_recommender_metrics(recs, rel, 2)
    print("Batch:", batch)

if __name__ == "__main__":
    test_regression()
    test_classification()
    test_recommender()
