import base64
import os
from google import genai
from google.genai import types
import streamlit as st

def generate( tipo_alimentacion, cantidad_comensales, ingredientes, contador_calorias, api_key):
    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.0-flash"
    prompt = f"""Recomiéndame una receta de cocina considerando los siguientes parámetros:
    Cantidad de comensales: {cantidad_comensales}
    Ingredientes disponibles: {ingredientes}
    Restricciones dietéticas: {tipo_alimentacion}
    
    Contador de calorías: {contador_calorias}
    """

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
            types.Part.from_text(text="""Eres un chef experto y quieres recomendar las mejores recetas de cocina para cualquier persona. Preguntas a través de inputs las características necesarias para hacer una receta como:
            - Cantidad de comensales
            - Ingredientes disponibles
            - Restricciones dietéticas (vegetariana, vegana, keto, celíaca)
            - Tipo de alimentación (vegetariano, vegano, omnívoro, keto, celíaco)
            - Contador de calorías

            Recomienda siempre recetas equilibradas y deliciosas, teniendo en cuenta las restricciones dietéticas y los ingredientes disponibles.
            """),
        ],
    )

    rutina = ""
    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")
            rutina += chunk.text

        return rutina
    except Exception as e:
        return f"Error: Ocurrió un error al generar la rutina: {e}"

if __name__ == "__main__":

    generate()

