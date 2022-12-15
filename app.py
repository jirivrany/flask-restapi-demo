"""
Ukázka jednoduchého REST API a zpracování parametrů v URL
včetně routingu a metod HTTP.
"""
import os
import jwt
from dataclasses import dataclass
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

import config

VERSION = '0.0.2'


app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
db = SQLAlchemy(app)


@dataclass
class User(db.Model):
    """
    Modely obvykle umísťujeme do zvláštního souboru.
    Pak je ale nutné upravit celou strukturu projektu aby fungoval import

    Model využívá dataclass - https://docs.python.org/3/library/dataclasses.html
    """
    id: int
    name: str
    about: str

    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(100), unique=True, nullable = False)
    about = db.Column(db.String(150), nullable=True)

    def __init__(self, name: str, about: str = None):
        self.name = name
        self.about = about


# Auth decorator

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "auth token is missing"}), 401

        try:
            jwt.decode(token, app.config.get("JWT_SECRET"), algorithms=["HS256"])
        except jwt.DecodeError:
            return jsonify({"message": "auth token is invalid"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "auth token expired"}), 401

        return f(*args, **kwargs)

    return decorated



@app.route("/auth", methods=["GET"])
def authorize():
    """
    create auth JWT

    request headers:
        key: secret api key
    """
    jwt_key = app.config.get("JWT_SECRET")
    secret_key = app.config.get("SECRET_KEY")

    user_key = request.headers.get('key', None)
    
    if user_key == secret_key:
        payload = {
            "user": "api",
            "exp": datetime.now() + timedelta(minutes=30),
        }
        encoded = jwt.encode(payload, jwt_key, algorithm="HS256")

        return jsonify({"token": encoded})
    else:
        payload = {"message": "auth token is invalid"}
        return jsonify(payload), 403




@app.route('/users')
def get_users():
    """
    Vrati seznam vsech uzivatelu
    """
    users = User.query.all()
    res = {"success": True, 'users': users, 'version': VERSION}
    return jsonify(res)


@app.route('/users/<name>', methods=['GET'])
@token_required
def get_user_by_name(name=None):
    """
    Vrati uzivatele pokud je zadany parametr name a uzivatel existuje

    request headers:
        x-access-token: secret 
    """
    user = User.query.filter_by(name=name).first()
    
    res = {"success": True, "user": user} if user else {"success": False, "reason": f'user not found:{name}'}

    return jsonify(res)


@app.route('/users', methods=['POST'])
@token_required
def create_user():
    """
    Vytvori noveho uzivatele z json dat 

    request headers:
        content-type: application/json
        x-access-token: secret 

    request:body
        {
        "name": "Tom Sawyer",
        "about": "titular character of the Mark Twain novel The Adventures of Tom Sawyer"
        }
    """
    user = request.get_json()
    
    #if not user or not user['name']:
    #    res = {"success": False,
    #           "reason": 'cannot create user (missing user name)'}
    #    return jsonify(res)

    myuser = User(user.get('name', None), user.get('about', None))
    try:
        db.session.add(myuser)
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        res = {"success": False, "reason": repr(err), "user": user}
        return jsonify(res)
    
    res = {"success": True, "user": myuser}
    return jsonify(res)



@app.route('/users/<name:str>', methods=['PUT'])
@token_required
def update_user(name=None):
    """
    Aktualizuje uzivatele 

    request url:
    v URL existujici jmeno  

    request headers:
    content-type: application/json
    x-access-token: secret 

    request body:
     {
        "name": "Tomas",
        "about": "Nova hodnota"
     }

    """ 
    user = User.query.filter_by(name=name).first()

    update = request.get_json()

    if user:
        user.name = update.get("name", None)
        user.about = update.get("about", None)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            res = {"success": False, "reason": repr(err), "user": user}
            return jsonify(res)    

    res = {"success": True, "user": user } if user else {"success": False, "reason": f"user {name} not found"}
    return jsonify(res)


@app.route('/users/<name:str>', methods=['DELETE'])
@token_required
def delete_user(name=None):
    """
    smaze uzivatele 
    
    request url: v URL existujici jmeno  
    """
    user = User.query.filter_by(name=name).first()

    try:
        User.query.filter_by(name=name).delete()
        db.session.commit()
    except IndentationError as err:
        db.session.rollback()
        res = {"success": False, "reason": repr(err), "user": user}
        return jsonify(res)  

    res = {"success": True, "user": user } if user else {"success": False, "reason": f"user {name} not found"}
    return jsonify(res)
