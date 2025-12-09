from app.extensions import ma
from marshmallow import fields
from app.models import Ticket

# Parent Class: Inherits from a marshmallow class to know what to do with the information in the Meta class
# Meta Class: Gives the information that the parent class needs to do what it's inheritance decides

class TicketSchema(ma.SQLAlchemyAutoSchema): # Inheritance allowing for TicketSchema to understand what to do with Meta
    class Meta:
        model = Ticket
        include_fk=True
        
class UpdateTicketMechanicsSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_book_ids", "remove_book_ids") # White list: "Of the fields we have, which do we want to use?"
        
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
update_ticket_mechanics_schema = UpdateTicketMechanicsSchema()