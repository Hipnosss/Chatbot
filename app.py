from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

faq = {
    "¿Cómo sé mi talla de calzado?": "Puedes consultar nuestra guía de tallas en la sección de ayuda.",
    "¿Qué tipos de bota son resistentes al agua?": "Las botas de la línea Outdoor Pro cuentan con resistencia al agua certificada.",
    "¿Qué significa que una bota tenga puntera de acero?": "La puntera de acero protege los dedos contra impactos y compresiones, ideal para entornos industriales.",
    "¿Cuánto tardan los envíos?": "Los envíos nacionales tardan entre 2 y 5 días hábiles dependiendo de tu ubicación.",
    "¿Puedo cambiar un producto si no me sirve?": "Sí, tienes hasta 15 días para cambios. Consulta nuestra política de devoluciones."
}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"answer": "Pregunta no válida."}), 400

    for key in faq:
        if key.lower() in question.lower():
            return jsonify({"answer": faq[key]})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en calzado industrial y de senderismo."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run()
