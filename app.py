from flask import Flask, jsonify, request
import qrcode
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Función para enviar un mensaje de WhatsApp con la imagen del código QR
def send_whatsapp_message(phone_number, qr_image_path):
    try:
        # Configurar el driver de Selenium (usando Chrome)
        options = webdriver.ChromeOptions()
        options.add_argument('--user-data-dir=/path/to/your/custom/profile')  # Usar un perfil de usuario persistente para WhatsApp Web
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://web.whatsapp.com')

        # Esperar a que se cargue la página
        input("Escanea el código QR en WhatsApp Web y presiona Enter para continuar...")

        # Buscar el contacto de WhatsApp y enviar el mensaje
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_box.click()
        search_box.send_keys(phone_number)
        search_box.send_keys(Keys.RETURN)

        message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]')
        message_box.send_keys("Tu código QR para el pedido ha sido generado. Aquí está el código QR.")
        message_box.send_keys(Keys.RETURN)

        # Adjuntar la imagen del QR
        attach_button = driver.find_element(By.XPATH, '//span[@data-icon="clip"]')
        attach_button.click()

        image_input = driver.find_element(By.XPATH, '//input[@accept="image/*"]')
        image_input.send_keys(qr_image_path)

        # Enviar el mensaje con el archivo adjunto
        send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        send_button.click()

        print(f"Mensaje enviado a {phone_number} con el código QR.")
        driver.quit()
    except Exception as e:
        print(f"Error al enviar el mensaje de WhatsApp: {e}")

@app.route('/')
def index():
    return "Servidor Flask en funcionamiento"

@app.route('/generar_qr', methods=['POST'])
def generar_qr():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Verificar que los datos necesarios estén presentes
        if 'pedido_id' not in data or 'expiracion' not in data or 'telefono' not in data:
            return jsonify({'error': 'Faltan parámetros en la solicitud'}), 400

        pedido_id = data['pedido_id']
        expiracion = data['expiracion']
        telefono_cliente = data['telefono']  # Teléfono del cliente para WhatsApp

        # Crear el contenido del QR
        qr_content = f"{pedido_id},{expiracion}"

        # Generar el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        # Crear la imagen del QR
        img = qr.make_image(fill='black', back_color='white')

        # Crear un nombre único para el archivo QR
        qr_filename = f"{pedido_id}.png"

        # Guardar el archivo en la carpeta 'static'
        img_path = os.path.join('static', qr_filename)
        img.save(img_path)

        # Calcular la fecha de expiración en formato UNIX (timestamp)
        expiration_time = time.time() + expiracion

        # Enviar el código QR por WhatsApp
        send_whatsapp_message(telefono_cliente, img_path)

        # Devolver la respuesta con el enlace al QR y la expiración
        return jsonify({
            'pedido_id': pedido_id,
            'expiracion': expiration_time,
            'qr_url': img_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
