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
    