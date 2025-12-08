import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)
from typing import List, Dict, Union, Any

def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate regression metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary containing MAE, RMSE, and MAPE
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    
    # Handle divide by zero for MAPE
    with np.errstate(divide='ignore', invalid='ignore'):
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        mape = np.nan_to_num(mape, nan=0.0, posinf=0.0, neginf=0.0)
        
    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    }

def calculate_classification_metrics(y_true: List[Any], y_pred: List[Any], labels: List[Any] = None) -> Dict[str, Any]:
    """
    Calculate classification metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: check for specific labels
        
    Returns:
        Dictionary containing Accuracy and per-class Precision, Recall, F1
    """
    accuracy = accuracy_score(y_true, y_pred)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    
    # If labels are not provided, infer them from the data
    if labels is None:
        labels = sorted(list(set(y_true) | set(y_pred)))
        
    per_class_metrics = {}
    for i, label in enumerate(labels):
        if i < len(precision):
             per_class_metrics[str(label)] = {
                "precision": precision[i],
                "recall": recall[i],
                "f1": f1[i]
            }
            
    return {
        "accuracy": accuracy,
        "per_class": per_class_metrics
    }

def get_confusion_matrix_df(y_true: List[Any], y_pred: List[Any], labels: List[Any] = None) -> pd.DataFrame:
    """
    Generate a confusion matrix as a Pandas DataFrame.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: check for specific labels
    
    Returns:
        Pandas DataFrame representing the confusion matrix
    """
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    if labels is None:
        labels = sorted(list(set(y_true) | set(y_pred)))
        
    return pd.DataFrame(cm, index=labels, columns=labels)


# Recommender Metrics

def precision_at_k(recommended_list: List[Any], relevant_set: set, k: int) -> float:
    """
    Calculate Precision@K.
    
    Args:
        recommended_list: List of recommended items (ordered)
        relevant_set: Set of relevant items
        k: Number of items to consider
        
    Returns:
        Precision@K score
    """
    recommended_k = recommended_list[:k]
    if not recommended_k:
        return 0.0
        
    num_relevant = sum(1 for item in recommended_k if item in relevant_set)
    return num_relevant / len(recommended_k)

def recall_at_k(recommended_list: List[Any], relevant_set: set, k: int) -> float:
    """
    Calculate Recall@K.
    
    Args:
        recommended_list: List of recommended items (ordered)
        relevant_set: Set of relevant items
        k: Number of items to consider
        
    Returns:
        Recall@K score
    """
    if not relevant_set:
        return 0.0
    
    recommended_k = recommended_list[:k]
    num_relevant = sum(1 for item in recommended_k if item in relevant_set)
    return num_relevant / len(relevant_set)

def ndcg_at_k(recommended_list: List[Any], relevant_set: set, k: int) -> float:
    """
    Calculate NDCG@K assuming binary relevance (1 for relevant, 0 for not).
    
    Args:
        recommended_list: List of recommended items (ordered)
        relevant_set: Set of relevant items
        k: Number of items to consider
        
    Returns:
        NDCG@K score
    """
    recommended_k = recommended_list[:k]
    if not recommended_k:
        return 0.0
        
    dcg = 0.0
    for i, item in enumerate(recommended_k):
        if item in relevant_set:
            dcg += 1.0 / np.log2(i + 2)
            
    # Calculate IDCG
    num_relevant = len(relevant_set)
    # The ideal scenario is that the relevant items are at the top
    # We take the minimum of k and num_relevant because we can only have at most k items in the top k
    ideal_k = min(k, num_relevant)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal_k))
    
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg

# Batch Helpers

def batch_regression_metrics(user_metrics: Dict[Any, Dict[str, float]]) -> pd.DataFrame:
    """
    Aggregate regression metrics across multiple users/instances.
    
    Args:
        user_metrics: Dictionary where keys are user_ids and values are dicts of metrics (MAE, RMSE, MAPE)
        
    Returns:
        DataFrame with average metrics
    """
    df = pd.DataFrame.from_dict(user_metrics, orient='index')
    return df.mean().to_frame().T

def batch_recommender_metrics(
    recommendations: Dict[Any, List[Any]], 
    ground_truth: Dict[Any, set], 
    k: int
) -> Dict[str, float]:
    """
    Calculate average recommender metrics across all users.
    
    Args:
        recommendations: Dict mapping user_id to list of recommended items
        ground_truth: Dict mapping user_id to set of relevant items
        k: Top-k items to consider
        
    Returns:
        Dictionary of average Precision@K, Recall@K, NDCG@K
    """
    precisions = []
    recalls = []
    ndcgs = []
    
    for user_id, recs in recommendations.items():
        if user_id in ground_truth:
            relevant = ground_truth[user_id]
            precisions.append(precision_at_k(recs, relevant, k))
            recalls.append(recall_at_k(recs, relevant, k))
            ndcgs.append(ndcg_at_k(recs, relevant, k))
            
    return {
        f"Precision@{k}": np.mean(precisions) if precisions else 0.0,
        f"Recall@{k}": np.mean(recalls) if recalls else 0.0,
        f"NDCG@{k}": np.mean(ndcgs) if ndcgs else 0.0
    }
