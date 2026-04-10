from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import io
import printer
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

@app.route('/')
def index():
    message = request.args.get('message')
    return render_template('index.html', message=message)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index', message="Error: No file part"))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index', message="Error: No selected file"))

    if file:
        try:
            # Load the image from the uploaded file
            img = Image.open(file.stream)
            
            # Convert to RGB if it's not (e.g., PNG with alpha or RGBA)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Calculate new height while maintaining aspect ratio (target width: 512)
            target_width = 512
            width_percent = (target_width / float(img.size[0]))
            target_height = int((float(img.size[1]) * float(width_percent)))
            
            # Resize the image
            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Print the image using the printer module
            print(f"Printing image: {file.filename} ({target_width}x{target_height})")
            printer.print_image(resized_img)
            
            return redirect(url_for('index', message="Success: Image sent to printer!"))
            
        except Exception as e:
            print(f"Printing Error: {e}")
            return redirect(url_for('index', message=f"Error: {str(e)}"))

if __name__ == '__main__':
    # Running on 0.0.0.0 so it's accessible from the network
    app.run(host='0.0.0.0', port=5000, debug=True)
