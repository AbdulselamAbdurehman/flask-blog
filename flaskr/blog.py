import datetime
import uuid
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, abort
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from .db import get_dynamodb_resource
from botocore.exceptions import ClientError

bp = Blueprint('blog', __name__)
dynamodb = get_dynamodb_resource()
blogs_table = dynamodb.Table('Blogs')  # Access the Blogs table once


@bp.route('/')
def index():
    """Displays all blogs."""
    response = blogs_table.scan()
    blogs = response.get('Items', [])

    # Format creation date for display
    for blog in blogs:
        blog['created'] = blog.get('created', '')[:10]  # Keep only the date part if present

    return render_template('blog/index.html', blogs=blogs)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Creates a new blog."""
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        if not title:
            flash('Title is required.')
        else:
            author_id = g.user['username']   
            item = {
                'blog_id': str(uuid.uuid4()),
                'title': title,
                'body': body,
                'author_id': author_id,
                'created': datetime.datetime.now().isoformat(),
            }
            blogs_table.put_item(Item=item)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/update/<string:id>', methods=('GET', 'POST'))
@login_required
def update(id):
    """Updates an existing blog."""
    response = blogs_table.get_item(Key={'blog_id': id})
    blog = response.get('Item')

    if blog is None:
        abort(404, f"Blog id {id} doesn't exist.")
    if blog['author_id'] != g.user['username']:
        abort(403, "Forbidden for users")  # Forbidden: user is not the author

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        if not title:
            flash('Title is required.')
        else:
            blogs_table.update_item(
                Key={'blog_id': id},
                UpdateExpression='SET title = :title, body = :body',
                ExpressionAttributeValues={':title': title, ':body': body}
            )
            return redirect(url_for('blog.index'))

    return render_template('blog/edit.html', blog=blog)


@bp.route('/<string:id>', methods=['GET'])
def view(id):
    """Display a single blog."""
    try:
        response = blogs_table.get_item(Key={'blog_id': id})  # Ensure this matches your table's primary key
        blog = response.get('Item')  # Get the item from the response
        
        if blog is None:
            abort(404, "Blog not found.")
        
        return render_template('blog/view.html', blog=blog)
    
    except ClientError as e:
        # Log the exception to understand what went wrong
        print(f"ClientError: {e.response['Error']['Message']}")
        abort(500, "Unable to retrieve blog. Please try again later.")


@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Deletes a blog if the user is the author."""
    # Fetch the blog to check the author
    response = blogs_table.get_item(Key={'blog_id': id})
    blog = response.get('Item')

    # Check if blog exists and if the current user is the author
    if blog is None:
        abort(404, f"Blog id {id} doesn't exist.")
    if blog['author_id'] != g.user['username']:
        abort(403)  # Forbidden: user is not the author

    # Delete the blog
    blogs_table.delete_item(Key={'blog_id': id})
    return redirect(url_for('blog.index'))
