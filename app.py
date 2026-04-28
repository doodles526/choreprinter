from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image
import requests
import io
import printer
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

def process_and_print(img_data, filename="image"):
    """Helper to resize and print a PIL Image or raw bytes."""
    try:
        if isinstance(img_data, bytes):
            img = Image.open(io.BytesIO(img_data))
        else:
            img = img_data
            
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
        print(f"Printing: {filename} ({target_width}x{target_height})")
        printer.print_image(resized_img)
        return True, "Success: Image sent to printer!"
    except Exception as e:
        print(f"Processing Error: {e}")
        return False, str(e)

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
        success, msg = process_and_print(Image.open(file.stream), file.filename)
        return redirect(url_for('index', message=msg))

@app.route('/print-url', methods=['POST'])
def print_url():
    url = request.form.get('url')
    if not url:
        return redirect(url_for('index', message="Error: No URL provided"))
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        success, msg = process_and_print(response.content, url.split('/')[-1])
        return redirect(url_for('index', message=msg))
    except Exception as e:
        return redirect(url_for('index', message=f"Error downloading image: {str(e)}"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
