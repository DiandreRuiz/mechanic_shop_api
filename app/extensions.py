from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_caching import Cache
from flask_limiter.util import get_remote_address
from app.models import Base

# Instantiations of extensions to be imported elsewhere
db = SQLAlchemy(model_class=Base)
ma = Marshmallow()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
limiter = Limiter(key_func=get_remote_address) # key_function = function returning domain to rate limit based on