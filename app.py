from flask import Flask,send_file,request,render_template,jsonify
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


#instantiate Flask application
app=Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")

#setting route
@app.route('/convert',methods=['GET','POST'])
def index():
    if request.method=='POST':
        pdfFile=request.files['pdf']
        textFile=pdf_to_txt(pdfFile)
        return send_file(textFile,as_attachment=True,download_name="converted.txt", mimetype='text/plain')
    return render_template("index.html")
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__=="__main__":
    app.run(debug=False)