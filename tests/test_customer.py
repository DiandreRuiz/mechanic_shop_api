from app import create_app
from app.extensions import db
from app.models import Customer
from app.utils.util import encode_token
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
        
    def test_login(self):
        # Add customer to test for
        self.customer = Customer(
            name="john pork",
            phone="2224445555",
            email="johnpork@gmail.com",
            password="testpassword"
        )
        db.session.add(self.customer)
        db.session.commit()
        
        # Attempt login with token
        credentials = {
            "email": "johnpork@gmail.com",
            "password": "testpassword"
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "success")
        return response.json['auth_token']
    
    def test_invalid_login(self):
        credentials = {
            "email": "andrew@example.com",
            "password": "bad-password"
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 401)
        print(response.json)