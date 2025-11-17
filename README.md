# 📊 Data Analyst Agent

An **AI-powered Data Analyst Assistant** that helps users analyze datasets in natural language.
Built with **HTML, Bootstrap, and JavaScript (frontend)** and **Python (Flask/FastAPI + Pydantic-AI + Pandas/Polars)** as backend.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-black?logo=flask)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green?logo=fastapi)
![Pydantic](https://img.shields.io/badge/Pydantic-AI-orange?logo=pydantic)
![Pandas](https://img.shields.io/badge/Pandas-1.5+-blue?logo=pandas)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-563D7C?logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chartdotjs)
![License](https://img.shields.io/github/license/your-username/data-analyst-agent)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)


The system allows users to:

* Upload datasets (CSV/Excel).
* Ask natural language questions (e.g., *“Show me the average revenue by region over time”*).
* Receive structured insights and visualizations (tables, charts).

---

## 🚀 Features

* **Dataset Upload**: Accepts CSV/Excel files from users.
* **Natural Language Querying**: Users type plain-English questions.
* **Pydantic-AI Schema Validation**: Queries are translated into structured, validated schemas.
* **Data Analysis Engine**: Pandas/Polars executes filtering, grouping, aggregation, and summaries.
* **Visualization**: Frontend renders results using **Bootstrap tables** and **Chart.js/D3.js** charts.
* **RESTful API**: Flask/FastAPI backend for query processing and dataset management.

---

## 🏗️ Architecture

### High-Level Flow

1. **Frontend (HTML + Bootstrap + JS)**

   * UI for file upload and query input.
   * Displays analysis results and charts.

2. **Backend (Python with Flask/FastAPI)**

   * Handles dataset uploads and query requests.
   * Passes user queries to reasoning engine.

3. **Reasoning Layer (Pydantic-AI)**

   * Translates natural language into structured schemas (e.g., `AggregationRequest`, `SummaryRequest`, `VisualizationRequest`).
   * Ensures valid queries.

4. **Execution Engine (Pandas/Polars)**

   * Executes requested analysis on dataset.
   * Returns structured JSON response.

5. **Frontend Rendering**

   * Uses Chart.js/D3.js for visualization.
   * Uses Bootstrap tables/cards for results display.

---

## 📊 EDA Project Phases

| Phase | Name        | Purpose                                                                 |
|-------|-------------|-------------------------------------------------------------------------|
| 1     | Foundation  | Establish the groundwork: load data, inspect structure, and set up the environment. |
| 2     | Refinement  | Clean and preprocess data: handle missing values, outliers, and ensure consistency. |
| 3     | Lens        | Focus on individual features: explore distributions, summary statistics, and categorical counts. |
| 4     | Connections | Analyze relationships: correlations, scatterplots, heatmaps, and multivariate insights. |
| 5     | Discovery   | Derive insights: feature engineering, highlight patterns, and prepare data for modeling. |


---

## 🔹 Architecture Overview

```
                ┌────────────────────────────┐
                │        Frontend (UI)        │
                │  HTML + Bootstrap + JS      │
                │────────────────────────────│
 User Uploads → │ File Upload (CSV/Excel)     │
 User Queries → │ Text Input (Natural Query)  │
                │ Visualization (Chart.js)    │
                └───────────▲─────┬──────────┘
                            │     │
          (AJAX/Fetch API)  │     │  (JSON Response)
                            │     │
                ┌───────────┴─────▼──────────┐
                │        Backend API          │
                │ Flask / FastAPI (Python)    │
                │─────────────────────────────│
   Routes:      │ /upload   → receive dataset │
                │ /analyze  → interpret query │
                │ /visualize→ return chart    │
                └───────────▲─────┬──────────┘
                            │     │
                            │     │ (structured schema)
                            │     │
                ┌───────────┴─────▼──────────┐
                │   Reasoning & Validation    │
                │    Pydantic-AI Models       │
                │─────────────────────────────│
                │ Validate Query Intent       │
                │ (Aggregation, Summary, Viz) │
                │ Ensure schema correctness   │
                └───────────▲─────┬──────────┘
                            │     │
                            │     │ (clean instructions)
                            │     │
                ┌───────────┴─────▼──────────┐
                │      Execution Engine       │
                │   Pandas / Polars in Python │
                │─────────────────────────────│
                │ Process dataset (filter,    │
                │ group, aggregate, describe) │
                │ Return table/chart data     │
                └───────────▲─────┬──────────┘
                            │     │
                            │     │ (results as JSON)
                            │     │
                ┌───────────┴─────▼──────────┐
                │        Frontend JS          │
                │  Renders results in DOM     │
                │  Bootstrap table / Chart.js │
                └─────────────────────────────┘
```

---

## 🔹 Key Flow

1. **Frontend (HTML/Bootstrap/JS)**

   * User uploads dataset & submits query.
   * Query + dataset metadata sent via AJAX to backend.

2. **Backend (Flask/FastAPI)**

   * Handles API routes (`/upload`, `/analyze`).
   * Passes user query to **Pydantic-AI models**.

3. **Pydantic-AI (Reasoning Layer)**

   * Interprets query into structured schema (e.g., `AggregationRequest`).
   * Ensures validity (no nonsense like “average of names”).

4. **Execution Engine (Pandas/Polars)**

   * Runs requested operation on dataset.
   * Returns structured JSON with results or chart data.

5. **Frontend (JS + Bootstrap)**

   * Receives JSON → Renders tables with Bootstrap and charts with Chart.js.


## 🔧 Tech Stack

### Frontend

* **HTML5, CSS3**
* **Bootstrap 5** (responsive layout, styling)
* **JavaScript (ES6)**
* **Chart.js / D3.js** (visualizations)

### Backend

* **Python 3.10+**
* **Flask / FastAPI** (REST API)
* **Pydantic-AI** (structured schema validation)
* **Pandas / Polars** (data analysis)

---

## ⚙️ API Endpoints

| Endpoint     | Method | Description                        |
| ------------ | ------ | ---------------------------------- |
| `/upload`    | POST   | Upload dataset (CSV/Excel)         |
| `/analyze`   | POST   | Submit natural language query      |
| `/visualize` | GET    | Retrieve visualization config/data |

---

## 📂 Project Structure

```
data-analyst-agent/
│── backend/
│   ├── app.py              # Flask/FastAPI entrypoint
│   ├── models.py           # Pydantic schemas
│   ├── analyzer.py         # Pandas/Polars execution engine
│   └── utils/              # Helpers (validation, parsing)
│
│── frontend/
│   ├── index.html          # Main UI page
│   ├── styles.css          # Custom Bootstrap overrides
│   ├── app.js              # JS logic (fetch API, rendering)
│   └── charts.js           # Chart rendering functions
│
│── datasets/               # Uploaded user datasets
│── README.md               # Documentation
│── requirements.txt        # Python dependencies
```

---

## 📖 Example Workflow

1. User uploads `sales_data.csv`.
2. User enters query: *“What is the average revenue by country?”*
3. Backend (via Pydantic-AI) translates into structured schema:

   ```json
   {
     "type": "AggregationRequest",
     "group_by": "country",
     "metric": "revenue",
     "agg_func": "mean"
   }
   ```
4. Execution engine (Pandas/Polars) computes results:

   ```
   Country   | Avg Revenue
   ----------|------------
   USA       | 45000
   UK        | 38000
   India     | 27000
   ```
5. Frontend renders:

   * Bootstrap **table** with computed values.
   * Chart.js **bar chart** of revenue by country.

---

## 📦 Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ARUNAGIRINATHAN-K/Data-Analyst-Agent.git
cd data-analyst-agent
```

### 2️⃣ Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Run the API server:

```bash
python app.py
```

### 3️⃣ Frontend Setup

Open `frontend/index.html` in a browser (or serve with any static server).

---

## 🔮 Future Enhancements

* ✅ Context-aware conversations (query memory).
* ✅ Automated chart recommendations.
* ✅ Multi-dataset comparison.
* ✅ Role-based access (Analyst, Manager, Admin).
* ✅ Deployment on Docker, AWS, or Streamlit Cloud (for alternative prototyping).


