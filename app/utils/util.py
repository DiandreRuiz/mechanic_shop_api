from datetime import datetime, timedelta, timezone
from jose import jwt
import jose

SECRET_KEY=""

def encode_token(user_id): # uses unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Sets expiration time of 1 hour
        'iat': datetime.now(timezone.utc), # "Issued At" time
        'sub': str(user_id) # subscribner must be a string else token will be malformed and won't be decodable
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256") # Create the actual token with appropriate attributes
    
    return token
    