from app import db # db should be imported from the app package's __init__

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Asset {self.name}: {self.value}>'

class Liability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount_owed = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Liability {self.name}: {self.amount_owed}>'
