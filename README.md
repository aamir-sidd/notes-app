# Notes Application

A simple, full-stack learning project that demonstrates building a secure RESTful API and connecting it to a lightweight frontend.

## Features
* **User Authentication**: Secure user registration and login using JSON Web Tokens (JWT) and password hashing.
* **CRUD Operations**: Users can Create, Read, Update, and Delete their own personal notes.
* **API-First Design**: The backend serves a pure JSON API, completely separated from the frontend presentation.
* **Single-Page Application**: A reactive frontend interface built with Vue.js that communicates securely with the backend via Axios.

## Included Files
* `app.py`: The complete Python backend (Flask server, SQLite database models, and API routes).
* `index.html`: The Vue.js frontend application structure and logic.
* `style.css`: The simple styling foundation for the user interface.

## How to Run Locally

### 1. Set up the Backend
First, ensure you have Python installed. Then, install the required Python packages:
```bash
pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-Cors Werkzeug
```

Start the Flask server:
```bash
python app.py
```
*(The server will run on `http://127.0.0.1:5000` and automatically generate a `notes.db` SQLite database file in the same directory upon first run.)*

### 2. Run the Frontend
Simply double-click the `index.html` file to open it in your favorite web browser. 

Because the frontend uses Vue.js and Axios via CDN, and the backend is configured with CORS, everything will work seamlessly without needing a separate frontend build process or server.
