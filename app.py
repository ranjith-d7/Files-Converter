from flask import Flask, request, send_file, jsonify, render_template
from pdf2docx import Converter
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'temp_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to display the HTML frontend
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle the file conversion
@app.route('/convert', methods=['POST'])
def convert_pdf_to_word():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['pdf_file']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Please select a valid PDF file"}), 400

    unique_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.pdf")
    docx_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.docx")

    file.save(pdf_path)

    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return send_file(docx_path, as_attachment=True, download_name="converted_document.docx")
        
    except Exception as e:
        return jsonify({"error": "Conversion failed. The PDF might be corrupted or protected."}), 500
        
    finally:
        if os.path.exists(pdf_path): 
            os.remove(pdf_path)

if __name__ == '__main__':
    app.run(debug=True)