Online Payment Service (Webapps2025) - Secondary Branch
=======================================================

Introduction
------------

Welcome to the **Online Payment Service**, a Django-based web application designed to facilitate secure payments and payment requests between users with support for multiple currencies (GBP, USD, and EUR). This project fulfills an academic assignment by implementing user registration, authentication, payment processing, payment requests, and an administrative interface, with currency conversion handled via a dedicated RESTful API. The application ensures a seamless user experience with Bootstrap 5 styling and maintains data integrity using a SQLite database. This branch provides the source code and migration files but does not include a preconfigured database, allowing you to set up a fresh environment.

The project showcases:

* **User Management**: Registration, login, and logout with customizable user profiles.
* **Payment Functionality**: Direct payments and payment requests with automatic currency conversion.
* **RESTful API**: A separate endpoint for currency conversion using hard-coded exchange rates.
* **Admin Interface**: Full administrative control, including user and transaction management.
* **Database**: Set up a new SQLite database to store user and transaction data.

This README provides step-by-step instructions to recreate the environment, run the application, and explore its features.

Setup and Installation
----------------------

To recreate this project on your local machine, follow these steps:

### Prerequisites

* **Python 3.11+**: Ensure Python is installed (check with `python --version` or `python3 --version`).
* **Git**: For cloning the repository (install via `git` or your package manager).
* **Virtual Environment**: Recommended for dependency isolation.

### Step-by-Step Instructions

1.  **Clone the Repository**  
    Clone this repository to your local machine using:
    
        git clone -b secondary https://github.com/yourusername/webapps2025.git
        cd webapps2025
    
    (Note: Replace `secondary` with the actual name of your secondary branch if different.)
2.  **Set Up a Virtual Environment**  
    Create and activate a virtual environment:
    
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
    
3.  **Install Dependencies**  
    Install the required Python packages from the included `requirements.txt`:
    
        pip install -r requirements.txt
    
    (Note: If `requirements.txt` is missing, generate it with `pip freeze > requirements.txt` after installing dependencies manually.)
4.  **Apply Migrations**  
    The repository includes migration files. Apply them to set up the database schema and create a new SQLite database (`webapps.db`):
    
        python manage.py migrate
    
5.  **Create a Superuser**  
    Since this branch does not include a preconfigured database, create a superuser to access the admin interface:
    
        python manage.py createsuperuser
    
    Follow the prompts to set a username, email, and password (e.g., username: `admin`, password: `admin`).
6.  **Create Sample Users**  
    To test the application, register sample users via the registration page:
    * Navigate to [http://127.0.0.1:8000/webapps2025/register/](http://127.0.0.1:8000/webapps2025/register/) after starting the server.
    * Create users with different currencies (e.g., user1 with GBP, user2 with USD, user3 with EUR).
    * Example user setup:
        
        | Username | Email | Password | Currency |
        | --- | --- | --- | --- |
        | user1 | user1@mail .com | Abc123!!! | GBP |
        | user2 | user2@mail.com | Abc123!!! | USD |
        | user3 | user3@mail.com | Abc123!!! | EUR |
        
    * Each user will start with a balance equivalent to 750 GBP, converted to their chosen currency (e.g., 750 GBP, 990 USD, 885 EUR).
7.  **Run the Development Server**  
    Start the Django server:
    
        python manage.py runserver
    
8.  **Access the Application**  
    Open your browser and navigate to:
    * **Main Application**: [http://127.0.0.1:8000/webapps2025/login](http://127.0.0.1:8000/webapps2025/login)
    * **Admin Interface**: [http://127.0.0.1:8000/webapps2025/admin/](http://127.0.0.1:8000/webapps2025/admin/)Log in with the superuser credentials you created or register new users to test the application.
9.  **Explore Features**  
    Register new users, send payments, request payments, and manage transactions.  
    Use the admin interface to view or edit data (superuser privileges required for balance changes).

### Notes

* Ensure the server is running for currency conversions to work during registration or payment processing.
* The application uses Bootstrap 5 for styling, enabled via `crispy-bootstrap5`.

Project Structure
-----------------

* `payapp/`: Contains payment-related models, views, and the currency conversion API.
* `register/`: Handles user registration, login, and authentication.
* `templates/`: HTML templates with Bootstrap 5 styling.
* `webapps2025/`: Project configuration files (settings, URLs, etc.).
* `migrations/`: Database migration files for schema setup.

Dependencies
------------

* Django 5.1.7
* djangorestframework
* django-crispy-forms
* crispy-bootstrap5
* requests

(Install via `pip install -r requirements.txt`.)

Currency Conversion Rates
-------------------------

The RESTful API (`/api/convert/`) uses the following hard-coded exchange rates (defined in `payapp/views.py`):

| From | To  | Rate |
| --- | --- | --- |
| GBP | EUR | 1.18 |
| GBP | USD | 1.32 |
| EUR | GBP | 0.85 |
| EUR | USD | 1.12 |
| USD | GBP | 0.76 |
| USD | EUR | 0.89 |

Challenges and Solutions
------------------------

During the development of this project, several challenges were encountered and successfully overcome:

* **Currency Conversion Consistency**: Initially, the registration form (`register/forms.py`) implemented its own hardcoded currency conversion (e.g., 750 * 1.18 for EUR), duplicating logic from the RESTful API. This risked inconsistency if rates changed. **Solution**: The form was updated to use the `/api/convert/` endpoint via the `convert_currency` utility, ensuring all conversions align with the API’s hard-coded rates.
* **Admin Interface Balance Editing**: The `balance` field was set as read-only in the admin interface, preventing necessary adjustments. **Solution**: Implemented dynamic read-only logic in `register/admin.py`, allowing superusers to edit balances while restricting non-superusers, with a `PermissionDenied` check for security.
* **Payment Request Direction**: The payment request system initially deducted money from the requester instead of the target, reversing the intended flow (e.g., User 1 requesting from User 2). **Solution**: Adjusted the `transactions` view in `payapp/views.py` to deduct from the target’s balance and credit the requester, with proper currency conversion.
* **Recursive File Combination**: Combining all Python files into a single document was challenging due to nested subfolders (e.g., `migrations`). **Solution**: Developed a Python script using `Path.rglob()` to recursively process all `.py` files, skipping migration files, and output to `combined_python_files.txt` with clear file headers.
* **Initial Database Setup**: Recreating the project required consistent database initialization, including sample users. **Solution**: Provided detailed instructions to create a new database and register sample users, ensuring a consistent starting point for testing.

These solutions enhanced the project’s reliability, compliance with assignment requirements, and usability for future developers or evaluators.

Contributing
------------

This project is primarily for educational purposes. However, contributions (e.g., bug fixes, enhancements) are welcome. Please submit a pull request or open an issue on GitHub.

License
-------

No license specified.

Contact
-------

For questions, contact me on [GitHub](https://github.com/BoiledPeanuts).
