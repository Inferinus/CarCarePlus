# This file makes 'main' a Python package.
from flask import Flask
import os
from .extensions import db, migrate
from .api.views import views_blueprint
from .api.app import app_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views_blueprint)
    app.register_blueprint(app_blueprint)
    

    # Configure the SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'carcareplus.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'capstone2023'

    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables for our models
    #db.create_all()
    
    # For vin_decoder
    app.config['CARMED_AUTHORIZATION_KEY'] = 'OWQ2ZWIwZjctYTAxNS00NzYwLWJiZjQtNTgxOWM0MWZmYTMw'
    app.config['CARMED_PARTNER_TOKEN'] = '2ba9e135d0e34f399fcdb1c4b4d32ca5'
    app.config['CARMED_API_BASE_URL'] = 'http://api.carmd.com/v3.0/'

    # For maintenance recommendations
    app.config['CARMD_API_KEY'] = 'OWQ2ZWIwZjctYTAxNS00NzYwLWJiZjQtNTgxOWM0MWZmYTMw'
    app.config['CARMD_PARTNER_TOKEN'] = '2ba9e135d0e34f399fcdb1c4b4d32ca5'
    
    return app

