from app.models import Mechanic
from app.extensions import db
from app import create_app
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
       
       