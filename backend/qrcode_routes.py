# backend/qrcode_routes.py

import io
import qrcode
from flask import request, send_file, jsonify, Blueprint
from flask_cors import cross_origin

qr = Blueprint('qr', __name__)

@qr.route('/generate_qrcode', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
def generate_qrcode():
    try:
        data = request.get_json()
        text = data.get('data')

        if not text:
            return jsonify({'message': 'Dados não fornecidos'}), 400

        # Gera QR Code em memória
        img = qrcode.make(text)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({'message': f'Erro ao gerar QR Code: {str(e)}'}), 500
