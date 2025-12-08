# Evaluation Framework

This directory contains the offline and online evaluation metrics for the Thesis project. The framework covers Regression, Classification, Recommender Systems, Chatbot Advice Scenarios, and API Latency.

## Dependencies

Ensure you have the following Python packages installed:

- `pandas`
- `numpy`
- `scikit-learn`
- `requests`

You can install them via pip:
```bash
pip install pandas numpy scikit-learn requests
```

## Running the Evaluation Scripts

Below are the exact commands to run each evaluation script using the provided sample data.

### 1. Regression Evaluation
Evaluates regression models (e.g., Savings Prediction) using MAE, RMSE, and MAPE.

```bash
python evaluation/offline_regression_eval.py --csv_path data/evaluation_samples/regression_predictions.csv --true_col actual_savings --pred_col predicted_savings
```

### 2. Classification Evaluation
Evaluates classification models (e.g., Risk Assessment) using Accuracy, Precision, Recall, F1, and Confusion Matrix.

```bash
python evaluation/offline_classification_eval.py --csv_path data/evaluation_samples/classification_predictions.csv --true_col actual_risk --pred_col predicted_risk
```

### 3. Recommender Evaluation
Evaluates recommender systems using Precision@K, Recall@K, and NDCG@K.

```bash
python evaluation/offline_recommender_eval.py --interactions_csv data/evaluation_samples/recommender_interactions.csv --recommendations_csv data/evaluation_samples/recommender_recommendations.csv --k 5
```

### 4. Advice Scenarios Evaluation
Aggregates human ratings for the Chatbot's advice quality (Correctness, Personalization, Actionability).

```bash
python evaluation/advice_scenarios_eval.py
```

### 5. Latency Evaluation
Tests the API performance by measuring response times (Mean, Median, P95).

```bash
python evaluation/latency_eval.py --requests 20
```
