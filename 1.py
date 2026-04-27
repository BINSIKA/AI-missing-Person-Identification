from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import face_recognition
import cv2
import numpy as np
import os
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database Model
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    details = db.Column(db.String(500))
    encoding = db.Column(db.PickleType)

# Create DB
with app.app_context():
    db.create_all()

# Function to encode face
def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return encodings[0] if encodings else None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No image uploaded"

        file = request.files['image']
        if file.filename == '':
            return "No file selected"

        filename = str(uuid.uuid4()) + ".jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        uploaded_encoding = encode_face(filepath)
        if uploaded_encoding is None:
            return "No face detected in uploaded image."

        # Search for match
        persons = Person.query.all()
        matches = []
        for person in persons:
            match = face_recognition.compare_faces([person.encoding], uploaded_encoding, tolerance=0.5)
            distance = face_recognition.face_distance([person.encoding], uploaded_encoding)
            if match[0]:
                matches.append((person, distance[0]))

        matches = sorted(matches, key=lambda x: x[1])  # Sort by similarity

        if matches:
            return render_template('result.html', match=matches[0][0], distance=matches[0][1])
        else:
            return render_template('result.html', match=None)

    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']
        file = request.files['image']

        filename = str(uuid.uuid4()) + ".jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        encoding = encode_face(filepath)
        if encoding is None:
            return "No face detected in uploaded image."

        new_person = Person(name=name, details=details, encoding=encoding)
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)
