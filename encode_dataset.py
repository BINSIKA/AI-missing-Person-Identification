import os
import face_recognition
import numpy as np
# Import the database manager functions
import database as db_manager 

# Define the path to the uploads folder, relative to where this script is run
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

def get_face_encoding(image_path):
    """
    Loads an image, finds a face, and returns its 128-dimension encoding as a list.
    Returns None if no face is found or an error occurs.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if encodings:
            # Return the first face found, converted to a list
            return encodings[0].tolist() 
        return None
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def rebuild_encodings():
    """
    Fetches all persons from the database, recalculates their face encodings, 
    and updates the database records.
    """
    # Initialize the database connection and ensure the table exists
    db_manager.init_db()
    
    # 1. Fetch all existing persons
    persons = db_manager.get_all_persons()
    
    conn = db_manager.get_db_connection()
    c = conn.cursor()

    print(f"Starting encoding rebuild for {len(persons)} records...")

    for p in persons:
        # Construct the full image path
        image_filename = p.get('image_filename')
        person_id = p.get('id')
        
        if not image_filename:
            print(f"Skipping ID {person_id}: No image filename found.")
            continue
            
        img_path = os.path.join(UPLOAD_FOLDER, image_filename)
        
        if os.path.exists(img_path):
            face_encoding_list = get_face_encoding(img_path)
            
            if face_encoding_list:
                # Convert the encoding list to JSON string for storage
                encoding_json = json.dumps(face_encoding_list)
                
                # 2. Update the specific person record in the database
                c.execute("UPDATE persons SET encoding_json = ? WHERE id = ?", 
                          (encoding_json, person_id))
                print(f"Updated encoding for ID {person_id}: {p.get('name')}")
            else:
                # Clear existing encoding if a face is no longer detected
                c.execute("UPDATE persons SET encoding_json = NULL WHERE id = ?", (person_id,))
                print(f"No face found in image for ID {person_id}: {p.get('name')}. Encoding cleared.")
        else:
            print(f"Image file not found for ID {person_id}: {p.get('name')} at {img_path}")

    # Commit all updates at once
    conn.commit()
    conn.close()
    print("Encoding rebuild complete.")

if __name__ == '__main__':
    rebuild_encodings()
