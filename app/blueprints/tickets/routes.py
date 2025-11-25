from app.blueprints.tickets.schemas import ticket_schema, tickets_schema
from app.extensions import db
from . import tickets_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Ticket
from sqlalchemy import select
from typing import Dict

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

    