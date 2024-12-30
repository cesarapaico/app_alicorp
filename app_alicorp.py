import streamlit as st
import vertexai
import google.auth
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_google_community import VertexAISearchRetriever
from langchain_google_vertexai import VertexAI


# Configuración de los parámetros
PROJECT_ID = "acpe-dev-uc-gen-ai-babel"
LOCATION = "global"
MODEL = "gemini-1.5-pro"  # Modelo generativo
DATA_STORE_ID = "datastore-alicorp-documentos_1735219596253"
DATA_STORE_LOCATION = "global"

# Set Up Application Default Credentials (ADC)
# This line retrieves credentials from the environment for authentication
credentials, project_id = google.auth.default()

# Initialize Vertex AI with retrieved credentials
vertexai.init(project=project_id, credentials=credentials)

# Configurar el modelo de lenguaje y el recuperador
llm = VertexAI(model_name=MODEL, languages=["es"])

retriever = VertexAISearchRetriever(
    project_id=PROJECT_ID,
    location_id=DATA_STORE_LOCATION,
    data_store_id=DATA_STORE_ID,
    engine_data_type=0,  # 0 indica motores de búsqueda generativa
)

# Inicializar QA con recuperación
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False  # Cambia a True si necesitas las fuentes
)

# Crear la aplicación Streamlit
def main():
    st.title("AI Chatbot")

    # Estado de sesión para almacenar el historial de conversación
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # Entrada de texto del usuario
    with st.form(key="user_input_form"):
        user_input = st.text_input("Escribe tu mensaje:", key="user_input")
        send_button = st.form_submit_button("Enviar")

    # Procesar la entrada del usuario
    if send_button and user_input:
        # Añadir la entrada del usuario al historial
        st.session_state.conversation_history.append({"role": "user", "text": user_input})

        # Generar respuesta usando el modelo
        response = qa_chain.run(user_input)

        # Añadir la respuesta del modelo al historial
        st.session_state.conversation_history.append({"role": "ai", "text": response})

    # Mostrar el historial de conversación
    st.subheader("Historial de conversación")
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.write(f"**Tú:** {message['text']}")
        elif message["role"] == "ai":
            st.write(f"**AI:** {message['text']}")

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
