<div align="center">

  ![DataCanvas Banner](img/banner.png)

> Transform complex datasets into actionable insights with intelligent visualization and scalable analytics

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/ARUNAGIRINATHAN-K/Data-Analyst-Agent)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-87%25-green)](https://codecov.io)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/ARUNAGIRINATHAN-K/Data-Analyst-Agent/releases)

### Tech Stack

| Category | Technologies |
|----------|-------------|
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white) ![D3.js](https://img.shields.io/badge/D3.js-F9A03C?style=for-the-badge&logo=d3.js&logoColor=white) |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) ![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white) |
| **Tools & Libraries** | ![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=python&logoColor=white) ![OAuth](https://img.shields.io/badge/OAuth_2.0-3C873A?style=for-the-badge&logo=auth0&logoColor=white) ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) |


</div>

---

## Overview

**Data Analytics App** is a comprehensive platform designed to simplify the management, segregation, and visualization of complex datasets. Born from the challenges of analyzing COVID-19 data during the pandemic, this application provides an intuitive interface for data entry, robust backend processing, and interactive visualizations that transform raw data into meaningful insights.

### Who It's For

- **Data Analysts** seeking powerful visualization tools
- **Researchers** managing diverse datasets across multiple categories
- **Organizations** requiring scalable analytics solutions
- **Decision Makers** who need clear, actionable insights from complex data

### What Makes It Unique

- **Hybrid Database Architecture**: Combines PostgreSQL for structured analytics with MongoDB for flexible data ingestion
- **Real-time Interactive Visualizations**: Powered by D3.js for dynamic, responsive charts and graphs
- **Big Data Ready**: Apache Spark integration for processing massive datasets efficiently
- **Category-Based Segregation**: Intelligent data organization system inspired by real-world pandemic data challenges
- **Secure & Scalable**: OAuth authentication with enterprise-grade security practices

---

## Installation / Setup Instructions

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.8 or higher
- **Node.js** 14.x or higher
- **PostgreSQL** 13.x or higher
- **MongoDB** 4.4 or higher
- **Apache Spark** 3.0+ (optional, for big data processing)
- **Git**

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/ARUNAGIRINATHAN-K/Data-Analyst-Agent.git
cd Data-Analyst-Agent
```

#### 2. Backend Setup (Python/Flask)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Database Configuration

**PostgreSQL Setup:**

```bash
# Create a PostgreSQL database
createdb analytics_db

# Run migrations
python manage.py db upgrade
```

**MongoDB Setup:**

```bash
# Start MongoDB service
# On Windows:
net start MongoDB
# On macOS/Linux:
sudo systemctl start mongod

# Create MongoDB database (automatically created on first connection)
```

#### 4. Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/analytics_db

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/analytics_data

# OAuth Configuration
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret

# Spark Configuration (Optional)
SPARK_HOME=/path/to/spark
```

#### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Build frontend assets
npm run build
```

#### 6. Run the Application

```bash
# Start the Flask backend (from root directory)
python app.py

# In a separate terminal, start the frontend development server
cd frontend
npm start
```

The application should now be running at:
- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:3000

#### 7. Initial Data Setup (Optional)

```bash
# Load sample datasets
python scripts/load_sample_data.py
```

---

## Learning Outcomes

Through this project, i had gained hands-on experience with:

- **Data Visualization with D3.js**: Create interactive, responsive charts and dashboards
- **Big Data Processing**: Utilize Pandas for analysis and Apache Spark for large-scale data handling
- **Interactive Dashboards**: Build user-friendly interfaces for complex data exploration
- **Secure Data Handling**: Implement OAuth authentication and best practices for data security
- **Scalable Analytics Platforms**: Design systems that grow with your data needs
- **Full-Stack Development**: Integrate frontend visualization with backend data processing
- **Database Management**: Work with both SQL and NoSQL databases for optimal performance

---

## Tech Stack

### Frontend
- **D3.js** - Interactive data visualizations
- **HTML5/CSS3** - Modern, responsive UI
- **JavaScript (ES6+)** - Client-side interactivity

### Backend
- **Python 3.8+** - Core application logic
- **Flask** - Web framework and REST API
- **Pandas** - Data analysis and manipulation
- **Matplotlib** - Static graph generation
- **Apache Spark** - Big data processing engine

### Database
- **PostgreSQL** - Structured analytics data
- **MongoDB** - Semi-structured data ingestion

### Authentication & Security
- **OAuth 2.0** - Secure user authentication

<div align="center">

**Built with ❤️ to make data analytics accessible and powerful**

</div>
