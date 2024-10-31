import os
from flask import Flask, render_template
from dotenv import load_dotenv
from . import db
from . import auth
from . import petition

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

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize DynamoDB
    dynamodb = db.get_dynamodb_resource()
    db.init_dynamodb_tables(dynamodb)
    app.config['DYNAMODB'] = dynamodb

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(petition.bp)

    # Define the index route directly
    @app.route('/')
    def index():
        """Render the index page with petitions."""
        table = dynamodb.Table('Petitions')
        try:
            response = table.scan()
            petitions = response.get('Items', [])
        except Exception as e:
            print(f"Error fetching petitions: {e}")
            petitions = []
        return render_template('petition/index.html', petitions=petitions)

    @app.route('/hello')
    def hello():
        return 'Hello, DynamoDB World!'

    return app
