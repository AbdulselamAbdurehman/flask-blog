import datetime
import uuid
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db import get_dynamodb_resource
from botocore.exceptions import ClientError


bp = Blueprint('petition', __name__)
dynamodb = get_dynamodb_resource()
petitions_table = dynamodb.Table('Petitions')  # Access the Petitions table once


@bp.route('/')
def index():
    """Displays all petitions."""
    response = petitions_table.scan()
    petitions = response.get('Items', [])

    # Format creation date for display
    for petition in petitions:
        petition['created'] = petition.get('created', '')[:10]  # Keep only the date part if present

    return render_template('petition/index.html', petitions=petitions)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Creates a new petition."""
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        if not title:
            flash('Title is required.')
        else:
            author_id = g.user['username']   
            item = {
                'petition_id': str(uuid.uuid4()),
                'title': title,
                'body': body,
                'author_id': author_id,
                'created': datetime.datetime.now().isoformat(),
            }
            petitions_table.put_item(Item=item)
            return redirect(url_for('petition.index'))

    return render_template('petition/create.html')


@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Updates an existing petition."""
    response = petitions_table.get_item(Key={'id': id})
    petition = response.get('Item')

    if petition is None:
        abort(404, f"Petition id {id} doesn't exist.")
    if petition['author_id'] != g.user['username']:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        if not title:
            flash('Title is required.')
        else:
            petitions_table.update_item(
                Key={'id': id},
                UpdateExpression='SET title = :title, body = :body',
                ExpressionAttributeValues={':title': title, ':body': body}
            )
            return redirect(url_for('petition.index'))

    return render_template('petition/edit.html', petition=petition)


from flask import Blueprint, render_template, abort, g
from botocore.exceptions import ClientError
from .db import get_dynamodb_resource

bp = Blueprint('petition', __name__)
dynamodb = get_dynamodb_resource()

@bp.route('/<string:id>', methods=['GET'])
def view(id):
    """Display a single petition."""
    table = dynamodb.Table('Petitions')
    
    try:

        response = table.get_item(Key={'petition_id': id})  # Ensure this matches your table's primary key
        petition = response.get('Item')  # Get the item from the response
        
        # Debugging output
        print(f"Fetched petition: {petition}")

        if petition is None:
            abort(404, "Petition not found.")
        
        return render_template('petition/view.html', petition=petition)
    
    except ClientError as e:
        # Log the exception to understand what went wrong
        print(f"ClientError: {e.response['Error']['Message']}")
        abort(500, "Unable to retrieve petition. Please try again later.")


@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Deletes a petition if the user is the author."""
    # Fetch the petition to check the author
    response = petitions_table.get_item(Key={'id': id})
    petition = response.get('Item')

    # Check if petition exists and if the current user is the author
    if petition is None:
        abort(404, f"Petition id {id} doesn't exist.")
    if petition['author_id'] != g.user['username']:
        abort(403)  # Forbidden: user is not the author

    # Delete the petition
    petitions_table.delete_item(Key={'id': id})
    return redirect(url_for('petition.index'))
