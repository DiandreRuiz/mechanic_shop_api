from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request, jsonify
import jose


SECRET_KEY=""

def encode_token(customer_id): # uses unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Sets expiration time of 1 hour
        'iat': datetime.now(timezone.utc), # "Issued At" time
        'sub': str(customer_id) # subscriber must be a string else token will be malformed and won't be decodable
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256") # Create the actual token with appropriate attributes
    
    return token

# Checks the request 'Authorization' header for a JWT. Parses this token
# for token string & decodes token string to deduce customer id. If
# token string cannot be decoded, we throw an error for an invalid token.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        # Look for token in authorization header
        token = None
        auth_section = request.headers.get('Authorization', '')
        if auth_section:
            token = auth_section.split(" ")[1] if 'Bearer' in auth_section else auth_section
        
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])    
            customer_id = data['sub'] # Fetch the user_id
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': "Token has expired!"}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': "Invalid Token!"}), 401
        
        return f(customer_id, *args, **kwargs)
    
    return decorated
        
    