from app.models import Mechanic, Ticket
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
        # seed mechanics and tickets
        mechanics = [
            Mechanic(name='test0', email='test0@example.com', phone="1111111111", salary=100000),
            Mechanic(name='test1', email='test1@example.com', phone="2222222222", salary=200000),
            Mechanic(name='test2', email='test2@example.com', phone="3333333333", salary=300000),
            Mechanic(name='test3', email='test3@example.com', phone="4444444444", salary=400000),
        ]
        tickets = [
            Ticket(VIN="1111111", service_date=date.today(), service_description="test description 0"),
            Ticket(VIN="2222222", service_date=date.today(), service_description="test description 1"),
            Ticket(VIN="3333333", service_date=date.today(), service_description="test description 2"),
            Ticket(VIN="4444444", service_date=date.today(), service_description="test description 3"),
            Ticket(VIN="5555555", service_date=date.today(), service_description="test description 4")
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
        
        
        

        
        
       