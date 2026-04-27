import face_recognition
import os

# --- IMPORTANT: Update these paths with your actual file names ---
# 1. The image to 'extract features' from (the known person)
KNOWN_IMAGE_PATH = "my_original_photo.jpg" 
# 2. The image to 'check' against the known person
UNKNOWN_IMAGE_PATH = "my_second_photo.jpg"
# ----------------------------------------------------------------

def check_person_similarity(known_img_path, unknown_img_path, tolerance=0.6):
    """
    Loads two images, extracts face features, and checks if the person is the same.
    """
    print(f"1. Loading and encoding known image: {os.path.basename(known_img_path)}")
    try:
        # Load the known image
        known_image = face_recognition.load_image_file(known_img_path)
    except FileNotFoundError:
        return f"Error: Known image not found at {known_img_path}"

    # Extract features (face encoding)
    known_encodings = face_recognition.face_encodings(known_image)

    if not known_encodings:
        return "⚠️ Error: No face found in the known image."

    # Use the first face found as the known person's features
    known_face_encoding = known_encodings[0]

    print(f"2. Loading and checking unknown image: {os.path.basename(unknown_img_path)}")
    try:
        # Load the image to be checked
        unknown_image = face_recognition.load_image_file(unknown_img_path)
    except FileNotFoundError:
        return f"Error: Unknown image not found at {unknown_img_path}"

    # Extract features from the image to be checked
    unknown_encodings = face_recognition.face_encodings(unknown_image)

    if not unknown_encodings:
        return "⚠️ Error: No face found in the image to be checked."

    # Compare the features of the known person against ALL faces in the unknown image
    for unknown_encoding in unknown_encodings:
        
        # 'compare_faces' returns True if the face distance is within the tolerance
        results = face_recognition.compare_faces(
            [known_face_encoding], # List of known encodings
            unknown_encoding,      # The unknown encoding to check
            tolerance=tolerance
        )

        if results[0]: # If the first (and only) result is True
            return "\n✅ **PERSON FOUND!** The person in the second image is the same."

    # If the loop completes without finding a match
    return "\n❌ **PERSON NOT FOUND.** The person in the second image is different."


# --- Execution ---
if __name__ == "__main__":
    result = check_person_similarity(KNOWN_IMAGE_PATH, UNKNOWN_IMAGE_PATH)
    print("\n--- Comparison Result ---")
    print(result)