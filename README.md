# Flask Social Media Project

This is a simple social media web application built using Flask, MongoDB, and Python.

## Features

- **User Registration and Authentication:** Users can register for an account, log in, and log out. Passwords are securely hashed using Werkzeug.

- **User Profiles:** Each user has a profile page displaying their information.

- **Admin Dashboard:** Admin users have access to a dashboard where they can manage users, create new users, update user information, and delete users.

- **Posts:** Users can create, update, and delete posts.

- **Comments:** Users can add comments to posts.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- Flask
- Flask-PyMongo
- MongoDB

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/flask-social-media.git
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure the application:

Rename the .env.example file to .env and update the configuration variables such as SECRET_KEY, MONGO_URI, etc.
Run the application:

bash
Copy code
python app.py
Visit http://localhost:5000 in your web browser.

Usage
Register for a new account.
Log in with your credentials.
Explore the main page, create posts, and add comments.
Admin users can access the admin dashboard to manage users.
Contributing
If you'd like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch for your feature or bug fix.
Make your changes and submit a pull request.


Acknowledgments
Flask
MongoDB
Werkzeug

Make sure to replace placeholders like `https://github.com/your-username/flask-social-media.git` with the actual URL of your GitHub repository and update any other details as needed.
by [Assia Benkhelifa]
