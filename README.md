A facial recognition web application that helps locate missing persons using AI-powered image search, GPS-based sightings logging, and a secure database system.

** Overview**
Every year, thousands of missing person cases go unresolved due to slow, manual identification processes. This project addresses that by building an automated AI system that can match facial features from camera feeds or uploaded images against a database of missing persons — enabling faster identification and real-time sightings tracking.

**Features**

       Face Recognition — Match uploaded photos or live camera input against a registered database of missing persons
       GPS Sightings Logging — Record and track location-based sightings with timestamps
       Secure SQLite Database — Efficient storage and retrieval of facial image data and case records
       Web Interface — Clean Flask-based UI for searching, registering, and managing cases
       Data Integrity — Structured database schema ensuring reliable and accurate image handling


**Tech Stack**
Language: Python 3.8+ 
Face Recognition OpenCV :face_recognition
Web Framework: Flask
Database: SQLite
Frontend: HTML, CSS, JavaScript

**Getting Started**
Prerequisites
       Python 3.8+
       pip
**Installation**
 Clone the repository
       git clone: https://github.com/BINSIKA/AI-missing-Person-Indentification.git
       cd AI-missing-Person-Indentification

**Install dependencies**
pip install -r requirements.txt

**Run the application**
python app.py

**Usage**

Open your browser and go to http://localhost:5000
Register a missing person with their photo and details
Search by uploading a photo or using the live camera
View sightings log with GPS coordinates and timestamps


**How It Works**

Input Image / Camera Feed
        ↓
Face Detection (OpenCV)
        ↓
Face Encoding (128-d vector)
        ↓
Compare against Database
        ↓
Match Found? → Log Sighting + GPS
        ↓
Display Result on Web UI

**Key Modules**

Face Recognition Engine
       Encodes facial features into 128-dimensional vectors
       Uses Euclidean distance to compare and match faces
       Handles multiple faces in a single image
GPS Sightings Logger
       Records location, date, and time for every confirmed sighting
       Stores structured data in SQLite for fast querying
Web Application
       Register missing persons with name, age, last seen location, and photo
       Search interface supports both image upload and webcam input
       
**Future Improvements**

       Real-time CCTV integration
        Mobile-responsive UI
        Email/SMS alert system on match
        Multi-face detection in crowd images
        Cloud database integration
