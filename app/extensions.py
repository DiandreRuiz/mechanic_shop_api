from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from app.models import Base

# Instantiations of extensions to be imported elsewhere
db = SQLAlchemy(model_class=Base)
ma = Marshmallow()