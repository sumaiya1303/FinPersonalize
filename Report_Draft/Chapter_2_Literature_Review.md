# Chapter 2: Literature Review

## 2.1 Overview

The development of a hyper-personalized financial product engine sits at the intersection of three distinct but increasingly converging fields: **Recommender Systems**, **Generative Artificial Intelligence (GenAI)**, and **Behavioral Finance**. To build a system that is both technically robust and socially impactful, one must understand the historical evolution and theoretical underpinnings of each of these domains. This chapter provides a comprehensive review of the foundational literature, tracing the evolution of Collaborative Filtering, the rise of Retrieval-Augmented Generation (RAG), and the psychological frameworks of "Money Scripts" that guide financial decision-making.

## 2.2 Recommender Systems in Finance

Recommender systems have become the invisible engine of the digital economy. In the financial sector, however, the application of these systems presents unique challenges due to data sparsity, regulatory constraints, and the high stakes of the recommendations.

### 2.2.1 Collaborative Filtering vs. Content-Based Filtering
Broadly, recommender systems fall into two categories:
1.  **Content-Based Filtering (CBF)**: This approach recommends items similar to those a user liked in the past. It relies on item features (e.g., "High Yield," "No Fees"). If a user views a "Tech ETF," the system recommends another "Tech ETF."
    *   *Pros*: No cold start for items; transparent logic.
    *   *Cons*: Limited serendipity; users are trapped in a "filter bubble."
2.  **Collaborative Filtering (CF)**: This approach relies on the wisdom of the crowd. It assumes that users who agreed in the past will agree in the future.
    *   *Pros*: Capable of discovering latent interests (serendipity).
    *   *Cons*: Suffers acutely from the **Cold Start Problem** for new users.

### 2.2.2 Matrix Factorization (SVD): The Mathematical Foundation
The field was revolutionized by the **Netflix Prize** competition, which popularized **Matrix Factorization (MF)** techniques. **Koren et al. [1]** demonstrated that mapping users and items to a joint latent factor space allows for superior prediction accuracy.

**Singular Value Decomposition (SVD)** is the premier method for this. It decomposes the user-item interaction matrix $R$ into three matrices:
$$ R = U \Sigma V^T $$
However, in the context of recommender systems with sparse data, we typically use an approximation method that minimizes the regularized squared error on the set of known ratings. We approximate $R$ as the product of two lower-rank matrices, User Factors ($P$) and Item Factors ($Q$):
$$ \hat{r}_{ui} = q_i^T p_u $$

**The Optimization Problem**:
To learn the factor vectors $p_u$ and $q_i$, the system minimizes the regularized squared error:
$$ \min_{p*, q*} \sum_{(u,i) \in \mathcal{K}} (r_{ui} - q_i^T p_u)^2 + \lambda (||q_i||^2 + ||p_u||^2) $$
Where:
*   $\mathcal{K}$ is the set of known ratings.
*   $r_{ui}$ is the actual rating.
*   $\lambda$ is the regularization parameter (to prevent overfitting).
*   $||q_i||^2 + ||p_u||^2$ is the penalty term for model complexity.

This mathematical rigor allows SVD to infer hidden attributes. For example, a latent factor might represent "Risk Tolerance." Even if a user never explicitly states they like risky assets, if they interact with products that have a high "Risk" factor in matrix $Q$, the model predicts a high affinity. This capability is crucial for our project's goal of hyper-personalization.

## 2.3 Generative AI and Retrieval-Augmented Generation (RAG)

The second pillar of this project is the "Explanation Engine." While Recommender Systems provide the *what*, Generative AI provides the *why*.

### 2.3.1 The Hallucination Problem in LLMs
Large Language Models (LLMs) like GPT-4 [9] are trained on vast corpora of text. They are excellent at pattern matching and fluency but lack a concept of "truth." **Lewis et al. [2]** identified that LLMs often "hallucinate"—confidently stating falsehoods when they lack specific knowledge. In finance, this is unacceptable. An LLM cannot be trusted to "remember" the specific interest rate of a user's savings account from its pre-training data.

### 2.3.2 Retrieval-Augmented Generation (RAG) Architecture
To solve this, Lewis et al. proposed **RAG**. RAG is a hybrid architecture that combines a **parametric memory** (the pre-trained Transformer) with a **non-parametric memory** (a searchable vector index of documents).

**The RAG Workflow in this Project**:
1.  **Retrieval**: When a user asks a question, the system first queries a "Knowledge Base" (our SQLite database and Product Catalog). It retrieves the top-$k$ relevant snippets (e.g., the user's last 5 transactions, the specific terms of the recommended loan).
2.  **Augmentation**: These snippets are injected into the prompt context.
    *   *Prompt*: "You are a financial assistant. Answer the user's question using ONLY the following context: [Retrieved Data]."
3.  **Generation**: The LLM generates the response based on this grounded truth.

This architecture ensures that the AI's advice is always factually accurate and personalized to the user's real-time data, effectively bridging the "Trust Gap."

## 2.4 Behavioral Finance: The Psychology of Money

The technology developed in this project is not an end in itself but a means to improve financial well-being. To do so effectively, it must account for the psychology of the user.

### 2.4.1 Money Scripts (Klontz & Klontz)
**Dr. Brad Klontz**, a leading figure in financial psychology, introduced the concept of **"Money Scripts"** [3]—unconscious, trans-generational beliefs about money that drive financial behavior. Klontz identifies four primary scripts:
1.  **Money Avoidance**: Belief that money is bad or that rich people are greedy. Users with this script may sabotage their own financial success or ignore statements.
    *   *System Adaptation*: The AI should use gentle, non-threatening language and focus on "financial health" rather than "wealth accumulation."
2.  **Money Worship**: Belief that more money will solve all of life's problems. These users are prone to overspending and buying things to fill a void.
    *   *System Adaptation*: The AI should focus on long-term value and "cooling off" periods for purchases.
3.  **Money Status**: Belief that self-worth is equal to net worth. These users may overspend on luxury goods to impress others.
    *   *System Adaptation*: The AI can gamify savings, making "saving" a status symbol (e.g., "You are in the top 10% of savers").
4.  **Money Vigilance**: Alert, watchful, and concerned about financial health. These users are good savers but may be anxious about spending.
    *   *System Adaptation*: The AI should provide reassurance and data-backed validation of their security.

By integrating these psychological profiles into the "User Persona," our system moves beyond simple math. A recommendation is not just a product match; it is a psychological intervention designed to resonate with the user's core beliefs.

### 2.4.2 Just-in-Time Education
**Fernandes et al. [4]** argued that traditional financial education (classroom lectures) has a negligible effect on behavior because knowledge decays. They advocate for **"Just-in-Time"** education—information provided exactly when a decision is being made. Our RAG Chatbot implements this by explaining financial concepts *at the moment of the transaction*, maximizing retention and impact.
