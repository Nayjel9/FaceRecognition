import torch
import cv2
import numpy as np
from flask import Flask, render_template, Response

# Load the YOLOv5 model
path = 'model/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path, force_reload=True)

app = Flask(__name__)

# Load custom class labels (replace with your own labels)
class_labels = ['Gun', 'Knife']

def detect_objects():
    cap = cv2.VideoCapture('0')
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))

        # Perform inference on the frame
        results = model(frame)

        # Get the predicted class labels, bounding boxes, and confidence scores
        pred_class_labels = results.names
        pred_boxes = results.pred[0][:, :4].cpu().numpy()
        pred_scores = results.pred[0][:, 4].cpu().numpy()
        pred_classes = results.pred[0][:, 5].cpu().numpy().astype(int)

        # Filter detections based on confidence threshold
        conf_threshold = 0.5
        detections = [(box, class_labels[class_idx], score)
                      for box, class_idx, score in zip(pred_boxes, pred_classes, pred_scores)
                      if score > conf_threshold]

        # Draw bounding boxes and labels on the frame
        for box, class_label, score in detections:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_label}: {score:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(detect_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
