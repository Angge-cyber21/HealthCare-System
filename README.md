# Healthcare Management System -- README

## 1. Install Python

Install **Python 3.10--3.12** from https://www.python.org/downloads/\
Check **"Add Python to PATH"** during installation.

------------------------------------------------------------------------

## 2. Unzip the Project

Unzip **HealthCare Management.zip**.\
Inside you will find:

    /app
    database.py
    web_main.py
    requirements.txt
    README.md

------------------------------------------------------------------------

## 3. Create a Virtual Environment

Open CMD/Terminal **inside the project folder**:

    python -m venv venv

------------------------------------------------------------------------

## 4. Activate the Virtual Environment

### Windows

    venv\Scripts\activate

### Mac / Linux

    source venv/bin/activate

You should now see:

    (venv)

------------------------------------------------------------------------

## 5. Install Dependencies

Run:

    pip install -r requirements.txt

------------------------------------------------------------------------

## 6. Set Up the Database (MySQL)

1.  Open phpMyAdmin / MySQL Workbench\
2.  Create the database:

```{=html}
<!-- -->
```
    CREATE DATABASE mydatabase;

3.  Import **mydatabase.sql**.

------------------------------------------------------------------------

## 7. Run the Web Application

Run:

    python web_main.py

Open the browser:

http://127.0.0.1:5000

------------------------------------------------------------------------

## Troubleshooting

### Flask cannot find modules

Activate venv:

    venv\Scripts\activate

### MySQL login error

Edit **database.py**:

    host="localhost"
    user="admin"
    password="1234"
    database="mydatabase"

------------------------------------------------------------------------

## System Features

-   Patient Management\
-   Doctors & Departments\
-   Appointment Scheduling\
-   Dashboard statistics\
-   Random bios matching doctor specialization\
-   Tree-view department structure\
-   Fully functional Flask routing


