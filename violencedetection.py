import cv2
import torch
import numpy as np
import tensorflow as tf

# Load your pre-trained violence detection model
violence_model = tf.keras.models.load_model('VModel/modelnew.h5')

# Load YOLOv5 model
yolov5_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def detect_and_box_violence_camera():
    cap = cv2.VideoCapture(0)  # Use the default camera (you can specify a different camera index if needed)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame to 640 x 480
        resized_frame = cv2.resize(frame, (640, 480))

        results = yolov5_model(resized_frame)

        detected_classes = results.pred[0][:, -1].cpu().numpy()
        detected_boxes = results.pred[0][:, :4].cpu().numpy()

        for class_id, box in zip(detected_classes, detected_boxes):
            x, y, x_max, y_max = box
            w = x_max - x
            h = y_max - y

            detected_img = resized_frame[int(y):int(y_max), int(x):int(x_max)]
            
            # Resize the detected image to match the expected input shape of the violence model
            resized_img = cv2.resize(detected_img, (128, 128))

            # Use the violence detection model to predict violence
            violence_probability = violence_model.predict(np.expand_dims(resized_img, axis=0))[0]

            if class_id == 0:  # Assuming class 0 corresponds to "person"
                if violence_probability > 0.5:  # Adjust this threshold as needed
                    color = (0, 0, 255)  # Red color for violent people
                else:
                    color = (0, 255, 0)  # Green color for non-violent people

                cv2.rectangle(resized_frame, (int(x), int(y)), (int(x_max), int(y_max)), color, 2)

        cv2.imshow('Violence Detection with YOLOv5 - Camera Feed', resized_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit the loop
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the camera feed violence detection
detect_and_box_violence_camera()

