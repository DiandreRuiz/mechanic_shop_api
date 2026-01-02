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