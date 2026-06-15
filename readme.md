
**FinPersonalize** is a comprehensive **personal finance management and AI-powered recommendation system** built as a final year project. It's a full-stack web application designed to help users manage their finances through intelligent insights, spending analysis, and personalized recommendations.

### **Project Overview**

- **Repository**: sumaiya1303/FinPersonalize
- **Type**: Final Year Project
- **Status**: Active development (last updated April 2026)
- **Language Composition**: 57.1% JavaScript, 41.9% Python, 1% Other

---

### **Architecture**

The project follows a **client-server architecture** with clear separation of concerns:

#### **Frontend (JavaScript)**
- **Framework**: React 19.2.0 with Vite for fast development
- **Styling**: Tailwind CSS 4.1.17 for modern UI design
- **Routing**: React Router DOM 7.9.6 for navigation
- **HTTP Client**: Axios for API communication
- **Authentication**: Firebase Authentication for user management
- **Data Visualization**: Recharts 3.5.0 for interactive charts and analytics
- **Utilities**: Lucide React for icons, React Markdown for content rendering

#### **Backend (Python)**
- **Framework**: Flask with CORS support for API endpoints
- **Database**: SQLAlchemy with Flask-SQLAlchemy ORM
- **Authentication**: Firebase Admin SDK for user validation
- **AI/ML**: 
  - OpenAI integration for advanced insights
  - Google Generative AI (LangChain integration)
  - Scikit-learn for machine learning models
- **Data Processing**: Pandas for data manipulation
- **Document Processing**: PDFPlumber for PDF parsing
- **Other**: Flask-Migrate for database migrations, Python-dotenv for configuration

---

### **Core Features**

Based on the frontend routing structure, the application includes:

1. **Dashboard** - Home page with overview of financial data
2. **Spending Management** - Track and categorize spending patterns
3. **Financial Goals** - Set and monitor financial objectives
4. **Bills Management** - Track upcoming and recurring bills
5. **Transactions** - View detailed transaction history
6. **Analytics** - Comprehensive financial analytics and insights
7. **Recommendations** - AI-powered personalized financial recommendations
8. **Analysis** - Detailed analysis tools (likely including AI-assisted analysis)
9. **Profile** - User profile management
10. **Admin** - Administrative controls
11. **Onboarding** - User onboarding workflow

---

### **Key Technologies & Capabilities**

**AI & Machine Learning:**
- OpenAI API integration for intelligent recommendations
- Google Generative AI for advanced analysis
- LangChain for AI workflow orchestration
- Scikit-learn for predictive analytics

**Data & Integration:**
- PDF document processing for statement uploads
- Real-time data sync between frontend and backend
- Firebase cloud authentication and data sync

**UI/UX:**
- Modern, responsive design with Tailwind CSS
- Interactive charts and data visualization with Recharts
- Intuitive navigation with React Router
- Loading states and error handling

---

### **Authentication & Security**

- **Multi-method authentication**: Google OAuth and email/password login via Firebase
- **Token-based authorization**: Uses Firebase ID tokens for API requests
- **User synchronization**: Backend syncs user data and tracks onboarding completion status

---

### **Use Case**

FinPersonalize is designed to be an **intelligent personal finance assistant** that combines traditional finance management features (budgeting, bill tracking, transaction monitoring) with **AI-powered insights and personalized recommendations** to help users make better financial decisions and achieve their financial goals.