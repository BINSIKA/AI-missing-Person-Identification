from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from identify import checkpersonsimilarity
from database import get_all_persons

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/search', methods=['GET', 'POST'])
def searchperson():
    if request.method == 'POST':
        search_image = request.files.get('searchimage')
        if not search_image:
            return render_template('search.html', error="No image uploaded")

        # Save uploaded image temporarily
        filename = secure_filename(search_image.filename)
        search_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        search_image.save(search_path)

        found_person = None
        # Query all persons from the database
        persons = get_all_persons()

        # Check each person's image against uploaded image
        for person in persons:
            person_image_path = person['image']  # Get image path from DB

            # Create absolute path if needed
            if not os.path.isabs(person_image_path):
                person_image_path = os.path.join(app.root_path, person_image_path)

            if os.path.exists(person_image_path):
                # Use the utility function to check similarity
                result = checkpersonsimilarity(person_image_path, search_path, tolerance=0.6)
                if result.startswith("PERSON FOUND"):
                    found_person = person
                    break

        # Remove uploaded temp image file
        os.remove(search_path)

        # Render the result page accordingly
        if found_person:
            return render_template('result_found.html', person=found_person)
        else:
            return render_template('result_notfound.html')

    # If GET request, show the search/upload page
    return render_template('search.html')

