from flask import Blueprint, render_template, request, jsonify
from app.controller.model.GestorChatBot import GestorChatBot
from app.controller.model.GestorEspecies import GestorEspecies
from app.controller.model.GestorEquipos import GestorEquipos


def chatbot_blueprint(db):
    """
    Crea y configura el blueprint del ChatBot.
    Define las rutas de acceso a la vista y al endpoint de consulta
    de comandos del ChatBot.
    """
    chatbot_bp = Blueprint("chatbot", __name__)

    # Inicialización de gestores de dominio
    gestor_especies = GestorEspecies(db)
    gestor_equipos = GestorEquipos(db)

    # Inicialización del gestor principal del ChatBot
    gestor_chatbot = GestorChatBot(gestor_especies, gestor_equipos)

    @chatbot_bp.route("/chatbot", methods=["GET"])
    def vista_chatbot():
        """
        Muestra la vista del ChatBot.
        El acceso se realiza desde el menú principal (prueba manual).
        """
        return render_template("chatbot.html")

    @chatbot_bp.route("/chatbot/consultar", methods=["POST"])
    def consultar_chatbot():
        """
        Recibe un comando enviado desde la vista del ChatBot,
        delega su procesamiento al GestorChatBot y devuelve
        la respuesta en formato JSON.
        """
        # Obtención segura del JSON enviado por la vista
        data = request.get_json(silent=True) or {}
        comando = (data.get("comando") or "").strip()

        # Procesamiento del comando
        respuesta = gestor_chatbot.procesarComando(comando)

        # Respuesta al cliente en formato JSON
        return jsonify({"respuesta": respuesta})

    return chatbot_bp
