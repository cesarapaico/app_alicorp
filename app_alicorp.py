import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from google.cloud import bigquery
from crewai.tools import BaseTool
from langchain_google_vertexai import VertexAI

# **Configuración de Streamlit**
st.title("CrewAI con BigQuery")
st.subheader("Generación y Ejecución de Consultas SQL")

# **Configuración del Modelo Gemini**
MODEL = "gemini-1.5-pro"
llm = VertexAI(model_name=MODEL)

# **Inicialización del Cliente de BigQuery (sin credenciales explícitas - asume SA)**
try:
    client = bigquery.Client()
    st.success("Conexión a BigQuery establecida (usando Service Account).")
except Exception as e:
    st.error(f"Error al conectar a BigQuery: {e}")
    st.stop()

# **Definición de la Herramienta BigQueryTool**
class BigQueryTool(BaseTool):
    name: str = "execute_bigquery_query"
    description: str = "Ejecuta una consulta SQL en BigQuery y devuelve los resultados."

    def _run(self, query: str) -> str:
        """Ejecuta una consulta SQL en BigQuery y devuelve los resultados."""
        try:
            query_job = client.query(query)
            results = query_job.result()
            # Formatear los resultados para una mejor visualización en Streamlit
            results_list = [list(row.values()) for row in results]
            if results.schema:
                headers = [field.name for field in results.schema]
                return {"headers": headers, "data": results_list}
            else:
                return str(results_list)
        except Exception as e:
            return f"Error al ejecutar la consulta: {e}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Esta herramienta no admite la ejecución asíncrona.")

    def __init__(self):
        super().__init__(name="execute_bigquery_query", description="Ejecuta una consulta SQL en BigQuery y devuelve los resultados.")

# **Creación de la Instancia de la Herramienta**
bigquery_tool = BigQueryTool()

# **Función para Crear y Ejecutar la Tripulación (fuera del botón)**
def run_crew():
    
    
    # Crear el agente generador de consultas
    query_generator_agent = Agent(
        role="Generador de Consultas SQL",
        goal="Generar consultas SQL precisas para BigQuery basadas en solicitudes.",
        backstory="Eres un experto en SQL y BigQuery, capaz de generar consultas complejas.",
        verbose=True,
        llm=llm,
    )

    # Crear el agente ejecutor de consultas
    query_executor_agent = Agent(
        role="Ejecutor de Consultas BigQuery",
        goal="Ejecutar consultas SQL en BigQuery y devolver los resultados.",
        backstory="Eres un experto en BigQuery con amplia experiencia en análisis de datos.",
        verbose=True,
        llm=llm,
        tools=[bigquery_tool],
    )
    
    generate_query_task = Task(
        description=f"""
        Genera una consulta SQL para BigQuery que responda a la siguiente solicitud del usuario:
        "{user_request}"
        Asegúrate de que la consulta sea precisa, eficiente y válida para BigQuery.
        """,
        expected_output="Una consulta SQL válida para BigQuery.",
        agent=query_generator_agent,
    )

    execute_query_task = Task(
        description="""
        Ejecuta la consulta SQL generada por el otro agente en BigQuery y devuelve los resultados.
        """,
        expected_output="Resultados de la consulta SQL en formato de tabla o lista.",
        agent=query_executor_agent  # Intentamos pasar el contexto aquí
    )

    crew = Crew(
        agents=[query_generator_agent, query_executor_agent],
        tasks=[generate_query_task, execute_query_task],
        verbose=False,
        process=Process.sequential,
    )

    st.info("Ejecutando la tripulación...")
    result = crew.kickoff()
    return result

# **Interfaz de Usuario en Streamlit**
user_request = st.text_area("Introduce tu solicitud de consulta:", "Obtén los 5 primeros registros de la tabla `bcp-sofia-78147.alicorp_genia.archivo`.")

if st.button("Ejecutar"):
    if user_request:
        # **Llamada a la función para ejecutar la tripulación y obtener resultados**
        crew_result = run_crew()

        st.subheader("Resultado:")
        if isinstance(crew_result, dict) and "headers" in crew_result and "data" in crew_result:
            st.table(crew_result)
        else:
            st.write(crew_result)
    else:
        st.warning("Por favor, introduce una solicitud de consulta.")