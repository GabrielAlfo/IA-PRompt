import streamlit as st
import os
from google import genai
from google.genai import types
import base64
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

st.title("Generador de Recetas")

st.markdown("""
    <div style="margin-top: 70px; padding: 20px; background-color: black; border-radius: 5px;">
        <h2>Acerca de esta aplicación</h2>
        <p>Esta aplicación genera recetas de cocina basadas en tus preferencias.</p>
        <p>Puedes especificar la cantidad de comensales, los ingredientes disponibles, si la receta debe ser vegetariana, keto o apta para celíacos, y la cantidad máxima de calorías.</p>
    </div>
    """, unsafe_allow_html=True)

# Obtener la clave de API de secrets.toml
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets = f.read()
        api_key = secrets.split('"')[1]
except FileNotFoundError:
    st.error("Error: El archivo .streamlit/secrets.toml no se encuentra.")
    st.stop()
except Exception as e:
    st.error(f"Error al leer el archivo .streamlit/secrets.toml: {e}")
    st.stop()

# Widgets de entrada
comensales = st.slider("Comensales", 1, 10, 4)
ingredientes = st.text_input("Ingredientes disponibles", "pollo, tomate, lechuga")
vegetariana = st.checkbox("Vegetariana")
keto = st.checkbox("Keto")
celiaco = st.checkbox("Celiaco")
calorias = st.number_input("Calorías máximas", 100, 2000, 500)

def generate(comensales, ingredientes, vegetariana, keto, celiaco, calorias, api_key):
    
    receta = ""
    pdf_href = None  # Inicializar pdf_href
    try:
        client = genai.Client(
            api_key=api_key,
        )

        model = "gemini-2.0-flash"
        prompt = _build_prompt(comensales, ingredientes, vegetariana, keto, celiaco, calorias)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""Eres un chef y quieres recomendar las mejores recetas de cocina para cualquier persona. Preguntas a través de inputs las características necesarias para hacer una receta como:
                - Cantidad de comensales
                - Ingredientes disponibles
                - Si es vegetariana
                - Si es keto
                - Si es celiaco
                - Calorías máximas permitidas

                Recomiendas siempre recetas que se adapten a las preferencias y restricciones alimentarias del usuario."""),
            ],
        )

        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        receta_builder = []
        for chunk in response_stream:
            receta_builder.append(chunk.text)

        receta = "".join(receta_builder)

    except Exception as e:
        receta = f"Error: {e}"
        pdf_href = None

    return receta, pdf_href


def _build_prompt(comensales, ingredientes, vegetariana, keto, celiaco, calorias):
    prompt = f"""Recomiéndame una receta de cocina.
    Cantidad de comensales: {comensales}
    Ingredientes disponibles: {ingredientes}
    Vegetariana: {vegetariana}
    Keto: {keto}
    Celiaco: {celiaco}
    Calorías máximas: {calorias}
    """
    return prompt

# Generar la receta al hacer clic en el botón
if st.button("Generar Receta"):
    try:
        st.markdown(
        f"""
        <style>
        .stButton > button {{
            color: #4F8BF9;
            border: 2px solid #4F8BF9;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
        receta, pdf_href = generate(comensales, ingredientes, vegetariana, keto, celiaco, calorias, api_key)
        st.write("## Receta:")
        st.write(receta)
    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown("""
    <footer class="footer text-white text-center py-3 fixed-bottom" style="background-color: #2E86C1;">
      <div class="container">
        <span class="text-muted">© 2025 Generador de Recetas</span>
      </div>
    </footer>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    color: white;
    background-color: #2E86C1;
}
.navbar {
    margin-bottom: 50px; /* Adjust as needed */
}
body {
    padding-top: 50px; /* Adjust based on navbar height */
    margin: 0;
}
</style>
""", unsafe_allow_html=True)