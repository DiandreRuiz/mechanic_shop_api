from app import create_app
from app.extensions import db
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            
    def test_customer(self):
        customer_payload = {
            "name": "Diandre The Example",
            "email": "druiz@email.com",
            "phone": "2159151004",
            "password": "this is my new password"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Diandre The Example")