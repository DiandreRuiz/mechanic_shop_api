from . import tickets_bp
from app.blueprints.tickets.schemas import ticket_schema, tickets_schema
from app.extensions import db, limiter, cache
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Ticket, Mechanic
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
def update_ticket(ticket_id):
    # Validate existance of ticket
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": f"No ticket found with id of {ticket_id}"}), 404
    
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
        


# NOTE: This code opens an endpoint capable of deleting a ticket, not sure we want to do that

""" @tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": f"Could not find ticket with ticket_id: {ticket_id}"})

    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({"message": f"Successfully deleted ticket with ticket_id: {ticket_id}"}) """
    
    
    



    