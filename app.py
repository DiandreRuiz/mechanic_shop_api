print("starting imports")

from app import create_app
from app.extensions import db

print("start")
app = create_app("DevelopmentConfig")
print("app created")

# Create tables in metadata
with app.app_context():
    db.create_all()
    print("ORM tables created")
    
app.run(debug=True, port=5001)
print("App Ran")