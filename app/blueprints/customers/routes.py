from app.blueprints.customers.schemas import customer_schema, customers_schema
from app.extensions import db
from . import customers_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Customer
from sqlalchemy import select

@customers_bp.route("/", methods=["GET"])
def get_customers():
    query = select(Customer)
    members = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(members), 200

@customers_bp.route("/", methods=["POST"])
def add_customer():
    # Validate request body
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    
    # Validate request body schema
    try:
        customer_data = customer_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Validate uniqueness of unique constrained columns
    query = select(Customer).where(Customer.email == customer_data["email"])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": f"Account with email '{Customer.email}' already exists."})

    # Validated, create new customer row
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201
