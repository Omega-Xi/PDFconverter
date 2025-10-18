from flask import Flask,send_file,request,render_template
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
app.secret_key = os.getenv("SECRET_KEY")

#setting route
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        pdfFile=request.files['pdf']
        textFile=pdf_to_txt(pdfFile)
        return send_file(textFile,as_attachment=True,download_name="converted.txt", mimetype='text/plain')
    return render_template("index.html")
    
if __name__=="__main__":
    app.run(debug=False)