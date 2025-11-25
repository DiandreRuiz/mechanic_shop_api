from app.blueprints.customers.schemas import customer_schema, customers_schema
from app.extensions import db
from . import customers_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Customer
from sqlalchemy import select
from typing import Dict

@customers_bp.route("/", methods=["GET"])
def get_customers():
    query = select(Customer)
    members = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(members), 200

@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": f"Could not find customer w/ customer_id {customer_id}"}), 404
    else:
        return customer_schema.jsonify(customer), 200

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
        return jsonify({"error": f"Account with email '{Customer.email}' already exists."}), 400

    # Validated, create new customer row
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    # 1. validate existance of customer
    # 2. validate presence of data for update
    # 3. validate schema of data for update
    # 4. perform update of row
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": f"Could not find customer with customer_id of {customer_id}"}), 404
    
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing JSON body for request"}), 404
    
    try:
        customer_data: Dict = customer_schema.load(data)
    except ValidationError as e:
        return jsonify({"error": f"malformed request body: {e.messages}"}), 400

    # update all column values of pulled customer with Dict api
    for k,v in customer_data.items():
        setattr(customer, k, v)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": f"No customer with customer_id: {customer_id} found"}), 404
    else:
        db.session.delete(customer)
        db.session.commit()
    return jsonify({"message": f"Customer with customer_id: {customer_id} deleted"}), 200