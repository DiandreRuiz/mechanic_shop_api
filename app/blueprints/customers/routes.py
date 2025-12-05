from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema

from app.extensions import db, limiter, cache
from app.utils.util import encode_token, token_required
from . import customers_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Customer, Ticket
from sqlalchemy import select
from typing import Dict


@customers_bp.route("/login", methods=["POST"])
def login():
    try:
        credentials = login_schema.load(request.get_json())
        username = credentials["email"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify(e.messages), 400
    except KeyError:
        return jsonify({"error": "Invalid payload, expecting 'username' & 'password' keys to be present"}), 400
    
    
    query = select(Customer).where(Customer.email == username)
    customer = db.session.execute(query).scalar_one_or_none() # Return the first scalar result or None
    
    if customer and customer.password == password:
        auth_token = encode_token(customer.id)
        response = {
            "status": "success",
            "message": "Succesfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({"messages": "Invalid email or password"}), 401
  
  
# Rate limit to prevent overloading servers with extra requests
# Cache results to ease strain on popular query
@customers_bp.route("/", methods=["GET"])
@limiter.limit("5 per minute")
@cache.cached(timeout=60)
def get_customers():
    query = select(Customer)
    members = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(members), 200

# Cache individual customer lookups to reduce database queries for frequently accessed records
@customers_bp.route("/<int:customer_id>", methods=["GET"])
@cache.cached(timeout=60)
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
        return jsonify({"error": f"Account with email '{customer_data['email']}' already exists."}), 400

    # Validated, create new customer row
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
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

# NOTE: Foreign Key constraint in ticket table violated by deleting this!
# Needs cascading setttings set or manual deletion of those records here.
# (Probably not a good idea regardless to have this functionality) 
""" @customers_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(customer_id): # Receives customer_id from the token via the wrapper in ../utils/util.py
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": f"No customer with customer_id: {customer_id} found"}), 404
    else:
        db.session.delete(customer)
        db.session.commit()
    return jsonify({"message": f"Customer with customer_id: {customer_id} deleted"}), 200 """