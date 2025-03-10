import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
import gen_pub

def generar_pdf(receta):
    """
    Genera un PDF con la receta de cocina estructurada.
    Si no hay datos estructurados para ingredientes o preparación, se muestra
    todo el contenido en el campo de "preparacion".
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Título
    story.append(Paragraph(receta.get("titulo", "Receta de Cocina"), styles["Title"]))
    story.append(Spacer(1, 12))

    # Sección de Ingredientes (solo si existen)
    ingredientes = receta.get("ingredientes", [])
    if ingredientes:
        story.append(Paragraph("Ingredientes:", styles["Heading2"]))
        story.append(Spacer(1, 6))
        for ingrediente in ingredientes:
            story.append(Paragraph(ingrediente, styles["Normal"]))
            story.append(Spacer(1, 6))

    # Sección de Preparación o Texto completo (si no hay datos estructurados)
    preparacion = receta.get("preparacion", "")
    if preparacion:
        story.append(Spacer(1, 12))
        story.append(Paragraph("Preparación:", styles["Heading2"]))
        story.append(Spacer(1, 6))
        for linea in preparacion.split('\n'):
            story.append(Paragraph(linea, styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    st.markdown("<h1 style='text-align: center;'>Chef AI</h1>", unsafe_allow_html=True)

    # API key
    #api_key = st.secrets.get("API_KEY")
    api_key = ("AIzaSyCrnhpYqo4Y94lY5E6rS4ZLuh_QJoxbC_U")
    if not api_key:
        st.error("La API key no está configurada. Configura la API_KEY en secrets.toml.")
        return

    # Inputs del usuario
    tipo_alimentacion = st.selectbox("Tipo de alimentación", ["Omnívoro", "Vegetariano", "Vegano", "Keto", "Celíaco"])
    cantidad_comensales = st.number_input("Cantidad de comensales", min_value=1, max_value=10, value=1)
    ingredientes = st.text_input("Ingredientes que desea utilizar (separados por coma)")
    contador_calorias = st.number_input("Cantidad máxima de calorías por porción", min_value=100, max_value=2000, value=500)

    if st.button("Generar Receta"):
        try:
            # Llamada a la función que genera la receta
            receta = gen_pub.generate(tipo_alimentacion, cantidad_comensales, ingredientes, contador_calorias, api_key)

            # Mostrar la respuesta generada por la IA en la interfaz de Streamlit
            st.write("Receta generada:", receta)

            # Si se detecta "Error" en la respuesta, se muestra el error
            if "Error" in receta:
                st.error(receta)
            else:
                # Guardar la receta en el estado de la sesión
                st.session_state.receta = receta
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

    # Mostrar información de depuración sobre la estructura de la receta
    if st.session_state.get("receta"):
        pass
    else:
        st.write("No hay receta guardada en el estado.")

    if st.button("Imprimir Receta"):
        try:
            receta = st.session_state.get("receta", None)

            if receta:
                # Si la receta es un string, la convertimos en una estructura mínima
                if isinstance(receta, str):
                    receta_pdf = {
                        "titulo": "Receta de Cocina",
                        "ingredientes": [],
                        "preparacion": receta  # Todo el texto se muestra aquí
                    }
                # Si es un diccionario, usamos sus claves
                elif isinstance(receta, dict):
                    receta_pdf = {
                        "titulo": "Receta de Cocina",
                        "ingredientes": [],
                        "preparacion": receta
                    }

                pdf_buffer = generar_pdf(receta_pdf)

                st.download_button(
                    label="Descargar Receta en PDF",
                    data=pdf_buffer,
                    file_name="receta.pdf",
                    mime="application/pdf",
                )
            else:
                st.warning("Genera una receta primero o revisa que la receta esté correctamente estructurada.")
        except Exception as e:
            st.error(f"Ocurrió un error al generar el PDF: {e}")

if __name__ == "__main__":
    main()
    st.markdown("<p style='text-align: center;'>© 2025 Chef AI</p>", unsafe_allow_html=True)
