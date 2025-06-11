from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Asset, Liability

@app.route('/')
@app.route('/index')
def index():
    assets = Asset.query.all()
    liabilities = Liability.query.all()

    total_assets = sum(asset.value for asset in assets)
    total_liabilities = sum(liability.amount_owed for liability in liabilities)
    net_worth = total_assets - total_liabilities

    return render_template('index.html',
                           title='Home',
                           assets=assets,
                           liabilities=liabilities,
                           total_assets=total_assets,
                           total_liabilities=total_liabilities,
                           net_worth=net_worth)

# --- Asset Routes ---
@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        name = request.form['name']
        asset_type = request.form['type']
        value = float(request.form['value'])
        new_asset = Asset(name=name, type=asset_type, value=value)
        db.session.add(new_asset)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_asset.html', title='Add Asset')

@app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    asset_to_edit = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        asset_to_edit.name = request.form['name']
        asset_to_edit.type = request.form['type']
        asset_to_edit.value = float(request.form['value'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_asset.html', title='Edit Asset', asset=asset_to_edit)

@app.route('/delete_asset/<int:asset_id>', methods=['POST'])
def delete_asset(asset_id):
    asset_to_delete = Asset.query.get_or_404(asset_id)
    db.session.delete(asset_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

# --- Liability Routes ---
@app.route('/add_liability', methods=['GET', 'POST'])
def add_liability():
    if request.method == 'POST':
        name = request.form['name']
        liability_type = request.form['type']
        amount_owed = float(request.form['amount_owed'])
        new_liability = Liability(name=name, type=liability_type, amount_owed=amount_owed)
        db.session.add(new_liability)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_liability.html', title='Add Liability')

@app.route('/edit_liability/<int:liability_id>', methods=['GET', 'POST'])
def edit_liability(liability_id):
    liability_to_edit = Liability.query.get_or_404(liability_id)
    if request.method == 'POST':
        liability_to_edit.name = request.form['name']
        liability_to_edit.type = request.form['type']
        liability_to_edit.amount_owed = float(request.form['amount_owed'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_liability.html', title='Edit Liability', liability=liability_to_edit)

@app.route('/delete_liability/<int:liability_id>', methods=['POST'])
def delete_liability(liability_id):
    liability_to_delete = Liability.query.get_or_404(liability_id)
    db.session.delete(liability_to_delete)
    db.session.commit()
    return redirect(url_for('index'))
