from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pdf2docx import Converter
import os
import tempfile
from pdf2image import convert_from_path
from zipfile import ZipFile, ZIP_DEFLATED
import io

application = Flask(__name__)
CORS(application)

@application.route('/hello', methods=['GET'])
def hello():
    return 'Hello, world!'

@application.route('/convert', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        print("No file in request")
        return jsonify({'error': 'No file provided'}), 400

    pdf_file = request.files['file']

    if pdf_file.filename == '':
        print("Empty filename")
        return jsonify({'error': 'Empty filename'}), 400

    if not pdf_file.filename.lower().endswith('.pdf'):
        print("Not a PDF file")
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            pdf_path = os.path.join(tmpdirname, pdf_file.filename)
            docx_path = os.path.join(tmpdirname, pdf_file.filename.rsplit('.', 1)[0] + '.docx')
            pdf_file.save(pdf_path)
            print(f"Saved PDF to: {pdf_path}")

            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            print(f"Converted to DOCX: {docx_path}")

            return send_file(
                docx_path,
                as_attachment=True,
                download_name=os.path.basename(docx_path),
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
    except Exception as e:
        print("Exception occurred:", e)
        return jsonify({'error': str(e)}), 500

@application.route('/convert_pdf_to_image', methods=['POST'])
def convert_pdf_to_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    pdf_file = request.files['file']
    if pdf_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # Get format from form data, default to png
    img_format = request.form.get('format')
    if not img_format:
        img_format = 'png'
    else:
        img_format = str(img_format).lower()
    if img_format not in ['png', 'jpeg']:
        return jsonify({'error': 'Invalid format. Use "png" or "jpeg".'}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            pdf_path = os.path.join(tmpdirname, pdf_file.filename)
            pdf_file.save(pdf_path)

            # Convert PDF to images
            print(f"Converting PDF to {img_format} images...")
            images = convert_from_path(pdf_path, dpi=200)  # Lower DPI for smaller files
            print(f"Converted {len(images)} pages")
            
            # Return first page as single image
            if len(images) == 0:
                return jsonify({'error': 'No pages found in PDF'}), 400
                
            # Save to temporary file first
            ext = 'jpg' if img_format == 'jpeg' else 'png'
            img_path = os.path.join(tmpdirname, f'output.{ext}')
            images[0].save(img_path, format=img_format.upper(), quality=85 if img_format == 'jpeg' else None)
            
            mimetype = 'image/jpeg' if img_format == 'jpeg' else 'image/png'
            
            return send_file(
                img_path,
                as_attachment=True,
                download_name=pdf_file.filename.rsplit('.', 1)[0] + f'.{ext}',
                mimetype=mimetype
            )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# <-- Make sure this is ABOVE __main__:
app = application

if __name__ == '__main__':
    application.run(debug=True)
