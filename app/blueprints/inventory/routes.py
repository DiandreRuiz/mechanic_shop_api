from app.blueprints.inventory.schemas import inventory_item_schema, inventory_items_schema
from app.blueprints.inventory import inventory_bp
from sqlalchemy import select
from app.models import Inventory
from flask import request, jsonify
from app.extensions import db
from marshmallow import ValidationError

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
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing post request body"}), 400
    try:
        inventory_item_data = inventory_item_schema.load()
    except ValidationError as e:
        return jsonify(e)
    
    inventory_name = inventory_item_data["name"]
    query = select(Inventory).where(Inventory.name == inventory_name)
    existing_inventory_item = db.session.execute(query).scalars().first()
    if existing_inventory_item:
        return jsonify({"error": f"Inventory item of name '{inventory_name}' already exists!"}), 400

    new_inventory_item = Inventory(**inventory_item_data)
    db.session.add(new_inventory_item)
    db.session.commit()
    return inventory_item_schema.jsonify(new_inventory_item), 201
    
    
    