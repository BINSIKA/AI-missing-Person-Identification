import os, time, threading, base64, io
import face_recognition
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image
import database as db_manager


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


try:
    import winsound
    def play_alarm():
        winsound.Beep(1000, 500)
except ImportError:
    def play_alarm():
        print("ALARM Triggered! (winsound not available on this OS)")

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TOLERANCE = 0.5


SENDER_EMAIL = "personfound1@gmail.com"       
SENDER_PASSWORD ="zynz ilzy csjh psqo" 


db_manager.init_db()

def send_email_alert(email_address, name, lat="0", lng="0", image_path=None):
    if not email_address:
        print("❌ No email address provided. Cannot send alert.")
        return

    link = f"http://www.google.com/maps/place/{lat},{lng}"
    
    try:
       
        msg = MIMEMultipart()
        msg['Subject'] = f"🚨 URGENT: Missing Person {name} Detected!"
        msg['From'] = SENDER_EMAIL
        msg['To'] = email_address

        
        body = f"Hello,\n\nThe system has detected the missing person: {name}.\n\n" \
               f"📍 Live GPS Location: {link}\n\n" \
               f"Please find the camera evidence attached to this email."
        msg.attach(MIMEText(body, 'plain'))

        
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as fp:
                img_data = fp.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            msg.attach(image)

     
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email Sent Successfully to {email_address}!")
    except Exception as e:
        print("❌ Email Error:", e)




@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload_person', methods=['GET', 'POST'])
def upload_person():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email_addr = request.form.get('email') 
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        image_file = request.files['image']

        filename = f"{name}_{int(time.time())}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(filepath)

        img = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(img)
        face_encoding = encodings[0].tolist() if encodings else None

        db_manager.add_person(name, age, gender, height, weight, filename, face_encoding, phone, email_addr)
        return redirect(url_for('view_all'))

    return render_template("upload.html")

@app.route('/search_person', methods=['GET', 'POST'])
def search_person():
    if request.method == 'POST':
        image_file = request.files['search_image']
        filename = f"search_{int(time.time())}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(filepath)

        img = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(img)
        if not encodings:
            return render_template("person_notfound.html")

        search_encoding = encodings[0]
        persons = db_manager.get_all_persons()

        for person in persons:
            if person['face_encoding']:
                matches = face_recognition.compare_faces([person['face_encoding']], search_encoding, tolerance=TOLERANCE)
                if True in matches:
                    # Threading: Send Email in background
                    threading.Thread(target=send_email_alert, args=(person['email'], person['name'], "0", "0", filepath)).start()
                    db_manager.log_sighting(person['id'], filename, "0", "0", "Email Sent")
                    return render_template("person_found.html", person=person, match_score="High Match", image_used=filename)

        return render_template("person_notfound.html")

    return render_template("search.html")

@app.route('/view_all')
def view_all():
    persons = db_manager.get_all_persons()
    return render_template("view_all.html", persons=persons)

@app.route('/camera_search', methods=['GET', 'POST'])
def camera_search():
    if request.method == 'POST':
        image_data = request.form.get('image_data')
        lat = request.form.get('latitude', "0")
        lng = request.form.get('longitude', "0")

        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_array = np.array(img)

        encodings = face_recognition.face_encodings(img_array)
        if not encodings:
            return jsonify({"status": "no_face"})

        frame_encoding = encodings[0]
        persons = db_manager.get_all_persons()

        for person in persons:
            if person['face_encoding']:
                matches = face_recognition.compare_faces([person['face_encoding']], frame_encoding, tolerance=TOLERANCE)
                
                if True in matches:
                    
                    filename = f"live_match_{int(time.time())}.jpg"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    img.save(filepath) 

                    play_alarm()
                    
                    threading.Thread(target=send_email_alert, args=(person['email'], person['name'], lat, lng, filepath)).start()
                    
                    db_manager.log_sighting(person['id'], filename, lat, lng, "Email Sent")
                    
                    return jsonify({
                        "status": "match_found",
                        "name": person['name'],
                        "latitude": lat,
                        "longitude": lng,
                        "redirect_url": url_for('view_all')
                    })

        return jsonify({"status": "no_match"})

    return render_template("camera_search.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')