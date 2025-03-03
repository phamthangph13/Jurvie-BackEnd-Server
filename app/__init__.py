from flask import Flask
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from .mail import mail
from .auth import auth
from config import Config
import os

def create_app():
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(Config)
    
    # Initialize extensions
    mail.init_app(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Swagger configuration
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Authentication API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return app 