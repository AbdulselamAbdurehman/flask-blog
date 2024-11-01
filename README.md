# PetitionApp

PetitionApp is a web application where users can create, view, and manage petitions. Built with Flask, DynamoDB, and Tailwind CSS, this app supports user registration, authentication, and CRUD operations for petitions.

## Features

- **User Authentication**: Register and log in to access the app.
- **CRUD Operations for Petitions**: Authenticated users can create, view, edit, and delete petitions.
- **Responsive UI**: Styled with Tailwind CSS for a clean, modern look.

## Project Structure

```plaintext
petition/
├── flaskr/
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   ├── petition/
│   │   │    ├── index.html
│   │   │    ├── view.html
│   │   │    ├── edit.html
│   │   │    └──create.html
│   │   └──base.html
│   │
│   ├── auth.py        # Authentication routes
│   ├── db.py          # DynamoDB setup
│   ├── petition.py    # Petition CRUD routes
│   └── __init__.py         # Main app and blueprint registration
├── .env               # Environment variables
├── .gitignore
├── README.Docker.md
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt   # Python dependencies
└── README.md
```
