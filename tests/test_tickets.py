from app.models import Customer, Ticket
from app.extensions import db
from app.utils.util import encode_token
from app import create_app
from datetime import date
import unittest

class TestTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()
    
    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.ctx.pop()
    
    def test_get_tickets(self):
        # seed customer & tickets
        customer = Customer(
            name='test_customer',
            email='test@email.com',
            phone='2159151004',
            password='test-password'
        )
        
        db.session.add(customer)
        db.session.flush()
        
        tickets = [
            Ticket(VIN="1111111", service_date=date.today(), service_description="test description 0", customer_id=customer.id),
            Ticket(VIN="2222222", service_date=date.today(), service_description="test description 1", customer_id=customer.id),
            Ticket(VIN="3333333", service_date=date.today(), service_description="test description 2", customer_id=customer.id),
            Ticket(VIN="4444444", service_date=date.today(), service_description="test description 3", customer_id=customer.id),
            Ticket(VIN="5555555", service_date=date.today(), service_description="test description 4", customer_id=customer.id)
        ]
        
        db.session.add_all(tickets)
        db.session.commit()
        
        # test status_code & quantity
        response = self.client.get('/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), len(tickets))
        
        # test fields
        fields = ['VIN', 'service_date', 'service_description', 'customer_id']
        for f in fields:
            expected = { getattr(t, f) for t in tickets }
            received = { item[f] for item in response.json }
            self.assertEqual(expected, received)
        
        
    
    def test_get_my_tickets(self):
        self.customer = Customer(
            name="john pork",
            phone="2224445555",
            email="johnpork@gmail.com",
            password="testpassword"
        )
        db.session.add(self.customer)
        db.session.commit()
        
        self.token = encode_token(self.customer.id)
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.get("/tickets/my-tickets", headers=headers)
        
        self.assertEqual(response.status_code, 200)