from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:2112@localhost:5432/music_shop"

# строка подключения приложения к локальной бд
# app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
#                                          f"{os.getenv('PG_PASS')}@localhost:5432/music_shop")

# строка подключения приложения внутри докера к его контейнерам
app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
                                         f"{os.getenv('POSTGRES_PASSWORD')}@dbserver:5432/music_shop")
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Instrument(db.Model):
    __tablename__ = 'instruments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(150))
    quantity = db.Column(db.Integer())

    def __init__(self, name, description, quantity):
        self.name = name
        self.description = description
        self.quantity = quantity

    def __repr__(self):
        return '<Instrument {}>'.format(self.name)


@app.route('/instruments', methods=['POST', 'GET'])
def handle_instrument():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_inst = Instrument(name=data['name'], description=data['description'], quantity=data['quantity'])
            db.session.add(new_inst)
            db.session.commit()
            return {"message": f"instrument {new_inst.name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        inst_ = Instrument.query.all()
        results = [
            {
                "id": inst.id,
                "name": inst.name,
                "description": inst.description,
                "quantity": inst.quantity
            } for inst in inst_]

        return {"count": len(results), "instruments": results}


@app.route('/instrument/<inst_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_instrument_gpd(inst_id):
    inst = Instrument.query.get_or_404(inst_id)
    if request.method == 'GET':
        result = {
            "name": inst.name,
            "description": inst.description,
            "quantity": inst.quantity
        }
        return {"message": "success", "instrument": result}

    elif request.method == 'PUT':
        if request.is_json:
            data = request.get_json()
            inst.name = data['name']
            inst.description = data['description']
            inst.quantity = data['quantity']
            db.session.commit()
            return {"message": f"instrument {inst.name} has been updated successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == "DELETE":
        db.session.delete(inst)
        db.session.commit()
        return {"message": f"instrument {inst.name} has been deleted successfully."}


# @app.route('/instrument/buying/<inst_id>', methods=['PATCH'])
@app.route('/instrument/buying/<inst_id>')
def buy_one_inst(inst_id):
    inst = Instrument.query.get_or_404(inst_id)
    inst.quantity -= 1
    db.session.commit()
    return {"message": f"instrument {inst.name} has been bought successfully."}


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='localhost')
    # app.run(debug=True)
