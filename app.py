from flask import Flask, jsonify, request, send_file
import qrcode
import os
import time
from flask_cors import CORS
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

        # Guardar la imagen QR en un objeto BytesIO para enviarla directamente
        img_io = BytesIO()
        qr.save(img_io)
        img_io.seek(0)

        # Simular envío de mensaje
        print(f"Simulando envío de WhatsApp a {telefono} con QR")

        # Enviar la imagen del QR directamente como un archivo
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f"{pedido_id}.png")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
