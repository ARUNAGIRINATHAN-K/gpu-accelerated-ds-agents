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
