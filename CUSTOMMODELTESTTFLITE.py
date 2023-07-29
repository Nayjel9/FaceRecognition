import numpy as np
import cv2
import tensorflow as tf

# Load the TensorFlow Lite model
model_path = 'model/best-int8.tflite'
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']

# Load labels for object classes
labels_path = 'model/labels.txt'
with open(labels_path, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Function to preprocess image and run inference
def detect_objects(image):
    # Preprocess the image
    input_data = cv2.resize(image, (input_shape[1], input_shape[2]))
    input_data = np.expand_dims(input_data, axis=0)
    input_data = (input_data.astype(np.float32) - 127.5) / 127.5

    # Set the input tensor
    interpreter.set_tensor(input_details[0]['index'], input_data)

    # Run inference
    interpreter.invoke()

    # Get the output tensor
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # Post-process the output to get the detected objects and their confidence scores
    detections = output_data[0]
    num_detections = int(detections[0])

    results = []
    for i in range(num_detections):
        class_id = int(detections[i + 1])
        score = detections[i + 1]
        bbox = detections[i + 2 : i + 6]
        results.append((labels[class_id], score, bbox))

    return results

# Load and process an example image
image_path = 'path/to/your/image.jpg'
image = cv2.imread(image_path)
results = detect_objects(image)

# Display the results
for label, score, bbox in results:
    if score > 0.5:  # Adjust this threshold to control the detection sensitivity
        x, y, w, h = [int(i) for i in bbox * [image.shape[1], image.shape[0], image.shape[1], image.shape[0]]]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, f"{label}: {score:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow("Object Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
