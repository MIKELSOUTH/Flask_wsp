from flask import Flask, jsonify, request, send_file
import qrcode
import os
import time
from flask_cors import CORS
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Servidor Flask en funcionamiento"

@app.route('/generar_qr', methods=['POST'])
def generar_qr():
    try:
        data = request.get_json()

        if 'pedido_id' not in data or 'expiracion' not in data or 'telefono' not in data:
            return jsonify({'error': 'Faltan parámetros en la solicitud'}), 400

        pedido_id = data['pedido_id']
        expiracion = data['expiracion']
        telefono = data['telefono']

        # Generar QR
        qr_content = f"{pedido_id},{expiracion}"
        qr = qrcode.make(qr_content)
        buffer = BytesIO()
        qr.save(buffer)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        # Simular envío de mensaje
        print(f"Simulando envío de WhatsApp a {telefono} con QR")

        return jsonify({
            'pedido_id': pedido_id,
            'expiracion': time.time() + expiracion,
            'qr_base64': img_base64
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
