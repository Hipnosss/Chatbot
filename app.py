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

# Preguntas frecuentes definidas para respuestas rápidas
faq = {
    "¿cómo sé mi talla de calzado?": "Puedes consultar nuestra guía de tallas en la sección de ayuda en la web.",
    "¿qué tipos de bota son resistentes al agua?": "Las botas de la línea Outdoor Pro cuentan con resistencia al agua certificada.",
    "¿qué significa que una bota tenga puntera de acero?": "La puntera de acero protege los dedos contra impactos y compresiones, ideal para entornos industriales.",
    "¿cuánto tardan los envíos?": "Los envíos nacionales tardan entre 2 y 5 días hábiles dependiendo de tu ubicación.",
    "¿puedo cambiar un producto si no me sirve?": "Sí, tienes hasta 15 días para cambios. Consulta nuestra política de devoluciones.",
    "¿qué métodos de pago aceptan?": "Aceptamos tarjeta de crédito, débito, PSE, Nequi y Daviplata.",
    "¿cómo contacto con atención al cliente?": "Puedes escribirnos al WhatsApp +57 3144403880 o al correo contacto@firsthill.com.co"
}

temas_permitidos = [
    "bota", "zapato", "calzado", "pago", "talla", "envío", "envios",
    "pedido", "devolución", "devoluciones", "guía", "seguridad", "trabajo", "senderismo",
    "política", "políticas", "contacto", "precio", "precios", "cotización", "envío gratis"
]

# Memoria temporal para usuarios (ejemplo simple)
memoria_usuario = {}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")  # Para identificar sesión/usuario
    question = data.get("question", "").lower().strip()
    if not question:
        return jsonify({"answer": "Por favor, ingresa una pregunta válida."}), 400

    # Respuesta rápida de FAQ si coincide con alguna pregunta frecuente exacta
    for pregunta_frecuente, respuesta_frecuente in faq.items():
        if pregunta_frecuente in question:
            return jsonify({"answer": respuesta_frecuente})

    # Guardar talla si el usuario la menciona
    if "mi talla es" in question:
        talla = ''.join(filter(str.isdigit, question))
        if talla:
            memoria_usuario[user_id] = {"talla": talla}
            return jsonify({"answer": f"¡Perfecto! Recordaré que tu talla es {talla}."})
        else:
            return jsonify({"answer": "No entendí tu talla, por favor indícala con números."})

    # Consultar talla guardada
    if "¿cuál es mi talla" in question or "cual es mi talla" in question:
        if user_id in memoria_usuario and "talla" in memoria_usuario[user_id]:
            return jsonify({"answer": f"Tu talla es {memoria_usuario[user_id]['talla']}."})
        else:
            return jsonify({"answer": "Aún no me has dicho tu talla."})

    # Validar que la pregunta contenga alguna palabra permitida
    if not any(palabra in question for palabra in temas_permitidos):
        return jsonify({"answer": "Solo puedo ayudarte con temas relacionados al calzado y nuestra tienda. ¿Tienes una consulta sobre productos, tallas o envíos?"})

    try:
        prompt = (
            "Eres un asistente experto en calzado industrial y de senderismo. "
            "Usa la siguiente información para responder las preguntas:\n\n"
            f"{contenido_sitio}\n\n"
            "Responde solo sobre temas relacionados a esta información, "
            "si la pregunta no corresponde, indica que solo puedes ayudar sobre esos temas.\n\n"
            f"Pregunta: {question}\nRespuesta:"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=400,
            temperature=0.6,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        answer = response.choices[0].text.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"Error al procesar la pregunta: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

