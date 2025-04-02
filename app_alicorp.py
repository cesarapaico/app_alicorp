import streamlit as st
import vertexai
import google.auth
from langchain_google_vertexai import VertexAI

# Configuración de los parámetros
PROJECT_ID = "acpe-dev-uc-gen-ai-babel"
LOCATION = "global"
MODELOS = [
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-pro-exp-03-25",
]

# Set Up Application Default Credentials (ADC)
credentials, project_id = google.auth.default()

# Inicializar Vertex AI con las credenciales obtenidas
vertexai.init(project=project_id, credentials=credentials)


# Crear la aplicación Streamlit
def main():
    st.title("AI Chatbot con Carga y Descarga de Archivo SQL")

    # Variable de contexto
    contexto = st.text_area("Introduce el contexto o las instrucciones:", height=150)

    # Widget para cargar el archivo SQL
    uploaded_file = st.file_uploader("Carga un archivo SQL (.sql)", type=["sql"])

    # Widget para la temperatura
    temperatura = st.slider(
        "Temperatura del modelo", min_value=0.0, max_value=1.0, value=0.2, step=0.1
    )

    # Widget para seleccionar el modelo
    modelo_seleccionado = st.selectbox("Selecciona el modelo LLM", MODELOS)
    
    # Botón para procesar el archivo
    if st.button("Generar Script SQL"):
        if uploaded_file and contexto:
            try:
                # Leer el contenido del archivo SQL
                contenido_archivo = uploaded_file.getvalue().decode("utf-8")

                # Combinar el contexto y el contenido del archivo
                entrada_usuario = f"{contexto}\n\nContenido del archivo SQL:\n{contenido_archivo}"
                print("modelo_seleccionado",modelo_seleccionado)
                # Configurar el modelo de lenguaje con la temperatura
                llm = VertexAI(
                    model_name=modelo_seleccionado,
                    languages=["es"],
                    temperature=temperatura,
                )

                # Generar respuesta usando el modelo
                response = llm.invoke(entrada_usuario)
 
                # Descargar la respuesta como archivo SQL
                st.download_button(
                    label="Descargar Script SQL",
                    data=response.encode("utf-8"),
                    file_name="script_generado.sql",
                    mime="application/sql",
                )

                # Limpiar el historial de conversación
                st.session_state.conversation_history = []

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")

    # Estado de sesión para almacenar el historial de conversación
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

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