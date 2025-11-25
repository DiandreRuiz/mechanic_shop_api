from app.extensions import ma
from app.models import Ticket

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)