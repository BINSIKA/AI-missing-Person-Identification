import cv2
import os
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

dataset_dir = r"Face Recognition System\images"
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)


person_name = input("Enter name of the person (or press Enter to skip): ").strip()

if person_name != "":
    person_folder = os.path.join(dataset_dir, person_name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)

    cap = cv2.VideoCapture(0)
    count = 0
    print("Position your face in front of the camera.")
    print("Press any key to start capturing images...")

    # Preview before starting
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.05, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)

        cv2.imshow("Preview - Press Any Key to Start", frame)
        if cv2.waitKey(1) != -1:
            break

    print("Starting image capture...")

    # Capture 100 images
    while count < 20:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.05, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)
            face_img = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            cv2.imwrite(os.path.join(person_folder, f"{count+1}.jpg"), face_img)
            count += 1
            print(f"Captured image {count}/100")

        cv2.imshow("Capturing Images", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Training images captured.")


train_images = []
train_labels = []
label_map = {}  # label -> person name
current_label = 0

for person_name in os.listdir(dataset_dir):
    person_folder = os.path.join(dataset_dir, person_name)
    if not os.path.isdir(person_folder):
        continue

    for img_file in os.listdir(person_folder):
        img_path = os.path.join(person_folder, img_file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            train_images.append(img)
            train_labels.append(current_label)


    label_map[current_label] = person_name
    current_label += 1

if len(train_images) == 0:
    print("No training images found. Exiting...")
    exit()

train_labels = np.array(train_labels, dtype=np.int32)


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(train_images, train_labels)
print("✅ Recognizer trained with all persons.")


cap = cv2.VideoCapture(0)
print("Starting recognition. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.05, 4)

    for (x, y, w, h) in faces:
        face_img = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        label, confidence = recognizer.predict(face_img)
        name = label_map[label] if confidence < 100 else "Unknown"

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()