# Mechanic Shop API

A Flask REST API for managing a mechanic shop with customers, mechanics, and service tickets.

## Features

- **Customers**: Manage customer information (name, email, phone)
- **Mechanics**: Manage mechanic profiles (name, email, phone, salary)
- **Tickets**: Track service tickets with VIN, service date, and descriptions
- Many-to-many relationship between tickets and mechanics

## Setup

### Prerequisites

- Python 3.13+
- MySQL database
- Virtual environment (recommended)

### Installation

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd mechanic_shop
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root with your database connection:
   ```env
   DEV_DATABASE_URI=mysql+mysqlconnector://username:password@localhost:3306/database_name
   TEST_DATABASE_URI=mysql+mysqlconnector://username:password@localhost:3306/test_database
   PROD_DATABASE_URI=mysql+mysqlconnector://username:password@localhost:3306/prod_database
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

   The API will start on `http://localhost:5001`

## API Endpoints

### Customers
- `GET /customers` - Get all customers
- `GET /customers/<id>` - Get customer by ID
- `POST /customers` - Create a new customer
- `PUT /customers/<id>` - Update a customer

### Mechanics
- `GET /mechanics` - Get all mechanics
- `GET /mechanics/<id>` - Get mechanic by ID
- `POST /mechanics` - Create a new mechanic
- `PUT /mechanics/<id>` - Update a mechanic

### Tickets
- `GET /tickets` - Get all tickets
- `GET /tickets/<id>` - Get ticket by ID
- `POST /tickets` - Create a new ticket
- `PUT /tickets/<id>` - Update a ticket

## Testing

A Postman collection (`mechanic_shop.postman_collection.json`) is included for testing the API endpoints. Import it into Postman to get started.

## Project Structure

```
mechanic_shop/
├── app/
│   ├── blueprints/
│   │   ├── customers/    # Customer routes and schemas
│   │   ├── mechanics/    # Mechanic routes and schemas
│   │   └── tickets/      # Ticket routes and schemas
│   ├── models.py         # SQLAlchemy models
│   ├── extensions.py     # Flask extensions (db, ma)
│   └── __init__.py       # App factory
├── app.py                # Application entry point
├── config.py             # Configuration classes
└── requirements.txt      # Python dependencies
```

