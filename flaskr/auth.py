from flask import Blueprint, flash, redirect, render_template, request, session, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_dynamodb_resource
from botocore.exceptions import ClientError
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

dynamodb = get_dynamodb_resource()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        error = None

        # Validate input
        if not email:
            error = 'email is required.'
        elif not password:
            error = 'Password is required.'
        else:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Store the user in DynamoDB
            table = dynamodb.Table('Users')
            try:
                table.put_item(
                    Item={
                        'email': email,  # Using email as the email
                        'password': hashed_password
                    },
                    ConditionExpression='attribute_not_exists(email)'  # Ensure unique email
                )
                session.clear()
                session['user_id'] = email  # Set the session
                return redirect(url_for('index'))  # Redirect to index after successful registration
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    error = 'Email is already registered.'
                else:
                    error = 'Registration failed.'

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
                return redirect(url_for('index'))  # Redirect to index after successful login

        except ClientError as e:
            error = 'Database error. Please try again later.'

        flash(error)

    return render_template('auth/login.html')


bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('petition.index'))




def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        table = dynamodb.Table('Users')
        try:
            response = table.get_item(Key={'email': user_id})
            g.user = response.get('Item')  
        except Exception as e:
            g.user = None 