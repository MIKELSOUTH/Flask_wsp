from flask import Flask, jsonify, request
import qrcode
import os
import time
import smtplib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS

# Configuración del navegador (Headless para Render)
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

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
        qr_filename = f"{pedido_id}.png"
        img_path = os.path.join('static', qr_filename)
        qr.save(img_path)

        # Simular envío de mensaje por WhatsApp Web
        enviar_whatsapp(telefono, img_path)

        return jsonify({
            'pedido_id': pedido_id,
            'expiracion': time.time() + expiracion,
            'qr_url': img_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def enviar_whatsapp(telefono, qr_path):
    try:
        whatsapp_url = f"https://web.whatsapp.com/send?phone={telefono}&text=Tu código QR está listo."
        driver.get(whatsapp_url)
        time.sleep(5)  # Esperar carga

        # Aquí deberías agregar automatización para enviar la imagen con Selenium
        print(f"Mensaje enviado a {telefono} con QR: {qr_path}")

    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
