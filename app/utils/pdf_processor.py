from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae todo el texto de un archivo PDF."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

if __name__ == '__main__':
    # Ejemplo de uso:
    pdf_file = "data/raw/documents/hernando_villanueva_valdes.pdf"
    try:
        content = extract_text_from_pdf(pdf_file)
        print("Texto extraído (primeros 500 caracteres):\n", content[:500])
    except FileNotFoundError:
        print(f"Error: El archivo PDF '{pdf_file}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el PDF: {e}")