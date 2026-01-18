
import sys
import PyPDF2

def extract_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = extract_text(sys.argv[1])
        output_file = sys.argv[1] + ".txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Written to {output_file}")
    else:
        print("Please provide a file path.")
