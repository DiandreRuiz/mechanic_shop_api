from app.models import Customer
from app.extensions import db
from app.utils.util import encode_token
import unittest

class TestTickets(unittest.TestCase):
    
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