import math

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

EROR = 'Validation Error'


class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    longitude = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)

    def __init__(self, title, longitude, latitude):
        self.title = title
        self.longitude = longitude
        self.latitude = latitude


class ObjectSchema(ma.Schema):

    class Meta:
        fields = ('title', 'longitude', 'latitude')


object_schema = ObjectSchema()

Objects_schema = ObjectSchema(many=True)


@app.route('/objects/create', methods=['POST'])
def add_object():
    try:
        title = str(request.form['title'])
        longitude = int(request.form['longitude'])
        latitude = int(request.form['latitude'])
        new_object = Object(latitude, longitude, title)
        db.session.add(new_object)
        db.session.commit()
        return object_schema.jsonify(new_object)
    except Exception:
        return EROR


@app.route('/objects/get_many', methods=['POST'])
def get_objects():
    all_objects = Object.query.all()
    result = Objects_schema.dump(all_objects)
    return jsonify(result.data)


@app.route('/objects/get/<id>', methods=['POST'])
def get_object(id):
    try:
        object = Object.query.get(id)
        return object_schema.jsonify(object)
    except Exception:
        return EROR


@app.route('/objects/edit/<id>', methods=['POST'])
def update_object(id):
    try:
        object = Object.query.get(id)
        title = str(request.form['title'])
        longitude = int(request.form['longitude'])
        latitude = int(request.form['latitude'])
        object.title = title
        object.longitude = longitude
        object.latitude = latitude
        db.session.commit()
        return object_schema.jsonify(object)
    except Exception:
        return EROR


@app.route('/objects/delete/<id>', methods=['POST'])
def delete_object(id):
    try:
        object = Object.query.get(id)
        db.session.delete(object)
        db.session.commit()
        return object_schema.jsonify(object)
    except Exception:
        return EROR


@app.route('/objects/calculate_distance', methods=['POST'])
def calculate_distance_objects():
    try:
        obj_1 = Object.query.filter(Object.title == \
                request.form['first_object_title']).one_or_none()
        obj_2 = Object.query.filter(Object.title == \
                request.form['second_object_title']).one_or_none()
        p1 = [obj_1.longitude, obj_1.latitude]
        p2 = [obj_2.longitude, obj_2.latitude]
        return str(math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2)))
    except Exception:
        return EROR


if __name__ == '__main__':
    app.run(debug=True)
