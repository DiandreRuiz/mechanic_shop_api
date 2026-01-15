# Mechanic Shop API

A Flask REST API for managing a mechanic shop with customers, mechanics, service tickets, and inventory management. Features JWT-based authentication, rate limiting, caching, and pagination support.

## Features

- **Authentication**: JWT-based authentication for customer endpoints
- **Customers**: Manage customer accounts with login functionality
- **Mechanics**: Manage mechanic profiles with ticket assignment tracking
- **Tickets**: Track service tickets with VIN, service dates, and descriptions
- **Inventory**: Manage shop inventory items and associate them with tickets
- **Relationships**: Many-to-many relationships between tickets and mechanics, tickets and inventory
- **Performance**: Rate limiting and caching for optimized performance
- **Pagination**: Support for paginated list endpoints

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

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. **Login** to get an authentication token:
   ```bash
   POST /customers/login
   {
     "email": "customer@example.com",
     "password": "password123"
   }
   ```

2. **Include the token** in the Authorization header for protected endpoints:
   ```
   Authorization: Bearer <your_token_here>
   ```

   Tokens expire after 1 hour and must be refreshed by logging in again. In Swagger UI, click **Authorize** and paste `Bearer <your_token_here>`.

## API Endpoints

### Authentication

- `POST /customers/login` - Customer login (returns JWT token)

### Customers

- `GET /customers` - Get all customers (supports pagination: `?page=1&per_page=10`)
  - Rate limited: 15 per hour
- `GET /customers/<id>` - Get customer by ID
  - Cached: 60 seconds
- `POST /customers` - Create a new customer
- `PUT /customers/<id>` - Update a customer

### Mechanics

- `GET /mechanics` - Get all mechanics
  - Rate limited: 5 per hour
  - Cached: 60 seconds
- `GET /mechanics/<id>` - Get mechanic by ID
  - Cached: 60 seconds
- `GET /mechanics/top-3-mechanics` - Get top 3 mechanics by ticket count
- `POST /mechanics` - Create a new mechanic
- `PUT /mechanics/<id>` - Update a mechanic
- `DELETE /mechanics/<id>` - Delete a mechanic
  - Rate limited: 1 per hour

### Tickets

- `GET /tickets` - Get all tickets
  - Rate limited: 5 per hour
  - Cached: 10 seconds
- `GET /tickets/<id>` - Get ticket by ID
- `GET /tickets/my-tickets` - Get current customer's tickets (requires authentication)
- `POST /tickets` - Create a new ticket
- `PUT /tickets/<id>` - Update a ticket (requires authentication, ownership verified)
- `PUT /tickets/<id>/assign-mechanic/<mechanic_id>` - Assign a mechanic to a ticket
- `PUT /tickets/<id>/remove-mechanic/<mechanic_id>` - Remove a mechanic from a ticket
  - Rate limited: 20 per hour
- `PUT /tickets/<id>/update-mechanics` - Bulk update mechanics (add/remove multiple)
- `POST /tickets/<id>/inventory` - Add inventory items to a ticket

### Inventory

- `GET /inventory` - Get all inventory items (supports pagination: `?page=1&per_page=10`)
- `POST /inventory` - Create a new inventory item
- `PUT /inventory/<id>` - Update an inventory item
- `DELETE /inventory/<id>` - Delete an inventory item

## Rate Limiting & Caching

The API implements rate limiting and caching to optimize performance and prevent abuse:

- **Rate Limiting**: Prevents excessive requests using Flask-Limiter
- **Caching**: Reduces database load using Flask-Caching (SimpleCache)
- **Cache TTL**: Varies by endpoint (10-60 seconds based on data volatility)

Protected operations (DELETE, sensitive updates) have stricter rate limits to prevent accidental or malicious actions.

## Data Models

### Customer
- `id`, `name`, `email`, `phone`, `password`
- One-to-many relationship with Tickets

### Mechanic
- `id`, `name`, `email`, `phone`, `salary`
- Many-to-many relationship with Tickets

### Ticket
- `id`, `VIN`, `service_date`, `service_description`, `customer_id`
- Belongs to one Customer
- Many-to-many relationship with Mechanics
- Many-to-many relationship with Inventory (via TicketInventory)

### Inventory
- `id`, `name`, `price`
- Many-to-many relationship with Tickets (via TicketInventory)

### TicketInventory (Join Table)
- `id`, `ticket_id`, `inventory_id`, `quantity`
- Links Tickets to Inventory with quantities

## Testing

A Postman collection (`mechanic_shop.postman_collection.json`) is included for testing the API endpoints. Import it into Postman to get started. Swagger UI is available at `http://localhost:5001/api/docs`.

## Project Structure

```
mechanic_shop/
├── app/
│   ├── blueprints/
│   │   ├── customers/       # Customer routes and schemas
│   │   ├── mechanics/       # Mechanic routes and schemas
│   │   ├── tickets/         # Ticket routes and schemas
│   │   └── inventory/       # Inventory routes and schemas
│   ├── models.py            # SQLAlchemy models
│   ├── extensions.py        # Flask extensions (db, ma, limiter, cache)
│   ├── utils/
│   │   └── util.py          # JWT token utilities (encode_token, token_required)
│   └── __init__.py          # App factory
├── app.py                   # Application entry point
├── config.py                # Configuration classes
└── requirements.txt         # Python dependencies
```

## Key Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Marshmallow**: Schema serialization
- **Flask-Limiter**: Rate limiting
- **Flask-Caching**: Response caching
- **python-jose**: JWT token handling
- **mysql-connector-python**: MySQL database connector

## Notes

- Customer passwords are stored in plain text (consider hashing for production)
- Customer passwords are accepted on input but not returned in API responses
- DELETE operations on customers are commented out due to foreign key constraints
- Token expiration is set to 1 hour
- Pagination is optional - endpoints return all results if pagination parameters are not provided
