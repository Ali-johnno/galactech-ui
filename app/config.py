import os
from dotenv import load_dotenv

from flask import Flask

load_dotenv()

class Config(object):
    """Base Config Object"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Som3$ec5etK*y'
    USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Password123'
    UPLOAD_FOLDER = './uploads'
    # app = Flask(__name__)

    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class DevelopmentConfig(Config):
    """Development Config that extends the Base Config Object"""
    DEVELOPMENT = True
    DEBUG = True

class ProductionConfig(Config):
    """Production Config that extends the Base Config Object"""
    DEBUG = False