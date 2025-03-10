import os
from google import genai
from google.genai import types
import streamlit as st
from fpdf import FPDF
import base64

st.title("Generador de Recetas")

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

    receta = ""
    pdf_href = None  # Inicializar pdf_href
    try:
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        receta_builder = []
        for chunk in response_stream:
            receta_builder.append(chunk.text)

        receta = "".join(receta_builder)

        # Generar PDF
        import tempfile
        import os

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, receta)

        # Guardar PDF en un archivo temporal en modo binario
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode="wb") as tmp:
            pdf.output(tmp.name)
            tmp_path = tmp.name

        # Leer el contenido del archivo temporal
        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()

        # Eliminar el archivo temporal
        os.remove(tmp_path)

        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_href = f'<a href="data:application/pdf;base64,{pdf_base64}" target="_blank">Descargar Receta en PDF</a>'

    except Exception as e:
        receta = f"Error: {e}"

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
        receta, pdf_href = generate(comensales, ingredientes, vegetariana, keto, celiaco, calorias, api_key)
        st.write("## Receta:")
        st.write(receta)
        if pdf_href:
            st.markdown(pdf_href, unsafe_allow_html=True)
        else:
            st.error("Error al generar el PDF.")
    except Exception as e:
        st.error(f"Error: {e}")
