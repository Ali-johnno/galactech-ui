import os
from dotenv import load_dotenv
from rnnt import RNNT3
from flask import Flask

load_dotenv()

class Config(object):
    num_hidden_encoder=512 
    num_hidden_joiner=64  
    num_hidden_predictor=64 
    input_dim=1024 
    num_predictions=2  
    encoder_input_shape=(15,1198) 
    predictor_input_shape=(1,2)
    joiner_input_shape=(160,) 
    batch_size=1
    num_encoder_dense=128
    num_predictor_dense=32
    label=1


    """Base Config Object"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Som3$ec5etK*y'
    USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Password123'
    UPLOAD_FOLDER = './uploads'
    RNNT=RNNT3(num_hidden_encoder, num_hidden_predictor, num_hidden_joiner, num_predictions, joiner_input_shape,predictor_input_shape,encoder_input_shape,num_encoder_dense,num_predictor_dense)
    # app = Flask(__name__)

    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class DevelopmentConfig(Config):
    """Development Config that extends the Base Config Object"""
    DEVELOPMENT = True
    DEBUG = True

class ProductionConfig(Config):
    """Production Config that extends the Base Config Object"""
    DEBUG = False