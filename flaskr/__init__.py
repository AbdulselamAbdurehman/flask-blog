import os
from flask import Flask
from dotenv import load_dotenv
import db
import auth

load_dotenv()


def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY")
    )
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    dynamodb = db.get_dynamodb_resource()
    db.init_dynamodb_tables(dynamodb)

    app.config['DYNAMODB'] = dynamodb
    app.register_blueprint(auth.bp)

    @app.route('/hello')
    def hello():
        return 'Hello, DynamoDB World!'

    return app

