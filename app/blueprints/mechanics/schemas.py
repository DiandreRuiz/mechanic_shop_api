from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_fk=True
        
class MechanicWithTicketCountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_fk = True
        fields = ("name", "email", "ticket_count")
    
    ticket_count = fields.Method("get_ticket_count", dump_only=True)
    def get_ticket_count(self, obj):
        return len(obj.tickets) if obj.tickets else 0
        
        
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanics_with_ticket_count_schema = MechanicWithTicketCountSchema(many=True)