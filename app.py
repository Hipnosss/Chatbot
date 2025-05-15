from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# 📌 Diccionario de preguntas frecuentes
faq = {
    "envío": "Hacemos envíos a toda Colombia. El envío es gratuito.",
    "cambio": "Puedes solicitar cambios dentro de los primeros 8 días.",
    "garantía": "Todos nuestros productos tienen garantía contra defectos de fábrica.",
    "talla": "Tenemos guía de tallas en la web para hombres y mujeres. ¿Te gustaría verla?",
    "pago": "Puedes pagar con tarjeta, transferencia, Addi o Sistecrédito.",
}

# 📌 Otras respuestas personalizadas
opciones_menu = {
    "1": "Tenemos botas industriales, outdoor, tácticas y de senderismo para hombre y mujer. ¿Te interesa alguna categoría específica?",
    "2": "Consulta la guía de tallas aquí: https://firsthill.com.co/tabla-de-tallas/",
    "3": "Aceptamos tarjeta de crédito/débito, Addi y Sistecrédito. También puedes pagar por PSE o en puntos físicos.",
    "4": "Puedes contactarnos en contacto@firsthill.com.co o al WhatsApp +57 3144403880.",
    "5": "Perfecto, dime tu pregunta y trataré de ayudarte.",
}

# 📌 Términos permitidos para redirigir a GPT
temas_permitidos = [
    "bota", "zapato", "calzado", "hombre", "mujer", "outdoor", "industrial",
    "talla", "envío", "cambio", "devolución", "garantía", "precio", "pago", "color", "sueldo", "pasarela", "referencia"
]

memoria_usuario = {}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").lower().strip()
    if not question:
        return jsonify({"answer": "Pregunta no válida."}), 400

    # 🎛 Menú básico
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

    # 🎯 Recordar talla
    if "mi talla es" in question:
        talla = ''.join(filter(str.isdigit, question))
        memoria_usuario["talla"] = talla
        return jsonify({"answer": f"¡Perfecto! Recordaré que tu talla es {talla}."})

    if "¿cuál es mi talla" in question or "cual es mi talla" in question:
        if "talla" in memoria_usuario:
            return jsonify({"answer": f"Tu talla es {memoria_usuario['talla']}."})
        else:
            return jsonify({"answer": "Aún no me has dicho tu talla."})

    # 🔎 Buscar en FAQ
    for key in faq:
        if key in question:
            return jsonify({"answer": faq[key]})

    # 🚫 Filtro de temas
    if not any(p in question for p in temas_permitidos):
        return jsonify({"answer": "Solo puedo ayudarte con temas relacionados al calzado y nuestra tienda. ¿Tienes una consulta sobre productos, tallas o envíos?"})

    # 🤖 Consulta a OpenAI con contexto del archivo
    try:
        with open("contenido_sitio.txt", "r", encoding="utf-8") as f:
            contexto = f.read()

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente experto de la tienda First Hill. "
                        "Usa la siguiente información para responder preguntas sobre productos, envíos, pagos y políticas:\n\n"
                        f"{contexto}"
                    )
                },
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500

@app.route("/")
def home():
    return "Servidor funcionando correctamente"

if __name__ == "__main__":
    app.run(debug=True)
