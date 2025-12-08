# Chapter 3: Methodology and System Architecture

## 3.1 System Architecture

The "Hyper-Personalized Financial Product Engine" is architected as a modern, decoupled web application. It follows a **Client-Server** model, utilizing a **React.js** Single Page Application (SPA) for the frontend and a **Flask (Python)** REST API for the backend. This separation of concerns allows for independent scaling and development of the user interface and the computational logic.

### 3.1.1 Technology Stack
The core technology stack was selected to balance performance, developer velocity, and the specific requirements of machine learning integration.

*   **Frontend**: **React.js** (v18) was chosen for its component-based architecture, which is essential for building complex, interactive dashboards. The UI utilizes **Tailwind CSS** for utility-first styling, ensuring a responsive design that works across devices. **Recharts** is used for data visualization (donut charts, bar graphs).
*   **Backend**: **Flask** (v2.3) serves as the application server. Python is the optimal choice here as it natively supports the data science libraries (**NumPy**, **Pandas**, **Scikit-Learn**) required for the Recommender System.
*   **Database**: **SQLite** is used as the relational database management system (RDBMS). While a production system would likely use PostgreSQL, SQLite provides a lightweight, serverless, zero-configuration engine perfect for this prototype. **SQLAlchemy** serves as the Object-Relational Mapper (ORM).
*   **Authentication**: **Google Firebase Authentication** handles user identity. This delegates the complex security requirements of password storage (hashing, salting) to a trusted third-party provider, ensuring that the system never stores raw credentials.

### 3.1.2 System Diagram
[INSERT FIGURE 1: System Architecture Diagram]
*Figure 1 illustrates the data flow: User interactions on the React Client trigger API calls to the Flask Server. The Server authenticates the request via Firebase, queries the SQLite Database, invokes the SVD Model for predictions, or calls the Google Gemini API for RAG-based explanations.*

## 3.2 Data Ingestion Pipeline

A critical challenge in financial modeling is acquiring clean, structured data. Real-world bank statements are often unstructured PDF documents. To address this, a custom Data Ingestion Pipeline was built in `backend/ingest_data.py`.

### 3.2.1 PDF Extraction and Cleaning
The pipeline utilizes the **`pdfplumber`** library to extract raw text from PDF bank statements. The extraction process follows these steps:
1.  **Text Extraction**: The script iterates through each page of the PDF, extracting text line by line.
2.  **Regex Parsing**: A regular expression is used to identify transaction lines. The pattern `(\d{2}/\d{2})\s+(.+?)\s+(-?\d+\.\d{2})` captures the Date, Description, and Amount.
3.  **Merchant Cleaning**: Raw merchant names in bank statements are often noisy (e.g., "VONS #1234 LONG BEACH CA"). A helper function `clean_merchant()` uses Regex to strip store numbers (`#\d+`), city names, and generic prefixes ("POS Purchase"), normalizing "VONS #1234..." to simply "Vons".

### 3.2.2 Categorization Logic
Once the merchant name is cleaned, the `tag_category()` function assigns a category based on keyword matching.
*   **Groceries**: Matches 'vons', 'ralphs', 'whole foods'.
*   **Utilities**: Matches 'edison', 'spectrum', 'water'.
*   **Subscriptions**: Matches 'netflix', 'spotify'.
This rule-based approach ensures that transactions are labeled correctly for downstream analysis.

### 3.2.3 SQL Schema Design
The data is persisted in a normalized SQL schema defined in `backend/app/models.py`:
*   **User**: Stores the `firebase_uid`, `email`, and demographic data.
*   **Transaction**: The core table, storing `date`, `amount`, `category`, `merchant_clean`, and a foreign key to `User`.
*   **MoneyScript**: Stores the psychological profile of the user (`risk_score`, `primary_persona`).
*   **Goal**: Tracks user-defined financial targets (`target_amount`, `target_date`).

### 3.2.4 Dataset Schema
The following table details the schema of the synthetic transaction dataset used for training the Recommender System:

**Table 1: Transaction Dataset Schema**

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `transaction_id` | Integer | Unique identifier for the transaction | `1001` |
| `user_id` | Integer | Foreign key linking to the User table | `42` |
| `date` | Date | The date the transaction occurred | `2023-10-15` |
| `amount` | Float | The value of the transaction (negative for expense) | `-45.50` |
| `category` | String | The high-level category assigned by the system | `Dining` |
| `merchant` | String | The cleaned merchant name | `Starbucks` |
| `description` | String | The raw description from the bank statement | `POS PUR STARBUCKS STORE #123` |

### 3.2.5 Synthetic Data Generation

To rigorously evaluate the system (as detailed in Chapter 5), we generated a large-scale synthetic dataset mimicking real-world banking patterns. This was necessary because obtaining millions of real, labeled banking transactions is not feasible for a student project due to privacy constraints.

The synthetic data generation process, implemented in `evaluate_system.py`, simulates:
1.  **Scale**: **2,000 unique users** and **1,000,000 transactions**. This volume allows us to stress-test the matrix factorization algorithm and ensure low-latency performance.
2.  **Product Catalog**: The catalog was expanded to **50 financial products** (5 real, 45 synthetic) to effectively measure "Top-N" ranking metrics. A small catalog would trivially yield perfect recall; a larger catalog challenges the system to find the "needle in the haystack."
3.  **Behavioral Bias**: To create a "Ground Truth" for accuracy testing, synthetic users were assigned latent risk profiles ('Conservative', 'Aggressive') with probabilistic biases.
    *   *Conservative Users* had an 85% probability of interacting with 'Savings' products and 1% with 'Crypto'.
    *   *Aggressive Users* had a 75% probability of interacting with 'Crypto/ETFs' and 10% with 'Savings'.
    
