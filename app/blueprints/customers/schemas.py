from app.extensions import ma
from app.models import Customer
from marshmallow import EXCLUDE, fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_fk=True
        unknown = EXCLUDE
        
class LoginSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE
    
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
        
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()