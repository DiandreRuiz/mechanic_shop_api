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
        
        # test persistence via id
        expected = { t.id for t in tickets }
        received = { item['id'] for item in response.json }
        self.assertEqual(expected, received)
        
        # test serialization
        fields = ['VIN', 'service_date', 'service_description', 'customer_id']
        for f in fields:
            expected = { getattr(t, f) for t in tickets }
            if f == 'service_date': # normalize for ORM objects
                expected = { d.isoformat() for d in expected }
                
            received = { item[f] for item in response.json }
            self.assertEqual(expected, received)
            
    def test_get_ticket(self):
        
        # seed customer
        customer = Customer(
            name='test_customer',
            email='test@email.com',
            phone='2159151004',
            password='test-password'
        )
        
        db.session.add(customer)
        db.session.flush()
        
        # seed tickets
        tickets = [
            Ticket(VIN="1111111", service_date=date.today(), service_description="test description 0", customer_id=customer.id),
            Ticket(VIN="2222222", service_date=date.today(), service_description="test description 1", customer_id=customer.id),
            Ticket(VIN="3333333", service_date=date.today(), service_description="test description 2", customer_id=customer.id),
            Ticket(VIN="4444444", service_date=date.today(), service_description="test description 3", customer_id=customer.id),
            Ticket(VIN="5555555", service_date=date.today(), service_description="test description 4", customer_id=customer.id)
        ]
        
        db.session.add_all(tickets)
        db.session.commit()
        
        # test status_code
        t_0, t_1, t_2 = tickets[0], tickets[1], tickets[2]
        test_tickets = [t_0, t_1, t_2]
        
        # test identity & data
        fields = ['VIN', 'service_date', 'service_description', 'customer_id']
        for t in test_tickets:
            response = self.client.get(f'/tickets/{t.id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['id'], t.id)
            for f in fields:
                expected = getattr(t, f)
                if f == "service_date": expected = expected.isoformat()
                self.assertEqual(response.json[f], expected)
                
        # test key presence
        for t in test_tickets:
            response = self.client.get(f'/tickets/{t.id}')
            for f in fields + ['id']:
                self.assertIn(f, response.json)

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
        
    def test_create_ticket(self):
        """
        - test status
        - test fields
        - test persistence
        - test payload > data
        - test malformed
        - test customer not found
        """
        # seed customer
        customer = Customer(
            name='test_customer',
            email='test@email.com',
            phone='2159151004',
            password='test-password'
        )
        
        db.session.add(customer)
        db.session.flush()
        
        payload = {
            'VIN': '1111111',
            'service_date': '2026-01-06',
            'service_description': 'this is an example description',
            'customer_id': customer.id
        }
        
        # test status & fields
        fields = ['VIN', 'service_date', 'service_description', 'customer_id']
        response = self.client.post('/tickets/', json=payload)
        self.assertEqual(response.status_code, 201)
        for f in fields:
            self.assertIn(f, response.json)
        
        # test payload > data
        for f in fields:
            self.assertEqual(response.json[f], payload[f])
        
        # test persistance
        created = db.session.get(Ticket, response.json['id'])
        self.assertIsNotNone(created)
        
        # test customer not found
        payload['customer_id'] = 9999
        response = self.client.post('/tickets/', json=payload)
        self.assertEqual(response.status_code, 404)
        
        # test malformed
        del payload['VIN']
        response = self.client.post('/tickets/', json=payload)
        self.assertEqual(response.status_code, 400)

        # test empty request body
        response = self.client.post('/tickets/', json={})
        self.assertEqual(response.status_code, 400)
        
        
        
        