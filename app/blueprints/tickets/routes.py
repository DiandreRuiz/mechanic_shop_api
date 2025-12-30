from . import tickets_bp
from app.blueprints.tickets.schemas import (
    ticket_schema,
    tickets_schema,
    update_ticket_mechanics_schema,
    update_ticket_mechanics_response_schema,
    update_ticket_inventory_items_schema
)
from app.extensions import db, limiter, cache
from app.utils.util import token_required
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Ticket, Mechanic, Customer, Inventory, TicketInventory
from sqlalchemy import select
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
    
@tickets_bp.route("/<int:ticket_id>/inventory", methods=["Post"])
def add_inventory(ticket_id, inventory_id):
    """
    1. Get ticket -> check if exists
    2. Get inventory item -> check if exists
    3. Check if this inventory item is already associated with this ticket
    4. Add Inventory Obj to ticket.inventory list
    4. Commit changes
    """
    
    try:
        inventory_updates = update_ticket_inventory_items_schema.load(request.get_json())    
    except ValidationError as e:
        return jsonify(e.messages)
    
    add_inventory_items = inventory_updates.get("add_inventory_items")
    remove_inventory_items = inventory_updates.get("remove_inventory_items")
    
    ticket = db.session.get(Ticket, ticket_id)
    inventory_item = db.session.get(Inventory, inventory_id)
    
    # Check for existance of ticket & inventory_item
    if not ticket:
        return jsonify({"error": f"Could not find ticket with ticket_id: {ticket_id}"})
    if not inventory_item:
        return jsonify({"error": f"Could not find inventory item with id: {inventory_id}"})
    
    # Check for existing
    assoc_query = select(TicketInventory).where(
        TicketInventory.ticket_id == ticket_id,
        TicketInventory.inventory_id == inventory_id
    )
    tic_inven_assoc = db.session.scalar(assoc_query)
    if tic_inven_assoc is not None:
        return jsonify({"error": f"Inventory item with id: {inventory_id} already associated with ticket with id: {ticket_id}"})
    
    ticket.
    db.session.commit()
    
    return jsonify({
        "message": "Inventory item successfully added to ticket",
        "ticket_id": ticket_id,
        "inventory_id": inventory_id
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
    
    
    



    