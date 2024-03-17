from datetime import timedelta

from flask import Flask, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_KEY')
jwt = JWTManager(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:2112@localhost:5432/music_shop"

# строка подключения приложения к локальной бд
app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
                                         f"{os.getenv('PG_PASS')}@localhost:5432/music_shop")

# строка подключения приложения внутри докера к его контейнерам
# app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
#                                          f"{os.getenv('POSTGRES_PASSWORD')}@dbserver:5432/music_shop")
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


@app.route('/', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    if email == os.getenv('APP_USER') and password == os.getenv('APP_USER_PASSWORD'):
        expire_time = 24
        access_token = create_access_token(identity=email, expires_delta=timedelta(expire_time))
        flash("Успешная авторизация", 'success')
        return jsonify(message='Login successful!', access_token=access_token)
    else:
        return jsonify(message='Login failed!')


# @app.route('/instruments', methods=['POST', 'GET'], headers={'Authorization': f'Bearer {request.args.access_token}'})
@app.route('/instruments', methods=['POST', 'GET'])
@jwt_required()
def handle_instrument():
    current_user = get_jwt_identity()
    if current_user:
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
            return {"count": len(results), "instruments": results, "token": request.args}
    else:
        return jsonify(message='Invalid token')


@app.route('/instrument/<inst_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_instrument_gpd(inst_id):
    current_user = get_jwt_identity()
    if current_user:
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
    else:
        return jsonify(message='Invalid token')


# @app.route('/instrument/buying/<inst_id>', methods=['PATCH'])
@app.route('/instrument/buying/<inst_id>')
@jwt_required()
def buy_one_inst(inst_id):
    current_user = get_jwt_identity()
    if current_user:
        inst = Instrument.query.get_or_404(inst_id)
        inst.quantity -= 1
        db.session.commit()
        return {"message": f"instrument {inst.name} has been bought successfully."}
    else:
        return jsonify(message='Invalid token')


#  накинуть сюда аутентификацию и авторизацию, получать jwt token который использоваться на всех
#  ендпоинтах, то есть сделать проверку на права (permissions)


# return redirect(url_for('handle_instrument') + f'?access_token={access_token}')
# строка выше позваляет делать переадресацию на другой эндпоинт с передачей токена в него,
# эту строку следует использовать когда на принимающем эндпоинте нет декоратора - @jwt_required() и дальше в логике
# нужно проверять токен на корректность, для проверки работы в postman неподходит вариант переадрисации.
# нужно брать и руками вставлять токен чтобы делать дальнейшие запросы.

if __name__ == '__main__':
    app.secret_key = os.getenv('FLASK_KEY')
    app.run(debug=True, port=8000, host='0.0.0.0')
