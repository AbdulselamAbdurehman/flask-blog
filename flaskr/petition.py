import datetime
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db import get_dynamodb_resource

bp = Blueprint('petition', __name__)

dynamodb = get_dynamodb_resource()


@bp.route('/')
def index():
    table = dynamodb.Table('Petitions')  # Get the Petitions table

    # Fetch petitions from DynamoDB
    response = table.scan()  # This will get all items
    petitions = response.get('Items', [])

    # Formatting petitions
    formatted_petitions = []
    for petition in petitions:
        formatted_petitions.append({
            'id': petition.get('id', ''),
            'title': petition.get('title', ''),
            'body': petition.get('body', ''),
            'created': petition.get('created', ''),
            'author_id': petition.get('author_id', ''),
            'username': petition.get('username', '')
        })

    # If created is a string in ISO 8601 format, format it as a date string
    for petition in formatted_petitions:
        if petition['created']:
            petition['created'] = petition['created'][:10]  # Extract just the date part

    return render_template('petition/index.html', petitions=formatted_petitions)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:

            table = dynamodb.Table('Petitions')  # 

            # Create a new petition item
            item = {
                'id': str(uuid.uuid4()),  # Generate a unique ID for the petition
                'title': title,
                'body': body,
                'author_id': g.user['id'],
                'created': datetime.utcnow().isoformat()  # Store the creation time
            }

            # Insert the item into the DynamoDB table
            table.put_item(Item=item)

            return redirect(url_for('petition.index'))

    return render_template('petition/create.html')


@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    petition = get_petition(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            table = dynamodb.Table('Petitions')
            # Update the petition in the DynamoDB table
            table.update_item(
                Key={'id': id},
                UpdateExpression='SET title = :title, body = :body',
                ExpressionAttributeValues={':title': title, ':body': body}
            )

            return redirect(url_for('petition.index'))
        

    

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    table = dynamodb.Table('Petitions')
    # Delete the petition from the DynamoDB table
    table.delete_item(Key={'id': id})
    return redirect(url_for('petition.index'))

    


def get_petition(id, check_author=True):
    table = dynamodb.Table('Petitions')  # Get the Petitions table

    # Fetch the petition from DynamoDB
    response = table.get_item(Key={'id': id})
    petition = response.get('Item')

    if petition is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and petition['author_id'] != g.user['id']:
        abort(403)

    return petition
