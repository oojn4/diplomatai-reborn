from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import uuid
import os
import requests

# Memuat variabel dari file .env
load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Konfigurasi database
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
OPENAI_API = os.getenv('OPENAI_API')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 's3creeer2312k3wewad!'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Swagger UI configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "DiplomatAI"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Model pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'umkm' atau 'diplomat'
    session_id = db.Column(db.String(50))
    umkm = db.relationship('UMKM', backref='user', uselist=False)
    diplomat = db.relationship('Diplomat', backref='user', uselist=False)
class UMKM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    domicile_id = db.Column(db.Integer, db.ForeignKey('domicile.id'), nullable=False)
    npwp = db.Column(db.String(15))
    business_entity_legality = db.Column(db.String(50))
    business_field_licensing = db.Column(db.String(50))
class Diplomat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nip = db.Column(db.String(18), nullable=False)
    
class Domicile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prov_code = db.Column(db.String(2), nullable=False)
    kab_code = db.Column(db.String(4), nullable=False)
    kec_code = db.Column(db.String(7), nullable=False)
    desa_code = db.Column(db.String(10), nullable=False)
    prov = db.Column(db.String(100), nullable=False)
    kab = db.Column(db.String(100), nullable=False)
    kec = db.Column(db.String(100), nullable=False)
    desa = db.Column(db.String(100), nullable=False)
    nearest_airport_port = db.Column(db.String(100), nullable=False)
    distance_nearest_airport_port = db.Column(db.Float, nullable=False)
    time_travel_nearest_airport_port = db.Column(db.Float, nullable=False)
    umkm = db.relationship('UMKM', backref='domicile', uselist=False)
    

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    role = data.get('role')
    email = data.get('email')
    password = data.get('password')
    additional_info = data.get('additional_info', {})

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if role not in ['umkm', 'diplomat']:
        return jsonify({"error": "Invalid role. Must be 'umkm' or 'diplomat'"}), 400

    # Cek apakah user sudah ada
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Hash password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    session_id = str(uuid.uuid4())

    # Buat user baru
    new_user = User(
        email=email,
        password=hashed_password,
        session_id=session_id,
        role=role,
    )
    db.session.add(new_user)
    db.session.flush()  # Pastikan ID user tersedia sebelum menyimpan relasi

    # Simpan data tambahan berdasarkan role
    if role == 'umkm':
        domicile = Domicile.query.filter_by(
            # prov_code=additional_info.get('province'),
            # kab_code=additional_info.get('city'),
            # kec_code=additional_info.get('district'),
            desa_code=additional_info.get('village'),
        ).first()

        if not domicile:
            return jsonify({"error": "Invalid domicile data"}), 400

        umkm_data = UMKM(
            user_id=new_user.id,
            domicile_id=domicile.id,
            npwp=additional_info.get('npwp'),
            business_entity_legality=additional_info.get('business_entity_legality'),
            business_field_licensing=additional_info.get('business_field_licensing'),
        )
        db.session.add(umkm_data)

    elif role == 'diplomat':
        diplomat_data = Diplomat(
            user_id=new_user.id,
            nip=additional_info.get('nip'),
        )
        db.session.add(diplomat_data)

    db.session.commit()

    # Buat access_token
    access_token = create_access_token(identity={'email': new_user.email, 'role': new_user.role})

    return jsonify({"message": "User created successfully", "access_token": access_token}), 201

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('username')
    password = data.get('password')
    role = data.get('role')

    user = User.query.filter_by(role=role).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Buat token JWT
    access_token = create_access_token(identity={'username': user.email, 'role': user.role})
    return jsonify({"message": "Login successful", "access_token": access_token}), 200

# Middleware untuk memeriksa akses berdasarkan role
def role_required(required_role):
    def decorator(func):
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if identity.get('role') != required_role:
                return jsonify({"error": "Access denied"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/chatbot', methods=['POST'])
@jwt_required()
def chatbot():
    identity = get_jwt_identity()
    if identity.get('role') not in ['umkm', 'diplomat']:
        return jsonify({"error": "Access denied"}), 403

    data = request.json
    username = identity['username']
    user = User.query.filter_by(email=username).first()
    session_id = user.session_id

    message = data['message']
    response = requests.post(OPENAI_API + "/conversation", json={
        'session_id': session_id,
        'sentence': message
    })

    return response.json()

@app.route('/generate-market-inteligence', methods=['POST'])
@role_required('diplomat')
def market_intelligence():
    data = request.json
    print(data)
    identity = get_jwt_identity()
    username = identity['username']

    user = User.query.filter_by(email=username).first()
    session_id = user.session_id

    product = data['product']
    destination_country = data['destination_country']
    response = requests.post(OPENAI_API + "/market-intelligence", json={
        'product': product,
        'destination_country': destination_country
    })

    return response.json()
@app.route('/locations', methods=['GET'])
def get_locations():
    # Mengambil semua data dari tabel Domicile
    locations = Domicile.query.all()
    # Membentuk struktur data hierarki
    data = {}
    for loc in locations:
        if loc.prov_code not in data:
            data[loc.prov_code] = {
                "name": loc.prov,
                "cities": {}
            }
        if loc.kab_code not in data[loc.prov_code]["cities"]:
            data[loc.prov_code]["cities"][loc.kab_code] = {
                "name": loc.kab,
                "districts": {}
            }
        if loc.kec_code not in data[loc.prov_code]["cities"][loc.kab_code]["districts"]:
            data[loc.prov_code]["cities"][loc.kab_code]["districts"][loc.kec_code] = {
                "name": loc.kec,
                "villages": {}
            }
        data[loc.prov_code]["cities"][loc.kab_code]["districts"][loc.kec_code]["villages"][loc.desa_code] = loc.desa

    # Mengubah struktur menjadi list yang mudah digunakan di frontend
    result = []
    for prov_code, prov_data in data.items():
        provinces = {
            "id": prov_code,
            "name": prov_data["name"],
            "cities": []
        }
        for kab_code, kab_data in prov_data["cities"].items():
            cities = {
                "id": kab_code,
                "name": kab_data["name"],
                "districts": []
            }
            for kec_code, kec_data in kab_data["districts"].items():
                districts = {
                    "id": kec_code,
                    "name": kec_data["name"],
                    "villages": []
                }
                for desa_code, desa_name in kec_data["villages"].items():
                    districts["villages"].append({
                        "id": desa_code,
                        "name": desa_name
                    })
                cities["districts"].append(districts)
            provinces["cities"].append(cities)
        result.append(provinces)

    return jsonify(result), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
