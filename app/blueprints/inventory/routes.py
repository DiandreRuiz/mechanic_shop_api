from app.blueprints.inventory.schemas import inventory_item_schema, inventory_items_schema
from app.blueprints.inventory import inventory_bp
from sqlalchemy import select
from app.models import Inventory
from flask import request, jsonify
from app.extensions import db
from marshmallow import ValidationError
from typing import Dict

@inventory_bp.route("/", methods=["GET"])
def get_inventory_items():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Inventory)
        inventory_items = db.paginate(query, page=page, per_page=per_page)
    except:
        query = select(Inventory)
        inventory_items = db.session.execute(query).scalars().all()
    
    return inventory_items_schema.jsonify(inventory_items), 200

@inventory_bp.route("/", methods=["POST"])
def add_inventory_item():
    """ from sqlalchemy import inspect
    mapper = inspect(Inventory)
    print(mapper.attrs.keys())
    exit() """
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing post request body"}), 400
    try:
        inventory_item_data = inventory_item_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    inventory_name = inventory_item_data["name"]
    query = select(Inventory).where(Inventory.name == inventory_name)
    existing_inventory_item = db.session.execute(query).scalars().first()
    if existing_inventory_item:
        return jsonify({"error": f"Inventory item of name '{inventory_name}' already exists!"}), 400

    new_inventory_item = Inventory(**inventory_item_data)
    
    db.session.add(new_inventory_item)
    db.session.commit()
    
    return inventory_item_schema.jsonify(new_inventory_item), 201

@inventory_bp.route("/<int:inventory_id>", methods=["PUT"])
def update_inventory_item(inventory_id):
    """Allows partial schema for request body"""
    
    inventory_item = db.session.get(Inventory, inventory_id)
    if not inventory_item:
        return jsonify({"error": f"Could not find inventory item with id: {inventory_id}"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    try:
        inventory_data: Dict = inventory_item_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for k,v in inventory_data.items():
        setattr(inventory_item, k, v)
        
    db.session.commit()
    return inventory_item_schema.jsonify(inventory_item), 200

@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
def delete_inventory_item(inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)
    if not inventory_item:
        return jsonify({"error": f"Could not find inventory item with id: {inventory_id}"}), 404
    db.session.delete(inventory_item)
    db.session.commit()
    return "", 204
    
        
    
    

    
    