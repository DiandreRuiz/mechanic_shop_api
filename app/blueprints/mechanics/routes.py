from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from app.extensions import db
from . import mechanics_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanic
from sqlalchemy import select
from typing import Dict

@mechanics_bp.route("/", methods=["GET"])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": f"No mechanic found with id: {mechanic_id}"}), 404
    else:
        return mechanic_schema.jsonify(mechanic), 200
    
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    # Validate body existance
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing request JSON body"}), 400
    
    # Validate body schema
    try:
        mechanic_data = mechanic_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Validate uniqueness constraints
    query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": f"Mechanic already exists with email: {mechanic_data["email"]}"}), 400
    
    # Create new entry
    mechanic = Mechanic(**mechanic_data)
    db.session.add(mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(mechanic), 201

@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    # Validate mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": f"No mechanic found with mechanic_id: {mechanic_id}"}), 404
    
    # Validate data existance
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing body JSON"}), 400
    
    # Validate data schema
    try:
        mechanic_data: Dict = mechanic_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Update appropriate entry
    for k,v in mechanic_data.items():
        setattr(mechanic, k, v)
    
    db.session.commit()
    
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": f"No mechanic with id: {mechanic_id} found"}), 404
    else:
        db.session.delete(mechanic)
        db.session.commit()
    
    return jsonify({"message": f"Mechanic with id: {mechanic_id} successfully deleted!"}), 200


        
    
    
    
    