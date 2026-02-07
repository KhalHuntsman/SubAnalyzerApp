# Subscription Analyzer

## Project Description

Subscription Analyzer is a full-stack web application that helps users track, detect, and manage recurring subscriptions and payments. Users can manually add subscriptions or import bank transaction CSV files to automatically detect recurring charges. The app analyzes transaction patterns to suggest subscription candidates, which users can confirm, edit, or ignore.

The goal of the project is to provide a centralized dashboard for monitoring subscription spending, predicting upcoming charges, and improving financial awareness through automated recurring payment detection.

---

## Technologies Used

### Backend

* Python 3
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-JWT-Extended (authentication)
* Flask-CORS
* SQLite (development database)

### Frontend

* JavaScript
* React
* React Router
* Vite
* CSS

---

## File Structure

```
SubAnalyzerApp/backend/run.py

SubAnalyzerApp/backend/requirements.txt

SubAnalyzerApp/backend/app/__init__.py

SubAnalyzerApp/backend/app/models/__init__.py
SubAnalyzerApp/backend/app/models/candidate.py
SubAnalyzerApp/backend/app/models/subscription.py
SubAnalyzerApp/backend/app/models/transaction.py
SubAnalyzerApp/backend/app/models/user.py

SubAnalyzerApp/backend/app/routes/__init__.py
SubAnalyzerApp/backend/app/routes/auth.py
SubAnalyzerApp/backend/app/routes/candidates.py
SubAnalyzerApp/backend/app/routes/dashboard.py
SubAnalyzerApp/backend/app/routes/imports.py
SubAnalyzerApp/backend/app/routes/subscriptions.py

SubAnalyzerApp/backend/app/utils/__init__.py
SubAnalyzerApp/backend/app/utils/normalize.py
SubAnalyzerApp/backend/app/utils/recurrence.py
SubAnalyzerApp/backend/app/utils/validation.py

SubAnalyzerApp/backend/instance/app.db

SubAnalyzerApp/frontend/index.html
SubAnalyzerApp/frontend/package.json
SubAnalyzerApp/frontend/vite.config.js

SubAnalyzerApp/frontend/src/App.jsx
SubAnalyzerApp/frontend/src/main.jsx
SubAnalyzerApp/frontend/src/styles.css

SubAnalyzerApp/frontend/src/components/ConfirmModal.jsx
SubAnalyzerApp/frontend/src/components/Header.jsx
SubAnalyzerApp/frontend/src/components/NavBar.jsx
SubAnalyzerApp/frontend/src/components/ProtectedRoute.jsx

SubAnalyzerApp/frontend/src/lib/api.js

SubAnalyzerApp/frontend/src/pages/Candidates.jsx
SubAnalyzerApp/frontend/src/pages/Dashboard.jsx
SubAnalyzerApp/frontend/src/pages/ImportCSV.jsx
SubAnalyzerApp/frontend/src/pages/Login.jsx
SubAnalyzerApp/frontend/src/pages/Register.jsx
SubAnalyzerApp/frontend/src/pages/Subscriptions.jsx

SubAnalyzerApp/frontend/src/state/AuthContext.jsx
```

---

## Setup and Run Instructions

### 1. Clone the repository

```
git clone <repo-url>
cd SubAnalyzerApp
```

---

### 2. Backend setup

```
cd backend
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the backend folder (optional for development):

```
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

Run the Flask server:

```
python run.py
```

The backend runs at:

```
http://127.0.0.1:5555
```

---

### 3. Frontend setup

Open a new terminal:

```
cd frontend
npm install
npm run dev
```

The frontend runs at:

```
http://localhost:5173
```

---

## Overview of Core Functionality

### Authentication

* User registration and login with JWT authentication
* Access and refresh tokens
* Automatic logout and session expiration handling
* Protected routes in the frontend

### Subscription Management

* Create, edit, cancel, and delete subscriptions
* Manual entry of subscription details
* Dashboard summaries for monthly and annual totals
* Upcoming charge predictions

### CSV Import & Detection

* Upload bank transaction CSV files
* Automatic parsing and normalization of merchant data
* Recurring payment detection algorithm
* Suggested subscription candidates for review

### Candidate Review System

* Confirm detected subscriptions
* Ignore or delete candidates
* Convert confirmed candidates into active subscriptions

### Dashboard Analytics

* Monthly and annual spending totals
* Active subscription count
* Upcoming charges within 30 days
* Top subscription overview

---

## Future Improvements

* Subscription analytics graphs and visualizations
* Enhanced recurring detection accuracy
* Editable transaction history
* Export and reporting features
* Improved UI/UX refinements

---

## Author

Hunter
