import unittest
from app import app, db  # Import app and db
from app.models import Asset, Liability
import os

class TestModels(unittest.TestCase):
    def setUp(self):
        # Ensure FLASK_ENV is set for testing configuration in app/__init__.py
        # However, directly setting app.config here ensures override for test environment
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = app.app_context()
        self.app_context.push() # Push an application context
        db.create_all() # Create all tables for the in-memory database

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop() # Pop the application context

    def test_create_asset(self):
        # Test creating an Asset instance
        asset = Asset(name="Test Asset", type="Savings", value=100.00)
        db.session.add(asset)
        db.session.commit()

        queried_asset = Asset.query.filter_by(name="Test Asset").first()
        self.assertIsNotNone(queried_asset)
        self.assertEqual(queried_asset.value, 100.00)

    def test_create_liability(self):
        # Test creating a Liability instance
        liability = Liability(name="Test Liability", type="Credit Card", amount_owed=50.00)
        db.session.add(liability)
        db.session.commit()

        queried_liability = Liability.query.filter_by(name="Test Liability").first()
        self.assertIsNotNone(queried_liability)
        self.assertEqual(queried_liability.amount_owed, 50.00)

if __name__ == '__main__':
    unittest.main()
