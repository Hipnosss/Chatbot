function createMessageElement(content, className) {
  const messageEl = document.createElement("div");
  messageEl.className = `chat-message ${className}`;
  messageEl.innerHTML = content;
  return messageEl;
}

async function sendMessage(customMessage = null) {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const message = customMessage || input.value.trim();
  if (!message) return;

  const userMessage = createMessageElement(message, "user");
  chatBox.appendChild(userMessage);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (!customMessage) {
    input.value = "";
    input.disabled = true;
  }

  const normalizedMessage = message.toLowerCase();

  const saludos = ["hola", "buenos días", "buenos dias", "buenas", "buenas tardes", "buenas noches"];
  const esSaludo = saludos.some(s => normalizedMessage.includes(s));

  // Si es un saludo, mostrar el menú directamente
  if (esSaludo) {
    setTimeout(() => {
      createBotMenu();
    }, 300);
    if (!customMessage) input.disabled = false;
    return;
  }

  try {
    const response = await fetch("https://chatbot-calzado.onrender.com/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: message }),
    });

    const data = await response.json();

    let botContent = data.answer;

    if (data.image_url) {
      botContent += `<br><img src="${data.image_url}" alt="Producto" style="margin-top:10px; max-width:100%; border-radius:12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">`;
    }

    const botMessage = createMessageElement(botContent, "bot");

    setTimeout(() => {
      chatBox.appendChild(botMessage);
      chatBox.scrollTop = chatBox.scrollHeight;
    }, 300);
  } catch (error) {
    const errorMessage = createMessageElement(
      "❌ Error al consultar. Intenta más tarde.",
      "bot"
    );
    chatBox.appendChild(errorMessage);
  } finally {
    if (!customMessage) input.disabled = false;
  }
}

function createBotMenu() {
  const chatBox = document.getElementById("chat-box");

  const welcomeMessage =
    "👋 ¡Hola! Soy tu asistente de First Hill. ¿En qué puedo ayudarte?";

  const messageEl = createMessageElement(welcomeMessage, "bot");

  const options = [
    { label: "1. Ver tipos de calzado", value: "1" },
    { label: "2. Guía de tallas", value: "2" },
    { label: "3. Métodos de pago", value: "3" },
    { label: "4. Contacto o devoluciones", value: "4" },
    { label: "5. Pregunta abierta", value: "5" },
  ];

  const buttonContainer = document.createElement("div");
  buttonContainer.style.marginTop = "10px";
  buttonContainer.style.display = "flex";
  buttonContainer.style.flexWrap = "wrap";
  buttonContainer.style.gap = "8px";

  options.forEach((option) => {
    const btn = document.createElement("button");
    btn.textContent = option.label;
    btn.style.padding = "6px 12px";
    btn.style.borderRadius = "8px";
    btn.style.border = "none";
    btn.style.cursor = "pointer";
    btn.style.backgroundColor = "#000";
    btn.style.color = "#fff";
    btn.style.fontSize = "14px";
    btn.style.transition = "background 0.3s";
    btn.addEventListener("click", () => sendMessage(option.value));
    buttonContainer.appendChild(btn);
  });

  messageEl.appendChild(buttonContainer);
  chatBox.appendChild(messageEl);
  chatBox.scrollTop = chatBox.scrollHeight;
}

window.addEventListener("DOMContentLoaded", () => {
  createBotMenu();
});
