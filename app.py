from flask import Flask, send_file, request, render_template, jsonify
from flask_cors import CORS
from converter.pdftotxt import pdf_to_txt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Use variables
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Instantiate Flask application
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-for-render")

# Add error handling for file size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Main route - serve the HTML page
@app.route('/')
def index():
    return render_template("index.html")

# Conversion endpoint
@app.route('/convert', methods=['POST'])
def convert_pdf():
    try:
        # Check if file is present
        if 'pdf' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        pdf_file = request.files['pdf']
        
        # Check if file is selected
        if pdf_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file is PDF
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400
        
        # Convert PDF to text
        text_file = pdf_to_txt(pdf_file)
        
        return send_file(
            text_file,
            as_attachment=True,
            download_name=pdf_file.filename.replace('.pdf', '.txt'),
            mimetype='text/plain'
        )
        
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)