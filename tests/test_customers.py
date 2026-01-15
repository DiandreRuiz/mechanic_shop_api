from app import create_app
from app.extensions import db
from app.models import Customer
from app.blueprints.customers.schemas import customer_schema
from sqlalchemy import select
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
    
    def test_invalid_login(self):
        credentials = {
            "email": "andrew@example.com",
            "password": "bad-password"
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 401)
        
    def test_get_customer(self):
        # Add known target Customer
        self.customer = Customer(
            name="Test-Customer",
            email="test-email@example.com",
            phone="2159151004",
            password="AnExamplePassword"
        )
        db.session.add(self.customer)
        db.session.commit()
        
        # Attempt to get target customer
        response = self.client.get(f'/customers/{self.customer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Test-Customer")
            
    def test_add_customer(self):
        customer_payload = {
            "name": "Billy The Example",
            "email": "billybob@gmail.com",
            "phone": "1222222222",
            "password": "an example password"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Billy The Example")
        
    def test_add_invalid_customer(self):
        customer_payload = {
            "namef": "Billy The Example",
            "email": "billybob@gmail.com",
            "phone": "1222222222",
            "password": "an example password"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)

    def test_update_customer(self):
        # seed customer
        customer = Customer(
            name="Test-Customer",
            email="test-email@example.com",
            phone="2159151004",
            password="AnExamplePassword"
        )
        db.session.add(customer)
        db.session.commit()
        
        # update seeded customer
        payload = {
            "name": "Updated Name",
            "email": "UpdatedEmail@gmail.com",
            "phone": "Updated Phone",
            "password": "Updated Password"
        }
        
        # test status_code
        response = self.client.put(f"/customers/{customer.id}", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # test data persistence (no password)
        for k in payload:
            if k != 'password':
                self.assertEqual(response.json[k], payload[k])
                
        # test password separately due to load_only=True in 
        # schema def for 'password' field in Customer
        
        db.session.refresh(customer) # protect against stale cache
        live_password = customer.password
        self.assertEqual(payload['password'], live_password)
        
        