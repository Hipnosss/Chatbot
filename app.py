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

Envíos:
- Tiempo de entrega: 2 a 5 días hábiles.
- Envío gratis en toda Colombia.

Cambios y devoluciones: Hasta 15 días después de la compra.
Métodos de pago: Tarjeta, PSE, Nequi, Daviplata.
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

imagenes_productos = {
    "alabama": "https://firsthill.com.co/wp-content/uploads/2024/04/Alabama-ProTrek.jpg",
    "arizona": "https://firsthill.com.co/wp-content/uploads/2024/04/Arizona-WildStride.jpg",
    "charlotte": "https://firsthill.com.co/wp-content/uploads/2024/04/Charlotte-PowerTech.jpg",
    "dakota": "https://firsthill.com.co/wp-content/uploads/2024/04/Dakota-Elite.jpg",
    "denver": "https://firsthill.com.co/wp-content/uploads/2024/04/Denver-TitanStep.jpg",
    "nevada": "https://firsthill.com.co/wp-content/uploads/2024/04/Nevada-TrailMaster.jpg",
    "cincinnati": "https://firsthill.com.co/wp-content/uploads/2024/09/1725576881351.webp"
}

temas_permitidos = [
    "bota", "zapato", "calzado", "pago", "talla", "envío", "envios",
    "pedido", "devolución", "devoluciones", "guía", "seguridad", "trabajo", "senderismo",
    "política", "políticas", "contacto", "precio", "precios", "cotización", "envío gratis"
]

memoria_usuario = {}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    question = data.get("question", "").lower().strip()

    if not question:
        return jsonify({"answer": "Por favor, ingresa una pregunta válida."}), 400

    # Menú por número
    if question in ["1", "2", "3", "4"]:
        opciones = {
            "1": "Ofrecemos botas industriales, outdoor y tácticas. ¿Te interesa algún modelo en particular?",
            "2": "Los envíos tardan entre 2 y 5 días hábiles. ¡Y son gratis en toda Colombia!",
            "3": "Aceptamos pagos por tarjeta, PSE, Nequi y Daviplata. ¿Cuál prefieres?",
            "4": "Puedes escribirnos al WhatsApp +57 3144403880 o al correo contacto@firsthill.com.co"
        }
        return jsonify({"answer": opciones[question]})

    # FAQ directa
    for faq_q, faq_r in faq.items():
        if faq_q in question:
            return jsonify({"answer": faq_r})

    # Guardar talla
    if "mi talla es" in question:
        talla = ''.join(filter(str.isdigit, question))
        if talla:
            memoria_usuario[user_id] = {"talla": talla}
            return jsonify({"answer": f"¡Perfecto! Recordaré que tu talla es {talla}."})
        else:
            return jsonify({"answer": "No entendí tu talla. Por favor indícala con números."})

    # Recordar talla
    if "¿cuál es mi talla" in question or "cual es mi talla" in question:
        if user_id in memoria_usuario and "talla" in memoria_usuario[user_id]:
            return jsonify({"answer": f"Tu talla es {memoria_usuario[user_id]['talla']}."})
        else:
            return jsonify({"answer": "Aún no me has dicho tu talla."})

    # Imagen del producto
    for nombre, url in imagenes_productos.items():
        if nombre in question:
            return jsonify({
                "answer": f"Aquí tienes la imagen del modelo {nombre.capitalize()}:",
                "image_url": url
            })

    # Restringir temas
    if not any(palabra in question for palabra in temas_permitidos):
        return jsonify({"answer": "Solo puedo ayudarte con temas relacionados al calzado y nuestra tienda. ¿Tienes una consulta sobre productos, tallas o envíos?"})

    # OpenAI Chat
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en calzado industrial y outdoor. Responde solo con la información de la tienda."},
                {"role": "user", "content": f"{contenido_sitio}\n\nPregunta: {question}"}
            ],
            temperature=0.5,
            max_tokens=400
        )
        answer = completion.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"Error al procesar la pregunta: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
