import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import gen_pub

def generar_pdf(data):
    """
    Genera un PDF con la receta.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    story.append(Paragraph("Receta de Cocina", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(data, styles["Normal"]))
    story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Configuración de la página Streamlit
    st.set_page_config(
        page_title="Recomendador de Recetas de Cocina",
        page_icon="🍳",
    )

    # Barra de navegación lateral
    menu = ["Home", "Info"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.title("Tu asistente de cocina")
        # API key
        api_key = st.secrets.get("api_key")
        if not api_key:
            st.error("La API key no está configurada. Configura la api_key en secrets.toml.")
            return
    elif choice == "Info":
        st.title("Información")
        st.markdown("""
        <div class="info-text">
        Esta aplicación te permite obtener recomendaciones de recetas de cocina personalizadas.
        Ingresa los ingredientes que tienes disponibles, tus restricciones dietéticas (vegetariana, keto, celiaca)
        y el número máximo de calorías que deseas consumir. La aplicación generará una receta adaptada a tus preferencias.
        </div>
        """, unsafe_allow_html=True)
        # API key
        api_key = st.secrets.get("api_key")
        if not api_key:
            st.error("La API key no está configurada. Configura la api_key en secrets.toml.")
            return

    # Estilos CSS personalizados
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #000000; /* Black */
            font-family: sans-serif;
        }
        .header {
            background-color: #a0522d; /* Sienna */
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        h1 {
            color: #008000; /* Green */
        }
        
            font-size: 2.5em;
        }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #663300; /* Chocolate */
            color: white;
            text-align: center;
            padding: 10px;
            margin: 0px;
            border-radius: 10px;
        }
        .stButton > button {
            color: #4F7942;
            background-color: #E1F0DA;
            border-color: #4F7942;
        }
        .stTextInput > label,
        .stNumberInput > label,
        .stSelectbox > label,
        .stArea > label {
            color: white;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background-color: #D3D3D3;
            color: black;
        }
        .stTextArea > div > textarea {
            background-color: #D3D3D3;
            color: black;
        }
        </style>
        <div class="header">
            <h1>Recomendador de Recetas</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        .info-text {
            color: #333333; /* Dark gray */
            background-color: #f0e68c; /* Khaki */
            padding: 10px;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    footer="""
    <style>
    .footer {
        solid 1px #4F7942;
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #a0522d; /* Sienna */
        color: white;
        text-align: center;
        padding: 10px;
        margin: 0px;
        border-radius: 10px;
    }
    </style>
    <div class="footer">
        <p>Todos los Derechos Reservados 2025</p>
    </div>
    """
    
    st.markdown(footer, unsafe_allow_html=True)
    receta = None

    with st.form("receta_form"):
        # Inputs para la receta
        comensales = st.number_input("Comensales", min_value=1, max_value=10, value=4)
        ingredientes = st.text_input("Ingredientes disponibles", value="pollo, tomate, lechuga")
        vegetariana = st.checkbox("Vegetariana?")
        keto = st.checkbox("Keto?")
        celiaco = st.checkbox("Celiaco?")
        calorias = st.number_input("Calorías máximas", min_value=100, max_value=2000, value=500)

        submitted = st.form_submit_button("Generar")

    if submitted:
        try:
            # Llamada a la función que genera la receta
            receta = gen_pub.generate(comensales, ingredientes, vegetariana, keto, celiaco, calorias, api_key)
            st.session_state["receta"] = receta

            # Mostrar la respuesta generada por la IA en la interfaz de Streamlit
            st.write("Resultado generado:", receta)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

    if st.button("Exportar a PDF"):
        receta = st.session_state.get("receta", "")

        if receta:
            try:
                pdf_buffer = generar_pdf(receta)

                st.download_button(
                    label="Descargar PDF",
                    data=pdf_buffer.getvalue(),
                    file_name="receta.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Ocurrió un error al generar el PDF: {e}")
        else:
            st.warning("Genera una receta primero.")
if __name__ == "__main__":
    main()
