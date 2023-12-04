from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from pytesseract import image_to_string
import pyocr.builders
import sys
import concurrent.futures
import re
import spacy
from Crypto.Cipher import AES


def from_images_to_text(pages):
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    # Sort OCR tools based on accuracy (higher accuracy first)
    tools.sort(key=lambda tool: tool.get_available_languages()[0])

    final_text = ""
    for i, page in enumerate(pages):
        pil_image = page.convert("L")
        threshold = 150
        pil_image = pil_image.point(lambda x: 0 if x < threshold else 255)

        # Iterate over OCR tools in descending order of accuracy
        for tool in reversed(tools):
            available_languages = tool.get_available_languages()
            if "eng" in available_languages:
                ocr_text = tool.image_to_string(
                    pil_image, lang="eng", builder=pyocr.builders.TextBuilder()
                )
                final_text += ocr_text
                break
        else:
            print("No OCR tool found for English language")

    return final_text


def readFile(reader, file_path):
    extracted_text = ""
    page = reader.pages[0]
    text = page.extract_text()

    if not text:
        images = convert_from_path(file_path)
        extracted_text = from_images_to_text(images)
    else:
        pgs = reader.pages
        for i in range(len(pgs)):
            extracted_text += pgs[i].extract_text()
    return extracted_text


def read_file(file_path):
    reader = PdfReader(file_path)
    text = ""
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        text = readFile(reader, file_path)
    return text


def has_repetitive_char(string):
    for i in range(len(string) - 2):
        if string[i] == string[i + 1] == string[i + 2] and not string[i].isdigit():
            return True
    return False


def return_repetitive_char(string):
    for i in range(len(string) - 2):
        if string[i] == string[i + 1] == string[i + 2] and not string[i].isdigit():
            return f"{string[i]}{string[i + 1]}{string[i + 2]}"


def find_range(sentence):
    r = re.findall("(\d{3})", sentence)
    if len(r) >= 2:
        return [r[-2], r[-1]]
    else:
        return []


def check(models, range, user_model_inpput):
    # print("check: ", models, range, user_model_inpput)
    for model in models:
        var = return_repetitive_char(model)
        var_pos = model.find(var)
        # n = user_model_inpput[var_pos : var_pos + 3]
        numbers = re.findall(r'\d{3}', user_model_inpput)
        # print("numbers: ", numbers)
        for number in numbers:
            user_number = int(number)
            number1 = 0
            number2 = 0
            range_check = find_range(range)
            if len(range_check) >= 2:
                number1 = int(range_check[0])
                number2 = int(range_check[1])
            if (
                user_number >= number1
                and user_number <= number2
                and user_number % 5 == 0
            ):
                m = model.replace(var, "").strip()
                n = user_model_inpput.replace(number,"")
                if n.strip() in m:
                    return True, model
    return False, False


def check_PV_tests(text):
    tests = {
        "Design and Type Approval": [],
        "Safety Qualification": [],
    }

    if "IEC 61215-1" in text:
        tests["Design and Type Approval"].append("IEC 61215-1")
    if "IEC 61215-2" in text:
        tests["Design and Type Approval"].append("IEC 61215-2")

    if "IEC 61730-1" in text:
        tests["Safety Qualification"].append("IEC 61730-1")
    if "IEC 61730-2" in text:
        tests["Safety Qualification"].append("IEC 61730-2")

    return tests


def checkTests_pv(tests):
    summary = {
        "Design and Type Approval": 0,
        "Safety Qualification": 0,
    }
    for test in tests:
        if len(tests[test]) > 0:
            if "IEC 61215-1" in tests[test] and "IEC 61215-2" in tests[test]:
                summary["Design and Type Approval"] += 1
            if "IEC 61730-1" in tests[test] and "IEC 61730-2" in tests[test]:
                summary["Safety Qualification"] += 1

    return summary
