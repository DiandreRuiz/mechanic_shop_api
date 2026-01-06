from app import create_app
from app.extensions import db
from app.models import Inventory
from app.blueprints.inventory.schemas import inventory_item_schema
import unittest

class TestInventory(unittest.TestCase):
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
        
    def test_get_inventory(self):
        # Add test inventory items
        test_invetory_items = [
            Inventory(name="test0", price=1.00),
            Inventory(name="test1", price=5.99),
            Inventory(name="test2", price=2.99)
        ]
        db.session.add_all(test_invetory_items)
        db.session.commit()
        
        # page 1, 1 response per page
        response = self.client.get('/inventory/?per_page=1&page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        p1_1 = response.json[0]
        
        # page 2, 1 response per page
        response = self.client.get('/inventory/?per_page=1&page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        p2_1 = response.json[0]
        
        # pages 1 & 2 return different results
        self.assertFalse(p1_1 == p2_1)
        
        # page 1, 3 responses per page
        response = self.client.get('/inventory/?per_page=3&page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)   
        
        # seeded data check
        response = self.client.get('/inventory/?per_page=3&page=1')
        names = { item["name"] for item in response.json }     
        self.assertSetEqual(names, { i.name for i in test_invetory_items })
        
        # out of range check
        response = self.client.get('/inventory/?per_page=1&page=4')
        self.assertEqual(response.status_code, 200)
    
    def test_duplicate_add_inventory_item(self):
        # seed test item
        inventory_item = Inventory(name="test_item", price=1.99)
        db.session.add(inventory_item)
        db.session.commit()
        
        # test duplicate warning
        payload = {
            "name": inventory_item.name,
            "price": inventory_item.price
        }
        response = self.client.post('/inventory/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json['error'],
            f"Inventory item of name '{inventory_item.name}' already exists!"                 
        )
    
    def test_add_inventory_item(self):
        # test post of inventory item
        inventory_item = {
            'name': 'test_item',
            'price': 2.99
        }
        response = self.client.post('/inventory/', json=inventory_item)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)
        self.assertEqual(response.json['name'], inventory_item['name'])
        self.assertEqual(response.json['price'], inventory_item['price'])
        
    def test_update_inventory_item(self):
        # seed known inventory item
        self.inventory_item = Inventory(name="test_item", price=6.99)
        db.session.add(self.inventory_item)
        db.session.commit()
        
        # update seeded item & test
        updated_item = {
            'name': 'updated_name',
            'price': 9.99
        }
        response = self.client.put(f'/inventory/{self.inventory_item.id}', json=updated_item)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], self.inventory_item.id)
        self.assertEqual(response.json['name'], updated_item['name'])
        self.assertEqual(response.json['price'], updated_item['price'])
        
        # verify db persistence via ORM object
        db.session.refresh(self.inventory_item)
        self.assertEqual(self.inventory_item.name, updated_item['name'])
        self.assertEqual(self.inventory_item.price, updated_item['price'])
        
    def test_delete_inventory_item(self):
        # seed known inventory item to delete
        self.inventory_item = Inventory(name='test_item', price=1.99)
        db.session.add(self.inventory_item)
        db.session.commit()
        
        # test deletion of known item
        response = self.client.delete(f'/inventory/{self.inventory_item.id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(response.data)
        
        # assert record is gone
        self.assertIsNone(db.session.get(Inventory, self.inventory_item.id))
        
        # test deletion of non-existant item
        nonexistant_id = self.inventory_item.id + 9999
        response = self.client.delete(f'/inventory/{nonexistant_id}')
        self.assertEqual(response.status_code, 404)