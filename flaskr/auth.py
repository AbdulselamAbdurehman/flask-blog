from flask import Blueprint, flash, redirect, render_template, request, session, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_dynamodb_resource
from botocore.exceptions import ClientError
import functools
from boto3.dynamodb.conditions import Key

bp = Blueprint('auth', __name__, url_prefix='/auth')

dynamodb = get_dynamodb_resource()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        error = None

        # Validate input
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not username:
            error = 'Username is required.'
        else:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Store the user in DynamoDB
            table = dynamodb.Table('Users')
            try:
                # Check for existing username
                username_response = table.query(
                    IndexName='UsernameIndex',  # Ensure this index exists
                    KeyConditionExpression=Key('username').eq(username)
                )
                
                if username_response['Items']:
                    error = 'Username is already taken.'
                else:
                    # Check for existing email
                    email_response = table.get_item(Key={'email': email})
                    if email_response.get('Item'):
                        error = 'Email is already registered.'
                
                # If no errors, proceed to store the user
                if error is None:
                    table.put_item(
                        Item={
                            'email': email,
                            'password': hashed_password,
                            'username': username
                        },
                        ConditionExpression='attribute_not_exists(email)'  # Ensure unique email
                    )
                    session.clear()
                    session['user_id'] = email  # Set the session
                    return redirect(url_for('index'))  # Redirect after successful registration
            except ClientError as e:
                error = 'Registration failed. Please try again later.'

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        # Fetch user from DynamoDB
        table = dynamodb.Table('Users')
        try:
            response = table.get_item(Key={'email': email})
            user = response.get('Item')

            if user is None:
                error = 'Incorrect email.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['email']  # Set the session
                return redirect(url_for('index'))  # Redirect after successful login

        except ClientError:
            error = 'Database error. Please try again later.'

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')  # Fix missing @bp.route decorator
def logout():
    session.clear()
    return redirect(url_for('petition.index'))  # Ensure petition.index exists


def login_required(view):
    """Decorator to ensure user is logged in."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """Load the logged-in user from the session."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        table = dynamodb.Table('Users')
        try:
            response = table.get_item(Key={'email': user_id})
            g.user = response.get('Item')
        except ClientError:
            g.user = None
