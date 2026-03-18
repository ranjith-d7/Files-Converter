from flask import Flask, request, send_file, jsonify, render_template
from pdf2docx import Converter
import os
import uuid
import io  # <-- NEW: Imports the input/output library for memory buffering

app = Flask(__name__)

UPLOAD_FOLDER = 'temp_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

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
        # 1. Convert the file and save it to the hard drive
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()

        # 2. Open the new Word doc and copy its contents into RAM
        memory_file = io.BytesIO()
        with open(docx_path, 'rb') as f:
            memory_file.write(f.read())
        
        # 3. Reset the memory pointer to the start of the file
        memory_file.seek(0)

        # 4. Delete the physical Word file from the hard drive
        os.remove(docx_path)

        # 5. Send the file from RAM to the user
        return send_file(memory_file, as_attachment=True, download_name="converted_document.docx")
        
    except Exception as e:
        return jsonify({"error": "Conversion failed. The PDF might be corrupted."}), 500
        
    finally:
        # 6. Delete the original PDF file
        if os.path.exists(pdf_path): 
            os.remove(pdf_path)
            
        # Failsafe: In case the code crashed before Step 4, clean up the docx too
        if os.path.exists(docx_path):
            os.remove(docx_path)

if __name__ == '__main__':
    app.run(debug=True)