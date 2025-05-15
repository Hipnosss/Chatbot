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
Cotizaciones por mayor (+60 pares).
Cobertura nacional con envío gratis a toda Colombia.
Pago seguro con pasarela que cumple todos los requisitos de seguridad.

Envíos:
- Tiempo de entrega: 2 a 5 días hábiles.
- Envío gratis en toda Colombia.

Cambios y devoluciones: Hasta 15 días después de la compra.
Métodos de pago: Tarjeta, PSE, Nequi, Daviplata.

Contacto:
- Dirección: Cl 69 Sur #18h-51, Bogotá
- Tel: (+57) 3144403880
- Email: contacto@firsthill.com.co
- Redes sociales: Instagram, Facebook y WhatsApp: @FIRSTHILLCOLOMBIA

Guía de tallas en la web. Políticas de privacidad, cambios y condiciones también están disponibles en línea.

© 2025 FIRST HILL S.A.S. Todos los derechos reservados.
"""

faq = {
    "¿cómo sé mi talla de calzado?": "Puedes consultar nuestra guía de tallas en la sección de ayuda en la web.",
    "¿qué tipos de bota son resistentes al agua?": "Las botas de la línea Outdoor Pro cuentan con resistencia al agua.",
    "¿qué significa que una bota tenga puntera de acero?": "Protección para los dedos contra impactos, ideal en ambientes industriales.",
    "¿cuánto tardan los envíos?": "Entre 2 y 5 días hábiles según la ciudad.",
    "¿puedo cambiar un producto si no me sirve?": "Sí, tienes hasta 15 días para cambios.",
    "¿qué métodos de pago aceptan?": "Tarjeta, PSE, Nequi y Daviplata.",
    "¿cómo contacto con atención al cliente?": "WhatsApp +57 3144403880 o contacto@firsthill.com.co"
}

temas_permitidos = [
    "bota", "zapato", "calzado", "pago", "talla", "envío", "envios",
    "pedido", "devolución", "devoluciones", "guía", "seguridad", "trabajo", "senderismo",
    "política", "políticas", "contacto", "precio", "precios", "cotización", "envío gratis"
]

# Memoria temporal por usuario
memoria_usuario = {}

# Palabras para detectar saludo y mostrar menú
saludos = ["hola", "buenos días", "buen día", "buenas tardes", "buenas noches", "buenas"]

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    question = data.get("question", "").lower().strip()
    if not question:
        return jsonify({"answer": "Por favor, ingresa una pregunta válida."})

    # Mostrar menú si es saludo
    if any(saludo in question for saludo in saludos):
        menu = (
            "👋 ¡Hola! Soy tu asistente de First Hill. ¿En qué puedo ayudarte?\n\n"
            "1. Ver tipos de calzado\n"
            "2. Guía de tallas\n"
            "3. Métodos de pago\n"
            "4. Contacto o devoluciones\n"
            "5. Pregunta abierta\n"
            "(Escribe solo el número de opción o tu pregunta)"
        )
        return jsonify({"answer": menu})

    # Manejo de opciones numéricas del menú
    if question in ["1", "2", "3", "4", "5"]:
        if question == "1":
            return jsonify({"answer": "En First Hill tenemos botas y zapatos para industria, construcción, senderismo y más."})
        elif question == "2":
            return jsonify({"answer": "Consulta nuestra guía de tallas en la web o dime tu talla y te ayudo a elegir."})
        elif question == "3":
            return jsonify({"answer": "Aceptamos pagos con tarjeta, PSE, Nequi y Daviplata."})
        elif question == "4":
            return jsonify({"answer": "Puedes contactarnos por WhatsApp +57 3144403880 o por correo contacto@firsthill.com.co. También gestionamos devoluciones en 15 días."})
        elif question == "5":
            return jsonify({"answer": "Perfecto, hazme cualquier pregunta sobre nuestros productos o servicios."})

    # Preguntas frecuentes con búsqueda básica
    for faq_q, faq_r in faq.items():
        if faq_q in question or question in faq_q:
            return jsonify({"answer": faq_r})

    # Guardar talla si la indican
    if "mi talla es" in question:
        talla = ''.join(filter(str.isdigit, question))
        if talla:
            memoria_usuario[user_id] = {"talla": talla}
            return jsonify({"answer": f"¡Perfecto! Recordaré que tu talla es {talla}."})
        else:
            return jsonify({"answer": "No entendí tu talla. Por favor indícala con números."})

    # Consultar talla guardada
    if "¿cuál es mi talla" in question or "cual es mi talla" in question:
        if user_id in memoria_usuario and "talla" in memoria_usuario[user_id]:
            return jsonify({"answer": f"Tu talla es {memoria_usuario[user_id]['talla']}."})
        else:
            return jsonify({"answer": "Aún no me has dicho tu talla."})

    # Temas permitidos para filtrar preguntas irrelevantes
    if not any(palabra in question for palabra in temas_permitidos):
        return jsonify({"answer": "Solo puedo ayudarte con temas relacionados al calzado y nuestra tienda. ¿Tienes una consulta sobre productos, tallas o envíos?"})

    # Crear prompt para OpenAI
    prompt = f"{contenido_sitio}\n\nPregunta: {question}"

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en calzado industrial y outdoor. Responde solo con la información de la tienda."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )
        answer = completion.choices[0].message.content.strip()

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"Error al procesar la pregunta: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
