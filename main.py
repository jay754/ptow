from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pdf2docx import Converter
import os
import tempfile

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

# <-- Make sure this is ABOVE __main__:
app = application

if __name__ == '__main__':
    application.run(debug=True)
