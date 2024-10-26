

# Flaskr: A Simple Blog Application

Flaskr is a basic blog application built using [Flask](https://flask.palletsprojects.com/), a lightweight web framework for Python. This app demonstrates foundational Flask concepts, such as using blueprints, managing user authentication, and rendering templates with Jinja2.

## Features

- **User Registration and Login**: Secure registration and login system with hashed passwords.
- **Post Creation and Editing**: Users can create, edit, and delete blog posts.
- **Template Inheritance with Jinja2**: Flexible templates that use base templates for consistency across pages.
- **Database Integration**: Data is stored in an SQLite database.


## Getting Started

### Prerequisites

- Python 3.6 or higher
- Virtual environment manager (e.g., `venv`)
- SQLite (pre-installed with Python)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/flaskr.git
    cd flaskr
    ```

2. **Set up the virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Initialize the database:**

    Run the following commands to set up the database:

    ```bash
    flask init-db
    ```

5. **Run the application:**

    ```bash
    flask run
    ```

    By default, the app will be accessible at `http://127.0.0.1:5000/`.

### Folder Structure

```
flaskr/
├── auth/                   # Blueprint for authentication
├── blog/                   # Blueprint for blog posts
├── templates/              # HTML templates with Jinja2
│   ├── base.html           # Base template for all pages
│   ├── auth/               # Templates for authentication pages
│   └── blog/               # Templates for blog pages
├── static/                 # Static files (CSS, images, etc.)
├── app.py                  # Application factory
└── README.md               # Project documentation
```

## Key Components

### 1. **Application Factory**

The `create_app` function in `app.py` initializes the Flask app with configurations and registers blueprints.

### 2. **Blueprints**

- **auth**: Manages user registration, login, and logout.
- **blog**: Handles viewing, creating, editing, and deleting blog posts.

### 3. **Template Inheritance with Jinja2**

Templates use a base template (`base.html`) that provides a consistent layout. Each page extends `base.html`, adding page-specific content to the `{% block %}` sections for dynamic content.

Example of `base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}{% endblock %} - Flaskr</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
</head>
<body>
    <nav>
        <h1>Flaskr</h1>
        <ul>
            {% if g.user %}
                <li><span>{{ g.user['username'] }}</span></li>
                <li><a href="{{ url_for('auth.logout') }}">Log Out</a></li>
            {% else %}
                <li><a href="{{ url_for('auth.register') }}">Register</a></li>
                <li><a href="{{ url_for('auth.login') }}">Log In</a></li>
            {% endif %}
        </ul>
    </nav>
    <section class="content">
        <header>{% block header %}{% endblock %}</header>
        {% for message in get_flashed_messages() %}
            <div class="flash">{{ message }}</div>
        {% endfor %}
        {% block content %}{% endblock %}
    </section>
</body>
</html>
```

### 4. **Database**

SQLite is used to store user data and blog posts. The database is initialized with the `flask init-db` command.

## Development

To add new features or modify the app:

1. **Add routes** within the appropriate blueprint (e.g., `auth` or `blog`).
2. **Create templates** in the `templates` directory to match new routes.
3. **Update styles** in the `static/style.css` file.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details
