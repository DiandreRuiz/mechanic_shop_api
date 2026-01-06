from app import create_app
from app.extensions import db
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        
        # create app context to use during this test
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        
        self.client = self.app.test_client()
            
    def tearDown(self):
        # clean up resources including db session (db connection) & pop app context
        db.session.remove()
        db.engine.dispose()
        self.ctx.pop()       
            
    def test_customer(self):
        customer_payload = {
            "name": "Billy The Example",
            "email": "billybob@gmail.com",
            "phone": "1222222222",
            "password": "an example password"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Billy The Example")
        
    def test_invalid_customer(self):
        customer_payload = {
            "namef": "Billy The Example",
            "email": "billybob@gmail.com",
            "phone": "1222222222",
            "password": "an example password"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)