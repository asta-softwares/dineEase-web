# DineEase Backend

This is the backend server for the **DineEase** project, built with Django. It handles all backend logic, including payments and user management, and provides APIs to interact with the front end.

## Folder Structure

- `dineease_backend/` - Main Django project folder
  - `settings.py` - Contains project settings
  - `urls.py` - Defines URL routes for the project
- `payments/` - Contains models, views, and logic for payment processing

## Getting Started

### Prerequisites

- Python 3.x
- Django
- Virtualenv

### Setup and Installation

1. **Clone the Repository**

    ```bash
    git clone <repository-url>
    cd dineease
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv env
    ```

3. **Activate the Virtual Environment**

    - On Windows:

        ```bash
        .\env\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source env/bin/activate
        ```

4. **Install the Required Packages**

    Install the required packages from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

5. **Apply Migrations**

    Run the following command to apply migrations and set up the database:

    ```bash
    python manage.py migrate
    ```

6. **Load Fixture Data (Optional)**

    If you have fixture data for initial setup, you can load it into the database using:

    ```bash
    python manage.py loaddata dineease_backend/fixtures/initial_data.json
    ```