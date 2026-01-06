from . import tickets_bp
from app.blueprints.tickets.schemas import (
    ticket_schema,
    tickets_schema,
    update_ticket_mechanics_schema,
    update_ticket_mechanics_response_schema,
    add_ticket_inventory_items_schema
)
from app.extensions import db, limiter, cache
from app.utils.util import token_required
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Ticket, Mechanic, Customer, Inventory, TicketInventory
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Dict

# Rate limit to prevent overloading servers with extra requests
# Cache results to ease strain on popular query
@limiter.limit("5 per hour")
@cache.cached(timeout=10)
@tickets_bp.route("/", methods=["GET"])
def get_tickets():
    query = select(Ticket)
    tickets = db.session.execute(query).scalars().all()
    
    return tickets_schema.jsonify(tickets), 200

@tickets_bp.route("/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": f"No ticket found with ticket_id: {ticket_id}"}), 404
    else:
        return ticket_schema.jsonify(ticket), 200
    
@tickets_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Could not find customer with supplied customer ID from your auth token"}), 404
    
    query = select(Ticket).where(Ticket.customer_id == customer.id)
    tickets = db.session.execute(query).scalars().all()
    
    return tickets_schema.jsonify(tickets), 200
    
@tickets_bp.route("/", methods=["POST"])
def create_ticket():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing request JSON body"}), 400
    
    try:
        ticket_data = ticket_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Create new ticket & add
    customer = db.session.get(Customer, ticket_data['customer_id'])
    if not customer:
        return jsonify({'error': f'Could not find customer with id: {ticket_data['customer_id']}'}), 404
    
    new_ticket = Ticket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
        
    return ticket_schema.jsonify(new_ticket), 201

@tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
@token_required
def update_ticket(customer_id, ticket_id):
    # Validate existance of ticket
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": f"No ticket found with id of {ticket_id}"}), 404
    
    if ticket.customer_id != int(customer_id):
        return jsonify({"error": "You are trying to alter a resource that you don't own (judged by auth token)"}), 401
    
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Could not find customer with supplied customer ID from your auth token"}), 404
        
    
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing request body JSON"}), 400
    
    try:
        ticket_data: Dict = ticket_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Go through each column of request payload and set it in selected ticket
    for k,v in ticket_data.items():
        setattr(ticket, k, v)
        
    db.session.commit()
        
    return ticket_schema.jsonify(ticket), 200

@tickets_bp.route("/<int:ticket_id>/update-mechanics", methods=["PUT"])
def update_ticket_mechanics(ticket_id):
    try:
        ticket_updates = update_ticket_mechanics_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # select ticket we want to update
    query = select(Ticket).where(Ticket.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()
    
    for mechanic_id in ticket_updates.get("add_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
    
    for mechanic_id in ticket_updates.get("remove_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
    
    db.session.commit()
    return update_ticket_mechanics_response_schema.jsonify(ticket), 200

@tickets_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not ticket:
        return jsonify({"error": f"Could not locate Ticket with id: {ticket_id}"}), 404
    if not mechanic:
        return jsonify({"error": f"Could not locate mechanic with id: {mechanic_id}"}), 404
    
    # Prevent duplicate linking
    if mechanic in ticket.mechanics:
        return jsonify({
            "message": "Mechanic is already assigned to this ticket.",
            "ticket_id": ticket_id,
            "mechanic_id": mechanic_id
        }), 200
    
    ticket.mechanics.append(mechanic)
    db.session.commit()
    
    return jsonify({
        "message": "Mechanic successfully assigned to ticket.",
        "ticket_id": ticket_id,
        "mechanic_id": mechanic_id
    }), 200

# Rate limit to prevent accidental mass removals of mechanics from tickets
@tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("3 per hour")
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not ticket:
        return jsonify({"error": f"Could not locate Ticket with id: {ticket_id}"}), 404
    if not mechanic:
        return jsonify({"error": f"Could not locate mechanic with id: {mechanic_id}"}), 404
    
    if mechanic not in ticket.mechanics:
        return jsonify({"error": f"Mechanic id: {mechanic_id} not found in mechanics for Ticket id: {ticket_id}"}), 404
    
    ticket.mechanics.remove(mechanic)
    db.session.commit()
    
    return jsonify({
        "message": "Mechanic successfully removed from ticket.",
        "ticket_id": ticket_id,
        "mechanic_id": mechanic_id
    }), 200
    
@tickets_bp.route("/<int:ticket_id>/inventory", methods=["POST"])
def add_inventory(ticket_id):
    
    # Validate payload schema
    try:
        inventory_updates = add_ticket_inventory_items_schema.load(request.get_json())    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Validate at least 1 inventory item
    add_inventory_items = inventory_updates.get("add_inventory_items")
    if not add_inventory_items:
        return jsonify({"error": "add_inventory_items key must be a non-empty list"}), 400
    
    # Validate Ticket exists
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": f"Could not find ticket with ticket_id: {ticket_id}"}), 404

    payload_ids = [i["inventory_id"] for i in add_inventory_items]
    if len(payload_ids) != len(set(payload_ids)):
        return jsonify({"error", "Payload contains at least 1 duplicate inventory ID"}), 400
    
    # Validate Inventory items exist
    inventory_ids = set([i["inventory_id"] for i in add_inventory_items])
    
    inventory_check_query = select(Inventory.id).where(Inventory.id.in_(inventory_ids))
    found_ids = set(db.session.scalars(inventory_check_query).all())
    
    missing = sorted(inventory_ids - found_ids)
    if missing:
        return jsonify({
            "error": "Some inventory items did not exist",
            "missing_ids": missing
        }), 404
    
    # Find Inventory items already associated with Ticket
    dup_inventory_query = select(TicketInventory.inventory_id).where(
        TicketInventory.ticket_id == ticket_id,
        TicketInventory.inventory_id.in_(inventory_ids)
    )
    
    dup_inventory = set(db.session.scalars(dup_inventory_query).all())
    inv_to_add = [i for i in add_inventory_items if i["inventory_id"] not in dup_inventory]
    
    # Create Rows
    for item in inv_to_add:
        db.session.add(TicketInventory(
                ticket_id=ticket_id,
                inventory_id=item["inventory_id"],
                quantity=item["quantity"]
        ))
    
    # Protect against race conditions
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "One or more inventory items were already associated with this ticket"}) 
    
    # Collect duplicate rows that weren't inserted
    added_ids = sorted(i["inventory_id"] for i in inv_to_add)
    duplicate_ids = sorted(dup_inventory)
    
    return jsonify({
        "ticket_id": ticket_id,
        "added_inventory_ids": added_ids,
        "duplicate_inventory_ids": duplicate_ids,
        "requested_count": len(add_inventory_items),
        "added_count": len(added_ids),
        "duplicate_count": len(duplicate_ids)
    }), 200


# NOTE: This code opens an endpoint capable of deleting a ticket, not sure we want to do that

""" @tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": f"Could not find ticket with ticket_id: {ticket_id}"})

    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({"message": f"Successfully deleted ticket with ticket_id: {ticket_id}"}) """
    
    
    



    