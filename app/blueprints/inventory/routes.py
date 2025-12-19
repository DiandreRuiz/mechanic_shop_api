from app.blueprints.inventory.schemas import inventory_item_schema, inventory_items_schema
from app.blueprints.inventory import inventory_bp
from sqlalchemy import select
from app.models import Inventory
from flask import request, jsonify
from app.extensions import db

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
    
    
    