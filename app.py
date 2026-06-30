from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Error Handlers

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Missing authorization token"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token"}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Token has expired"}), 401

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"message": "Internal server error"}), 500


# Database Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    notes = db.relationship('Note', backref='author', lazy=True)

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_ist_time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()


# Routes

@app.route('/')
def hello():
    return jsonify({"message": "Hello World! Welcome to Simple Notes API"})

# Auth

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401
        
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200


# Notes CRUD Routes

@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    current_user_id = get_jwt_identity()
    notes = Note.query.filter_by(user_id=current_user_id).all()
    
    notes_list = [{
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for note in notes]
    
    return jsonify(notes_list), 200

@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"message": "Title and content are required"}), 400
        
    new_note = Note(
        title=data.get('title'),
        content=data.get('content'),
        user_id=current_user_id
    )
    
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({"message": "Note created successfully", "id": new_note.id}), 201

@app.route('/api/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    current_user_id = get_jwt_identity()
    
    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
    
    if not note:
        return jsonify({"message": "Note not found"}), 404
        
    return jsonify({
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    current_user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
    
    if not note:
        return jsonify({"message": "Note not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400
        
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    
    db.session.commit()
    
    return jsonify({"message": "Note updated successfully"}), 200

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    current_user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
    
    if not note:
        return jsonify({"message": "Note not found"}), 404
        
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({"message": "Note deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
