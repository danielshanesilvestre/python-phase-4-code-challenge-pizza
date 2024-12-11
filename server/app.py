#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantsIndex(Resource):
    def get(self):
        return [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in Restaurant.query.all()], 200

class RestaurantByID(Resource):
    def get(self, id):
        
        if restaurant := Restaurant.query.filter_by(id=id).first():
            return restaurant.to_dict(), 200
        else:
            return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        if restaurant := Restaurant.query.filter_by(id=id).first():
            db.session.delete(restaurant)
            db.session.commit()

            return {}, 204
        else:
            return {"error": "Restaurant not found"}, 404

class PizzasIndex(Resource):
    def get(self):
        return [pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in Pizza.query.all()], 200
        pass

class RestaurantPizzasIndex(Resource):
    def post(self):
        request_json = request.get_json()

        try:
            restaurant_pizza = RestaurantPizza(
                price=request_json.get("price"),
                pizza_id=request_json.get("pizza_id"),
                restaurant_id=request_json.get("restaurant_id")
            )

            db.session.add(restaurant_pizza)
            db.session.commit()

            return restaurant_pizza.to_dict(), 201
        except ValueError:
            pass
        
        return {"errors": ["validation errors"]}, 400

api.add_resource(RestaurantsIndex, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(PizzasIndex, "/pizzas")
api.add_resource(RestaurantPizzasIndex, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
