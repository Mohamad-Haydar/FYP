import pdf_processor
import os

def process_folder(folder_path, model_name, certificate_type):
    result = {}
    counter = 0

    for root, dirs, files in os.walk(folder_path):
        for file_path in files:
            full_file_path = os.path.join(root, file_path)

            # Call the process_pdf() function from pdf_processor module
            (
                data,
                user_input,
                model,
                range,
                manufactor,
                tested,
                summary,
                case,
                text,
            ) = pdf_processor.process_pdf(
                full_file_path,
                model_name,
                certificate_type,
            )
            result[counter] = {
                "file_name": file_path,
                "data": data,
                "user_input": user_input,
                "model": model,
                "range": range,
                "manufactor": manufactor,
                "tested": tested,
                "summary": summary,
                "case": case,
                "text": text,
            }
            counter += 1

    return result