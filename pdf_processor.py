from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from pytesseract import image_to_string
import spacy
import re

from functions.pv_functions import (
    check,
    check_PV_tests,
    checkTests_pv,
    has_repetitive_char,
    read_file,
)
from functions.inv_functions import check_INV_tests, check_inv, checkTests

nlp1 = spacy.load("./models/PV_best_model/output/model-best")  # load PV model
nlp2 = spacy.load(
    "./models/Inverter_best_model/Inverter_output/model-best"
)  # load Inverter model


def getManufactor(manufactors, text):
    for line in text.lower().splitlines():
        for key in manufactors:
            if key in line:
                return line
    return None  # Return None if no match is found

def doubleCheckPR(numbers):
    for number in numbers:
        if(int(number) % 5 != 0):
            return False
    return True

def process_pdf(file_path, model_input, certificate_type):
    print("*"*20)
    print(file_path)
    text = read_file(file_path)
    text = text.replace(":", ": ").replace(",", ", ")
    # print(text)
    manufactors = [
        "license holder",
        "manufacturer",
        "holder of certificate",
        "applicant",
        "certificate colder",
        "licensee",
        "issued to",
    ]

    manufactors = sorted(manufactors, key=lambda x: len(x), reverse=True)

    all_manufactorer = getManufactor(manufactors, text)
    manufactor = ""
    text = text.replace("\n", " ")

    if certificate_type == "PV":
        # check the tested according to
        start_pos = 0
        end_pos = 0
        tested = check_PV_tests(text)
        result = checkTests_pv(tested)
        doc = nlp1(text)
        model_name = []

        if(model_input in text):
            start_pos = text.index(model_input)
            end_pos = start_pos + len(model_input)
            final_text = (
                text[:start_pos]
                + "<span class='p-2' style='background-color: yellow;'>"
                + text[start_pos:end_pos]
                + "</span>"
                + text[end_pos:]
            )
            return (
                "compatible",
                model_input,
                model_input,
                False,
                all_manufactorer,
                tested,
                result,
                0,
                final_text,
            )

        for token in doc.ents:
            numbers = re.findall(r'\d{3}', token.text)
            flag = doubleCheckPR(numbers)
            # print(model_name)
            if token.label_ == "PV Module Name" and has_repetitive_char(token.text):
                model_name.append(token.text)
                start_pos = token.start_char
            if token.label_ == "Power Range" and len(model_name) > 0:
                # print(model_name)
                check_result, model = check(model_name, token.text, model_input)
                end_pos = token.start_char + len(token.text)
                if (check_result):
                    final_text = (
                        text[:start_pos]
                        + "<span class='p-2' style='background-color: yellow;'>"
                        + text[start_pos:end_pos]
                        + "</span>"
                        + text[end_pos:]
                    )
                    # return the final result
                    return (
                        "compatible",
                        model_input,
                        model,
                        token.text,
                        all_manufactorer,
                        tested,
                        result,
                        0,
                        final_text,
                    )
                model_name = []

    elif certificate_type == "Inverter":
        doc = nlp2(text)
        # extarct the tested according to
        tested = check_INV_tests(text)
        result = checkTests(tested)
        start_pos = 0
        end_pos = 0

        if(model_input in text):
            start_pos = text.index(model_input)
            end_pos = start_pos + len(model_input)
            final_text = (
                text[:start_pos]
                + "<span class='p-2' style='background-color: yellow;'>"
                + text[start_pos:end_pos]
                + "</span>"
                + text[end_pos:]
            )
            return (
                "compatible",
                model_input,
                model_input,
                False,
                all_manufactorer,
                tested,
                result,
                0,
                final_text,
            )

        # check for the model name without variable
        for token in doc.ents:
            if (
                token.label_ == "PV Module Name"
                and token.text.replace(" ", "") == model_input.replace(" ", "")
            ):
                start_pos = token.start_char
                end_pos = token.start_char + len(token.text)
                final_text = (
                    text[:start_pos]
                    + "<span class='p-2' style='background-color: yellow;'>"
                    + text[start_pos:end_pos]
                    + "</span>"
                    + text[end_pos:]
                )
                return (
                    "compatible",
                    model_input,
                    token.text,
                    False,
                    all_manufactorer,
                    tested,
                    result,
                    0,
                    final_text,
                )
        # check for the model name with variable
        model_name = []
        power_range = []
        for token in doc.ents:
            if token.label_ == "PV Module Name":
                # stop adding and start processing
                start_pos = token.start_char
                if len(power_range) > 0:
                    check_inv_result = check_inv(model_name, power_range, model_input)
                    if (check_inv_result):
                        end_pos = token.start_char + len(token.text)
                        final_text = (
                            text[:start_pos]
                            + "<span class='p-2' style='background-color: yellow;'>"
                            + text[start_pos:end_pos]
                            + "</span>"
                            + text[end_pos:]
                        )
                        return (
                            "compatible",
                            model_input,
                            token.text,
                            False,
                            all_manufactorer,
                            tested,
                            result,
                            0,
                            final_text,
                        )
                    model_name = []
                    power_range = []

                # add tokens to the array
                model_name.append(token.text)
            elif token.label_ == "Power Range" and len(model_name) > 0:
                power_range.append(token.text)

    return (
        "not compatible",
        model_input,
        False,
        False,
        all_manufactorer,
        tested,
        result,
        1,
        text,
    )
