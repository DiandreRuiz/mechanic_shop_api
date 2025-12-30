from typing import Dict
from app.extensions import ma
from marshmallow import fields
from app.models import Ticket
from app.blueprints.mechanics.schemas import MechanicSchema


# Parent Class: Inherits from a marshmallow class to know what to do with the information in the Meta class
# Meta Class: Gives the information that the parent class needs to do what it's inheritance decides
class TicketSchema(ma.SQLAlchemyAutoSchema): # Inheritance allowing for TicketSchema to understand what to do with Meta
    class Meta:
        model = Ticket
        include_fk=True

class UpdateTicketMechanicsResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        include_fk=True
    
    mechanics = fields.Nested(MechanicSchema(exclude=["salary", "phone", "email"]), many=True, dump_only=True)
        
class UpdateTicketMechanicsSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids") # White list: "Of the fields we have, which do we want to use?"

class TicketInventoryItemInputSchema(ma.Schema):
    inventory_id = fields.Int(required=True)
    quantity = fields.Int(required=True)

class AddTicketInventoryItemsSchema(ma.Schema):
    add_inventory_ids = fields.List(fields.Nested(TicketInventoryItemInputSchema), required=True)
    
    class Meta:
        fields = ("add_inventory_ids")
        
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
update_ticket_mechanics_schema = UpdateTicketMechanicsSchema()
update_ticket_mechanics_response_schema = UpdateTicketMechanicsResponseSchema()
add_ticket_inventory_items_schema = AddTicketInventoryItemsSchema()