| Endpoint | Method | Purpose | Request Body |
| :--- | :--- | :--- | :--- |
| `/api/upload` | `POST` | Uploads and parses a PDF bank statement | `FormData` (file) |
| `/api/dashboard` | `GET` | Fetches summary metrics (Income, Expenses, Savings) | N/A |
| `/api/chat` | `POST` | Sends a user query to the RAG agent and returns a response | `{ "message": "..." }` |
| `/api/recommendations` | `GET` | Retrieves the top-N product recommendations | N/A |
| `/api/goals` | `POST` | Creates or updates a financial goal | `{ "target": 5000, "date": "..." }` |
| `/api/analysis/spending` | `GET` | Returns category-wise spending breakdown for charts | N/A |


### 4.1.2 Database Schema (`models.py`)
The database schema is defined in `app/models.py` and consists of the following key entities:
*   **User**: Stores `firebase_uid`, `email`, and demographic fields like `income_level` and `risk_tolerance`.
*   **Transaction**: The core entity, storing `date`, `amount`, `category`, `merchant_clean`, and `balance_after`.
*   **MoneyScript**: Stores the user's psychographic profile (`risk_score`, `primary_persona`) derived from the onboarding quiz.
*   **Product**: Represents the financial products available for recommendation, including `risk_level` and `tags`.
*   **RecurringBill**: Stores detected recurring obligations, including `frequency` and `day_of_month`.
*   **Goal**: Tracks user savings targets (`target_amount`, `target_date`).

### 4.1.3 Data Ingestion (`ingest_data.py`)
The `ingest_data.py` script handles the parsing of PDF bank statements.
*   **Library**: `pdfplumber` is used for text extraction.
*   **Regex Parsing**: The script uses a specific regex pattern `(\d{2}/\d{2})\s+(.+?)\s+(-?\d+\.\d{2})\s+(\d+\.\d{2})` to capture the Date, Description, Amount, and Balance from each line.
*   **Merchant Cleaning**: A `clean_merchant` function removes noise using regex substitutions (e.g., removing `#\d+` for store numbers and common city names like `LOS ANGELES`).
*   **Categorization**: The `tag_category` function maps keywords (e.g., "netflix" -> "Subscription", "vons" -> "Groceries") to standardized categories.

## 4.2 AI Service Implementation (`services.py`)

The core intelligence is encapsulated in `app/services.py`.

### 4.2.1 Hybrid Recommender Implementation
The `get_hybrid_recommendations` function implements the switching logic:
1.  **Cold Start Check**: It first counts the user's transactions. If count < 5, it triggers the Rule-Based engine.
    *   *Emergency Fund Rule*: Checks if `total_savings < 3 * monthly_expenses`.
    *   *Debt Rule*: Checks if `cc_payments > 5`.
2.  **SVD Inference**: If count >= 5, it loads the `svd_model.pkl`.
    *   *Mapping*: It maps the user's `risk_score` (0-100) to a synthetic user index (`min(99, int(risk_score))`) to retrieve the appropriate latent user vector [12].
    *   *Scoring*: Computes `np.dot(user_vector, svd.components_)`.
3.  **Risk Filtering**: It iterates through the recommendations and removes any product with `risk_level='High'` if the user's persona is 'Conservative Protector' or `risk_score < 40`.

### 4.2.2 RAG Chatbot Implementation
The `generate_chat_response` function implements the RAG pipeline:
1.  **PII Scrubbing**: Calls `scrub_pii` to redact phone numbers and emails using regex.
2.  **Context Building**: Queries the database for the last 90 days of transactions to calculate `total_income`, `total_expenses`, `surplus`, and `top_category`.
3.  **Prompt Construction**: Injects this data into a `SystemMessage` along with a behavioral instruction based on the user's persona (e.g., "Your client is Conservative...").
4.  **LLM Invocation**: Uses `ChatGoogleGenerativeAI` to call the Gemini model.

### 4.2.3 Savings Analysis
The `analyze_savings_plan` function calculates two scenarios:
*   **Current**: Projects the completion date based on the current 90-day average surplus.
*   **Optimized**: Projects a new date assuming a 20% reduction in "Food" category spending.

## 4.3 Evaluation Implementation (`evaluate_system.py`)

The evaluation logic is contained in `backend/evaluate_system.py`.

### 4.3.1 Data Regeneration
A unique implementation detail is that the evaluation script **regenerates the synthetic interaction matrix** in-memory (lines 54-78) to establish a ground truth for testing. This is done because the training script did not serialize the full interaction matrix. The regeneration logic uses probabilistic rules (e.g., "Safe users have 80% prob of Savings products") to recreate the test environment.

### 4.3.2 Metric Calculation
*   **Precision@3**: The script iterates through 100 synthetic users, predicts the top 3 products using the SVD model, and checks for overlap with the regenerated ground truth matrix.
*   **Coverage**: It tracks the set of unique recommended product IDs across all test users to calculate the percentage of the catalog covered.

### 4.3.3 Persona Consistency Check
The `evaluate_persona_consistency` function creates temporary test users (e.g., "eval_Safe User") with specific risk scores. It then runs the recommender and asserts that no "High Risk" products are returned for the safe user, validating the effectiveness of the Risk Filter layer.

## 4.4 Frontend Implementation and User Interface

The frontend is a React SPA located in `frontend/src/pages/`. It is designed to be responsive and intuitive, providing users with immediate access to their financial health metrics.

### 4.4.1 Dashboard View
The **Dashboard** (`Dashboard.jsx`) is the landing page. It fetches data from `/api/dashboard` and renders:
*   **Financial Health Donut Chart**: A visual representation of Income vs. Expenses.
*   **Recent Transactions**: A scrollable list of the latest bank transactions.

[INSERT FIGURE 4.1: Main Dashboard Screenshot showing Financial Health Donut Chart and Recent Transactions]

### 4.4.2 AI Chat Interface
The **Chat Interface** is a persistent floating widget accessible from any page. It calls `/api/chat` to interact with the RAG agent, allowing users to ask natural language questions about their finances.

[INSERT FIGURE 4.2: RAG Chatbot Interface showing a user query and AI response]

### 4.4.3 Spending Analysis
The **Spending Page** (`Spending.jsx`) provides a deep dive into user expenses. It visualizes the category-wise breakdown (e.g., Food, Transport, Utilities) using bar charts and pie charts derived from the `analyze_spending` endpoint.

[INSERT FIGURE 4.3: Spending Breakdown Charts]

### 4.4.4 Goal Setting
The **Goals Page** (`Goals.jsx`) allows users to set and track savings targets. This input feeds into the `analyze_savings_plan` logic to provide personalized recommendations on how to reach these goals faster.

[INSERT FIGURE 4.4: Goal Setting Interface]

