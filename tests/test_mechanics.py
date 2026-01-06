from app.models import Mechanic, Ticket, Customer
from app.extensions import db
from app import create_app
from datetime import date
import unittest

class TestMechanics(unittest.TestCase):
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
        
    def test_get_mechanics(self):
        # seed known mechanics
        mechanics = [
            Mechanic(name='test0', email='test0@example.com', phone="1111111111", salary=100000),
            Mechanic(name='test1', email='test1@example.com', phone="2222222222", salary=200000),
            Mechanic(name='test2', email='test2@example.com', phone="3333333333", salary=300000),
            Mechanic(name='test3', email='test3@example.com', phone="4444444444", salary=400000),
        ]
        db.session.add_all(mechanics)
        db.session.commit()
        
        # test get
        response = self.client.get('/mechanics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), len(mechanics))
        
        # assert all fields are matched
        fields = ['name', 'email', 'phone', 'salary'] 
        for f in fields:
            expected = { getattr(m, f) for m in mechanics }
            response_values = { item[f] for item in response.json }
            self.assertSetEqual(expected, response_values)
            
    def test_get_top_3_mechanics(self):
        # seed customer, mechanics and tickets
        customer = Customer(
            name='test_customer',
            email='test@email.com',
            phone='2159151004',
            password='test-password'
        )
        
        db.session.add(customer)
        db.session.flush()
        
        mechanics = [
            Mechanic(name='test0', email='test0@example.com', phone="1111111111", salary=100000),
            Mechanic(name='test1', email='test1@example.com', phone="2222222222", salary=200000),
            Mechanic(name='test2', email='test2@example.com', phone="3333333333", salary=300000),
            Mechanic(name='test3', email='test3@example.com', phone="4444444444", salary=400000),
        ]
        tickets = [
            Ticket(VIN="1111111", service_date=date.today(), service_description="test description 0", customer_id=customer.id),
            Ticket(VIN="2222222", service_date=date.today(), service_description="test description 1", customer_id=customer.id),
            Ticket(VIN="3333333", service_date=date.today(), service_description="test description 2", customer_id=customer.id),
            Ticket(VIN="4444444", service_date=date.today(), service_description="test description 3", customer_id=customer.id),
            Ticket(VIN="5555555", service_date=date.today(), service_description="test description 4", customer_id=customer.id)
        ]
        
        # seed ticket assignments
        m_0, m_1, m_2 = mechanics[0], mechanics[1], mechanics[2]
        
        m_0.tickets.extend(tickets[0:3])
        m_1.tickets.append(tickets[3])
        m_2.tickets.append(tickets[4])
        
        # add all rows
        db.session.add_all(mechanics + tickets)
        db.session.commit()
        
        response = self.client.get('/mechanics/top-3-mechanics')
        
        # test response order
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        
        expected_names = [m_0.name, m_1.name, m_2.name]
        actual_names = [item['name'] for item in response.json]
        self.assertEqual(actual_names, expected_names)
    
    def test_create_mechanic(self):
        """
        test 200 & response.json
        test uniqueness check
        """
        
        # test status & fields
        payload = {
            'name': 'test0',
            'email': 'test@example.com',
            'phone': '2159151004',
            'salary': 100000
        }
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        
        fields = ['name', 'email', 'phone', 'salary']
        for f in fields:
            self.assertEqual(response.json[f], payload[f])
            
        # test persistence
        created_id = response.json['id']
        created = db.session.get(Mechanic, created_id)
        self.assertIsNotNone(created)
        self.assertEqual(created.email, payload['email'])
        
        # test uniqueness violation
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], f"Mechanic already exists with email: {payload['email']}")
        
        
        

        
        
       