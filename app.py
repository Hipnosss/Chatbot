from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

contenido_sitio = """
First Hill es una tienda colombiana especializada en calzado industrial y de senderismo.
Ofrecemos botas para hombre y mujer en categorías Industrial, Outdoor y Tactical.

Productos destacados y precios:
- Botas Alabama ProTrek Outdoor para Hombre (Café) - $288.000 COP (antes $320.000)
- Botas Arizona WildStride Outdoor para Hombre (Negro Goma) - $320.000 COP
- Botas Charlotte PowerTech Outdoor para Mujer (Negro) - $270.000 COP
- Botas Dakota Elite Outdoor para Hombre (Verde) - $320.000 COP
- Botas Denver PowerStep Industrial para Mujer (Miel) - $360.000 COP
- Botas Denver PowerStep Industrial para Mujer (Negro Gris) - $360.000 COP
- Botas Denver TitanStep Industrial para Hombre (Café) - $360.000 COP
- Botas Nevada TrailMaster Outdoor para Hombre (Verde) - $320.000 COP
- Botas Cincinnati IronForce Industrial para Hombre (Negro Amarillo) - $360.000 COP
- Botas Cincinnati IronForce Industrial para Hombre (Café) - $360.000 COP
- Botas Cincinnati IronForce Industrial para Hombre (Miel) - $360.000 COP

Calidad garantizada: Todos los productos pasan por inspección antes de despacho.
Ofrecemos cotizaciones por mayor (+60 pares).
Cobertura nacional con envío gratis a toda Colombia.
Pago seguro con pasarela que cumple todos los requisitos de seguridad.

Envíos:
- Tiempo de entrega: 2 a 5 días hábiles según ubicación.
- Envío gratis en toda Colombia.

Políticas:
- Cambios y devoluciones: Hasta 15 días después de la compra.
- Métodos de pago: Tarjeta de crédito/débito, PSE, Nequi, Daviplata.

Contacto:
- Dirección: Cl 69 Sur #18h-51, Bogotá, Colombia
- Teléfono: (+57) 3144403880
- Email: contacto@firsthill.com.co
- Redes sociales: Instagram, Facebook, WhatsApp @FIRSTHILLCOLOMBIA

Guía de tallas disponible en la sección "Tabla de Tallas" en la web.

Avisos legales:
- Políticas de privacidad, términos y condiciones y política de cambios están disponibles en el sitio web.

Derechos reservados © 2025 FIRST HILL S.A.S
"""

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip().lower()
    if not question:
        return jsonify({"answer": "Por favor, ingresa una pregunta válida."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en calzado industrial y de senderismo."},
                {"role": "system", "content": f"Esta es la información sobre First Hill:\n{contenido_sitio}"},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error al procesar la pregunta: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
