# Library Management System

This Library Management System is designed to help librarians manage document catalogs and client records efficiently. It supports various functionalities such as registering new clients, managing documents (books, journals, magazines), handling loans, and maintaining client information including financial transactions.

## Features

### Document Management:

Add, update, and manage different types of documents in the library.

### Client Management: 

Register new clients, update client information, and manage client financials.


### Loan Management: 

Handle the borrowing and returning of books and other library materials.


### Search Functionality:

Search through the library's catalog using various criteria.


## Technologies Used

### Python: 

Main programming language used for the backend.


### PostgreSQL:

Database used for storing all the library and user data.


### Psycopg2: 

PostgreSQL database adapter for Python.


## Installation
To set up the Library Management System, follow these steps:

### Clone the Repository


git clone https://github.com/TahaHabibullah/Library-Management-System/

cd application

Set Up a Python Environment (Optional but recommended)

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`


### Install Dependencies


pip install psycopg2

### Database Setup
Install PostgreSQL and create a database named project.


Run the SQL scripts provided in relationalschema.sql to set up the database schema.


### Configuration


Update the database connection settings in main.py to match your PostgreSQL configuration.


### Usage


To start the application, run the following command from the root of your project directory:



python mainapp.py
Follow the on-screen prompts to navigate through the application.
