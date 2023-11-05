from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS, cross_origin
import os
from app import main

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
db = SQLAlchemy(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = ' NAasodalsdas dasdla asdawd'
jwt = JWTManager(app)

# User Model
class User(db.Model):
    email = db.Column(db.String(120), unique=True, nullable=False, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    selected_course = db.Column(db.Integer)
    # daily_excercise_flag = db.Column(db.Boolean, default=False)
    # beginner_course_progress = db.Column(db.Integer, default=0)
    # intermediate_course_progress = db.Column(db.Integer, default=0)
    # advanced_course_progress = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.email + " " + self.last_name


# User Registration
@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    password = bcrypt.hash(data['password'])
    selected_course = data['selected_course']
    
    all_users = User.query.all()
    for user in all_users:
        if user.email == email:
            return 'already generated', 400

    new_user = User( email=email, first_name=first_name, last_name=last_name, password=password, selected_course=selected_course)
    db.session.add(new_user)
    db.session.commit()

    print(new_user)

    return 'good', 200
# User Login
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.verify(password, user.password):
        return "good", 200
    else:
        return "error", 400

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_video():
    filePath = 'video.webm'

    if 'video' not in request.files:
        return "error", 400

    video_file = request.files['video']

    if video_file:
        video_file.save(filePath)
        actual = main()
        print(actual)
        return actual, 200

# Protected Route (Example)
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    return jsonify({'email': user.email, 'first_name': user.first_name,'last_name': user.last_name})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)
