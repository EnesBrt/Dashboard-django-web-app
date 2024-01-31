# Dashboard Django Web App

## Description
This repository contains the source code for a Django-based web application designed to provide a comprehensive dashboard experience. The application features user account management, including signup, login, logout, account activation via email, and the ability to resend activation emails.

## Features
- **User Account Management**: Secure signup and login functionality.
- **Email Verification**: Activation of user accounts through a verification email.
- **Resend Activation Email**: Users can request a new activation email if the initial one expires or gets lost.
- **User Dashboard**: After successful login, users are redirected to a personalized dashboard.

## Stack
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Database**: PostgreSQL
- **Email Service**: SMTP for email handling

## Installation and Usage
Follow these steps to set up and run the project:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/EnesBrt/Dashboard-django-web-app.git
   cd Dashboard-django-web-app
   ```

2. **Set Up a Virtual Environment (Optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Database**
   ```bash
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the App**
   Open your browser and go to `http://127.0.0.1:8000/`.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
Feel free to modify or add any additional information that you find relevant to your project.
