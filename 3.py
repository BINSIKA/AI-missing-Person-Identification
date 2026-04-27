from ultralytics import YOLO
import cv2

def detect_and_track(video_path):
    model = YOLO("yolov5s.pt")  # Pre-trained YOLOv5 model
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated_frame = results[0].plot()

        cv2.imshow("YOLOv5 Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Example:
# detect_and_track("test_video.mp4")
