from app.blueprints.tickets.schemas import UpdateTicketMechanicsSchema
from app.models import Customer, Ticket, Mechanic
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
        
    def test_update_ticket(self):
        # NOTE: Partial test coverage
        
        # seed customer
        customer = Customer(name='test0', phone='1234567890', email='test@example.com', password='testpassword')
        db.session.add(customer)
        db.session.flush()
        
        # seed ticket
        ticket = Ticket(VIN='1111111', service_date=date.today(), service_description='example description', customer_id=customer.id)
        db.session.add(ticket)
        db.session.commit()
        
        payload = {
            'VIN': '2222222',
            'service_date': '2026-01-07',
            'service_description': 'updated description',
            'customer_id': customer.id
        }
        token = encode_token(customer.id)
        headers = { 'Authorization': f'Bearer {token}' }
        response = self.client.put(f'/tickets/{ticket.id}', json=payload, headers=headers)
        
        # test status_code & ORM update
        self.assertEqual(response.status_code, 200)
        fields = ['VIN', 'service_date', 'service_description', 'customer_id']
        for f in fields:
            self.assertEqual(response.json[f], payload[f])
            
        # test missing data
        payload = {}
        response = self.client.put(f'/tickets/{ticket.id}', json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Empty request body')
        
        # test missing auth token
        payload = {
            'VIN': '2222222',
            'service_date': '2026-01-07',
            'service_description': 'updated description',
            'customer_id': customer.id
        }
        response = self.client.put(f'/tickets/{ticket.id}', json=payload)
        self.assertEqual(response.status_code, 401) # unauthorized response
        self.assertEqual(response.json['message'], 'Token is missing!')
        
    def test_update_ticket_mechanics(self):
        # seed customers
        existing_customers = [
            Customer(name='test0', phone='1111111111', email='me0@ex.com', password='testpass0'),
            Customer(name='test1', phone='2222222222', email='me1@ex.com', password='testpass1'),
        ]
        db.session.add_all(existing_customers)
        db.session.flush()

        # seed ticket owned by customer0
        ticket = Ticket(
            VIN=0,
            service_date=date.today(),
            service_description='example description',
            customer_id=existing_customers[0].id
        )
        db.session.add(ticket)
        db.session.commit()

        # seed mechanics
        m1 = Mechanic(name='m1', email='m1@me.com', phone='9999999999', salary=100000)
        m2 = Mechanic(name='m2', email='m2@me.com', phone='8888888888', salary=120000)
        db.session.add_all([m1, m2])
        db.session.commit()

        # ADD m1
        payload_add = {"add_mechanic_ids": [m1.id], "remove_mechanic_ids": []}
        resp = self.client.put(f"/tickets/{ticket.id}/update-mechanics", json=payload_add)
        self.assertEqual(resp.status_code, 200)

        db.session.expire_all()
        updated_ticket = db.session.get(Ticket, ticket.id)
        self.assertIn(m1, updated_ticket.mechanics)

        # ADD m2, REMOVE m1
        payload_swap = {"add_mechanic_ids": [m2.id], "remove_mechanic_ids": [m1.id]}
        resp2 = self.client.put(f"/tickets/{ticket.id}/update-mechanics", json=payload_swap)
        self.assertEqual(resp2.status_code, 200)

        db.session.expire_all()
        updated_ticket2 = db.session.get(Ticket, ticket.id)
        self.assertIn(m2, updated_ticket2.mechanics)
        self.assertNotIn(m1, updated_ticket2.mechanics)
        
    def test_assign_mechanic(self):
        # NOTE: Partial test coverage

        # seed customer
        customer = Customer(
            name='test_customer',
            email='test@email.com',
            phone='2159151004',
            password='test-password'
        )
        db.session.add(customer)
        db.session.flush()

        # seed ticket
        ticket = Ticket(
            VIN="1111111",
            service_date=date.today(),
            service_description="test description",
            customer_id=customer.id
        )
        db.session.add(ticket)
        db.session.commit()

        # seed mechanic
        mechanic = Mechanic(
            name='test_mechanic',
            email='mechanic@email.com',
            phone='9999999999',
            salary=100000
        )
        db.session.add(mechanic)
        db.session.commit()

        # test ticket not found
        response = self.client.put(f"/tickets/999999/assign-mechanic/{mechanic.id}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Could not locate Ticket with id: 999999")

        # test mechanic not found
        response = self.client.put(f"/tickets/{ticket.id}/assign-mechanic/999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Could not locate mechanic with id: 999999")

        # test assign mechanic (happy path)
        response = self.client.put(f"/tickets/{ticket.id}/assign-mechanic/{mechanic.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Mechanic successfully assigned to ticket.")
        self.assertEqual(response.json["ticket_id"], ticket.id)
        self.assertEqual(response.json["mechanic_id"], mechanic.id)

        # test persistence
        db.session.expire_all()
        updated_ticket = db.session.get(Ticket, ticket.id)
        self.assertIn(mechanic, updated_ticket.mechanics)
        self.assertEqual(len(updated_ticket.mechanics), 1)

        # test duplicate prevention
        response = self.client.put(f"/tickets/{ticket.id}/assign-mechanic/{mechanic.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Mechanic is already assigned to this ticket.")
        self.assertEqual(response.json["ticket_id"], ticket.id)
        self.assertEqual(response.json["mechanic_id"], mechanic.id)

        # test no duplicate association created
        db.session.expire_all()
        updated_ticket_2 = db.session.get(Ticket, ticket.id)
        self.assertIn(mechanic, updated_ticket_2.mechanics)
        self.assertEqual(len(updated_ticket_2.mechanics), 1)
        
        
        
        
        
        