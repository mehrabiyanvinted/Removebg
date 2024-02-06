import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file, render_template
import io
import os

app = Flask(__name__)

# Ensure a "uploads" folder exists for uploaded images
if not os.path.exists("uploads"):
    os.makedirs("uploads")


# Function to remove background using GrabCut algorithm and output PNG
def remove_background(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Create a mask with the same size as the image
    mask = np.zeros(image.shape[:2], np.uint8)

    # Define a rectangle around the object to help GrabCut
    rect = (10, 10, image.shape[1] - 10, image.shape[0] - 10)

    # Initialize the background and foreground models for GrabCut
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # Apply GrabCut algorithm
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # Create a mask where all probable background pixels are marked
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # Create an RGBA image (4 channels) with a transparent background
    h, w, _ = image.shape
    rgba_image = np.zeros((h, w, 4), dtype=np.uint8)

    # Copy the object from the original image to the RGBA image
    for c in range(3):
        rgba_image[:, :, c] = np.where(mask2[:, :] == 1, image[:, :, c], 0)

    # Set the alpha channel to 255 (fully opaque) for the object pixels
    rgba_image[:, :, 3] = np.where(mask2[:, :] == 1, 255, 0)

    # Convert the image to PNG format
    png_image = cv2.imencode('.png', rgba_image)[1].tobytes()

    return png_image


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_image():
    if 'image' in request.files:
        image = request.files['image']
        image_path = os.path.join("uploads", "temp_image.jpg")
        image.save(image_path)

        processed_image = remove_background(image_path)

        # Return the processed image as a PNG with transparent background
        return send_file(
            io.BytesIO(processed_image),
            mimetype='image/png',
            as_attachment=True,
            download_name='processed_image.png'
        )

    return jsonify({'result': 'error', 'message': 'No image uploaded'})


if __name__ == '__main__':
    app.run(debug=True)