This known bias allows us to quantitatively measure if the Recommender System successfully "learns" these hidden patterns from the raw transaction matrix alone.
## 3.3 The "Digital Twin" Profiling

To achieve hyper-personalization, the system creates a "Digital Twin" of the user—a digital representation of their financial personality. This is calculated during the Onboarding process.

### 3.3.1 Onboarding Quiz Logic
Upon first login, users complete a psychometric quiz. The answers are processed by `calculate_persona()` in `services.py`. Each answer is assigned a point value corresponding to risk appetite.
*   *Question*: "What would you do if the stock market dropped 20%?"
    *   *Answer*: "Sell everything" (0 points)
    *   *Answer*: "Do nothing" (10 points)
    *   *Answer*: "Buy more" (20 points)

### 3.3.2 Risk Score and Persona Assignment
The system sums these points to calculate a **Risk Score** (0-100). This score is then mapped to a specific **Persona**:
*   **Conservative Protector (Score < 40)**: Users who prioritize capital preservation. The system will filter out high-volatility products for this group.
*   **Balanced Strategist (Score 40-70)**: Users seeking a mix of growth and stability.
*   **Growth Seeker (Score > 70)**: Users willing to accept high volatility for higher returns.
This `primary_persona` is stored in the `MoneyScript` table and dictates the behavior of both the Recommender Engine and the AI Chatbot.

## 3.4 The Hybrid Recommender Engine

The core innovation of this project is the **Hybrid Recommender Engine**, implemented in `services.py`. It employs a "Switching Hybrid" strategy with three distinct layers to ensure robust recommendations for all users.

### 3.4.1 Layer 1: Rule-Based Filtering (The "Health Check")
Before suggesting investment products, the system first checks for fundamental financial health.
*   **Emergency Fund Check**: The system calculates the user's average monthly expenses. If their total savings are less than 3 months of expenses, it *overrides* other recommendations to suggest "High Yield Savings Accounts."
*   **Debt Optimization**: If the system detects more than 5 "Credit Card Payment" transactions in the last 90 days, it prioritizes "Debt Consolidation Loans."
This layer ensures that the advice is *fiscally responsible* before it is *profitable*.

### 3.4.2 Layer 2: Collaborative Filtering (SVD)
For users who pass the health check, the system employs **Singular Value Decomposition (SVD)**.
*   **Model Loading**: The pre-trained model (`svd_model.pkl`) is loaded into memory. This model contains the `user_factors` matrix ($P$) and `item_factors` matrix ($Q$).
*   **Prediction**: The system identifies the user's latent vector based on their Risk Score (mapping real users to synthetic profiles). It then computes the dot product between this user vector and all item vectors.
*   **Ranking**: Products are ranked by their predicted rating. This allows the system to discover non-obvious connections (e.g., "Users like you also invested in Green Energy ETFs").

### 3.4.3 Layer 3: The Risk Filter (Safety Layer)
The final layer is a safety mechanism. The system iterates through the top SVD recommendations and cross-references them with the user's Persona.
*   **Logic**: `if (persona == 'Conservative Protector') and (product.risk_level == 'High'): continue`
This ensures that a conservative user is *never* recommended a high-risk crypto asset, even if the collaborative filtering algorithm predicts a high affinity. This "Safety Layer" is crucial for regulatory compliance and user trust.

## 3.5 The Agentic RAG Chatbot

The "Financial Assistant" is powered by an **Agentic Retrieval-Augmented Generation (RAG)** pipeline. Unlike a standard chatbot, this agent has "Total Awareness" of the user's financial state.

### 3.5.1 Context Building
When a user asks a question, `generate_chat_response()` builds a rich context object:
1.  **Financial Snapshot**: It calculates total income, expenses, and surplus for the last 90 days.
2.  **Top Spending**: It identifies the category with the highest spend (e.g., "Dining: $450").
3.  **Upcoming Bills**: It calls `detect_upcoming_bills()` to forecast liabilities.
4.  **Active Recommendations**: It fetches the top 3 products from the Recommender Engine.

### 3.5.2 PII Scrubbing
To protect user privacy, all input text is passed through `scrub_pii()`. This function uses Regular Expressions to identify and redact sensitive information:
*   **Phone Numbers**: `\b\d{3}-\d{4}\b` -> `[REDACTED]`
*   **Emails**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b` -> `[REDACTED]`
This ensures that Personally Identifiable Information (PII) is never sent to the external LLM provider.

### 3.5.3 System Prompt Engineering
The context is injected into a dynamically generated System Prompt.
> "You are a professional Financial Advisor AI dedicated to a **[Persona]** client. Your client has a surplus of **$[Surplus]**. Their top spending is **[Category]**. Use this data to answer their question."

This prompt engineering forces the generic LLM (Google Gemini) to adopt a specific persona and ground its advice in the user's actual data, effectively solving the "Hallucination Problem."
