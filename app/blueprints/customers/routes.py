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


