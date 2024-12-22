from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from flask_swagger_ui import get_swaggerui_blueprint
import datetime
import requests
import os
import uuid
import logging

# Memuat variabel dari file .env
load_dotenv()
logger = logging.getLogger()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Mengambil kredensial database dari .env
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
OPENAI_API = os.getenv('OPENAI_API')

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Tambahkan JWT Secret Key ke konfigurasi
app.config['SECRET_KEY'] = 's3creeer2312k3wewad!'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Swagger UI configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Your App Name"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Model pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    session_id = db.Column(db.String(50))


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Cek apakah user sudah ada
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Menggunakan metode hashing yang valid
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    session_id = uuid.uuid4()
    new_user = User(username=username, password=hashed_password, session_id=session_id)

    db.session.add(new_user)
    db.session.commit()

    # Buat access_token untuk user yang baru dibuat
    access_token = create_access_token(identity={'username': new_user.username})

    return jsonify({"message": "User created successfully", "access_token": access_token}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Jika login berhasil, buat token JWT
    access_token = create_access_token(identity={'username': user.username})
    print("berhasil login")
    return jsonify({"message": "Login successful", "access_token": access_token}), 200

# contoh

@app.route('/chatbot', methods=['POST'])
@jwt_required()
def chatbot():
    data = request.json
    username = get_jwt_identity()

    user = User.query.filter_by(username=username.get('username')).first()
    session_id = user.session_id
    
    message = data['message']
    print(message)
    print(session_id)
    print(OPENAI_API)
    ask_chatbot = requests.post(OPENAI_API+"/conversation",json={'session_id': session_id,'sentence':message})
    
    return ask_chatbot.json()
@app.route('/generate-market-inteligence', methods=['POST'])
@jwt_required()
def market_inteligence():
    data = request.json
    username = get_jwt_identity()
    print(data)

    user = User.query.filter_by(username=username.get('username')).first()
    session_id = user.session_id
    
    product = data['product']
    destination_country = data['destination_country']
    generate_market_inteligence = requests.post(OPENAI_API+"/market-intelligence",json={'product': product,'destination_country':destination_country})
    
    return generate_market_inteligence.json()





if __name__ == '__main__':
    # Buat tabel jika belum ada
    with app.app_context():
        db.create_all()
    app.run(debug=True ,host="0.0.0.0",port=5000)
