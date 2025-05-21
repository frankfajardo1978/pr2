import os
import openai
import sys

def main():
    # Obtener la clave de API de OpenAI desde variable de entorno
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Falta la variable de entorno OPENAI_API_KEY.")
        sys.exit(1)

    openai.api_key = api_key

    try:
        # Leer commits desde archivo
        with open("commits.txt", "r", encoding="utf-8") as f:
            commits = f.read().strip()

        # Si no hay commits, salir temprano
        if not commits:
            mensaje = "ℹ️ No hay commits nuevos para revisar."
            print(mensaje)
            with open("revision.txt", "w", encoding="utf-8") as out:
                out.write(mensaje)
            return

        print("🔍 Enviando commits a OpenAI (gpt-3.5-turbo)...\n")

        # Limitar longitud del texto (≈ 4000 tokens)
        max_chars = 12000
        if len(commits) > max_chars:
            commits = commits[:max_chars]
            print("⚠️ Los commits fueron truncados por exceder el tamaño máximo.")

        # Llamada a OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos un revisor de código. Dado un resumen de cambios de un PR, "
                        "comentá si hay algo que mejorar o si está todo bien."
                    )
                },
                {
                    "role": "user",
                    "content": f"Estos son los mensajes de commit:\n\n{commits}"
                }
            ]
        )

        # Extraer respuesta
        revision = response.choices[0].message.content.strip()

        print("🧠 Sugerencias de revisión:\n")
        print(revision)

        # Guardar resultado
        with open("revision.txt", "w", encoding="utf-8") as out:
            out.write(revision)

    except openai.error.RateLimitError:
        mensaje = "⚠️ No se pudo completar la revisión: superaste el límite de uso de OpenAI."
        print(mensaje)
        with open("revision.txt", "w", encoding="utf-8") as out:
            out.write(mensaje)

    except Exception as e:
        mensaje = f"❌ Error durante la revisión automática: {e}"
        print(mensaje)
        with open("revision.txt", "w", encoding="utf-8") as out:
            out.write(mensaje)
        # Descomenta la siguiente línea si querés que el CI falle en caso de error
        # sys.exit(1)

if __name__ == "__main__":
    main()
