from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Leer el archivo de texto una sola vez al iniciar la app
with open("contenido.txt", "r", encoding="utf-8") as f:
    contenido_sitio = f.read()

memoria_usuario = {}

faq = {
    "¿cómo sé mi talla de calzado?": "Puedes consultar nuestra guía de tallas en la sección de ayuda.",
    "¿qué tipos de bota son resistentes al agua?": "Las botas de la línea Outdoor Pro cuentan con resistencia al agua certificada.",
    "¿qué significa que una bota tenga puntera de acero?": "La puntera de acero protege los dedos contra impactos y compresiones, ideal para entornos industriales.",
    "¿cuánto tardan los envíos?": "Los envíos nacionales tardan entre 2 y 5 días hábiles dependiendo de tu ubicación.",
    "¿puedo cambiar un producto si no me sirve?": "Sí, tienes hasta 15 días para cambios. Consulta nuestra política de devoluciones."
}

opciones_menu = {
    "1": "Ofrecemos calzado industrial (Titanium, SteelGuard) y senderismo (OutdoorPro, UltraGrip).",
    "2": "Consulta la guía de tallas aquí: https://firsthill.com.co/tabla-de-tallas",
    "3": "Aceptamos tarjeta de crédito, débito, PSE, Nequi y Daviplata.",
    "4": "Contáctanos por WhatsApp al +57 3144403880 o revisa políticas en https://firsthill.com.co/"
}

temas_permitidos = [
    "bota", "zapato", "calzado", "pago", "talla", "envío",
    "pedido", "devolución", "guía", "seguridad", "trabajo", "senderismo"
]

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").lower().strip()
    if not question:
        return jsonify({"answer": "Pregunta no válida."}), 400

    menu_html = (
        "👋 ¡Hola! Soy tu asistente de First Hill.<br><br>"
        "¿En qué puedo ayudarte?<br><br>"
        "<strong>1.</strong> Ver tipos de calzado<br>"
        "<strong>2.</strong> Guía de tallas<br>"
        "<strong>3.</strong> Métodos de pago<br>"
        "<strong>4.</strong> Contacto o devoluciones<br>"
        "<strong>5.</strong> Hacer una pregunta abierta<br><br>"
        "<em>(Escribe solo el número de opción o tu consulta)</em>"
    )

    if question in ["", "hola", "buenos días", "buenas", "menú", "menu", "opciones"]:
        return jsonify({"answer": menu_html})

    if question in opciones_menu:
        return jsonify({"answer": opciones_menu[question]})

    if "mi talla es" in question:
        talla = ''.join(filter(str.isdigit, question))
        memoria_usuario["talla"] = talla
        return jsonify({"answer": f"¡Perfecto! Recordaré que tu talla es {talla}."})

    if "¿cuál es mi talla" in question or "cual es mi talla" in question:
        if "talla" in memoria_usuario:
            return jsonify({"answer": f"Tu talla es {memoria_usuario['talla']}."})
        else:
            return jsonify({"answer": "Aún no me has dicho tu talla."})

    for key in faq:
        if key in question:
            return jsonify({"answer": faq[key]})

    if not any(p in question for p in temas_permitidos):
        return jsonify({"answer": "Solo puedo ayudarte con temas relacionados al calzado y nuestra tienda. ¿Tienes una consulta sobre productos, tallas o envíos?"})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente experto en calzado industrial y de senderismo. "
                        "Responde únicamente preguntas relacionadas con calzado, tallas, productos, materiales, pagos, envíos o nuestra tienda. "
                        "Usa la siguiente información para responder:\n\n"
                        f"{contenido_sitio}"
                    )
                },
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
