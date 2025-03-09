import os
from google import genai
from google.genai import types
import streamlit as st

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
    try:
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        receta_builder = []
        for chunk in response_stream:
            print(chunk.text, end="")
            receta_builder.append(chunk.text)

        receta = "".join(receta_builder)
        return receta
    except genai.APIError as e:
        return f"Error de la API de Google: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"


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


if __name__ == "__main__":
    # Ejemplo de uso
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: La variable de entorno GOOGLE_API_KEY no está definida.")
        exit()
    comensales = 4
    ingredientes = "pollo, tomate, lechuga"
    vegetariana = False
    keto = False
    celiaco = False
    calorias = 500

    receta = generate(comensales, ingredientes, vegetariana, keto, celiaco, calorias, api_key)
    print(receta)
