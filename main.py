from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import io
import base64
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

app = Flask(__name__)

# Load and prepare the model
iris = load_iris()
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    image = Image.open(image_file).convert('RGB')
    
    # Preprocess the image
    image = np.array(image.resize((4, 4)))  # Resize image for simplicity
    image = image.flatten()  # Flatten to 1D array
    
    # Dummy feature scaling for demonstration (actual model should be trained with real image data)
    image = np.expand_dims(image, axis=0)
    image = scaler.transform(image)
    
    # Predict using the trained model
    prediction = model.predict(image)
    class_name = iris.target_names[prediction[0]]
    
    return jsonify({'prediction': class_name})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'Running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
