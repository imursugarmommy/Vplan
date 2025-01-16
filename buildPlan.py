import requests
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta
import os
import json
import pypdf
import sys

shortform_faecher = {
    "Ma": "Mathe",
    "De": "Deutsch",
    "En": "Englisch",
    "Ge": "Geschichte",
    "Geo": "Geographie",
    "Bi": "Biologie",
    "Ku": "Kunst",
    "Sp": "Sport",
    "Inf": "Informatik",
    "Sk": "Seminarkurs",
    "Ph": "Physik",
    "PB": "Politik",
    "Tk": "Technik",
    "Ch": "Chemie",
    "Mu": "Musik",
}

url = "https://www.barnim-gymnasium.de/fileadmin/schulen/barnim-gymnasium/Dokumente/Pl%C3%A4ne/splan.pdf"

password = "schule"

pdf_path = "Stundenplan.pdf"

valid_classes = [
    "5LM",
    "6LM",
    "7/2",
    "7/3",
    "7/4",
    "7/5",
    "7/6",
    "7/7",
    "7LM",
    "7M",
    "8/2",
    "8/3",
    "8/4",
    "8/5",
    "8/6",
    "8LM",
    "8M",
    "9/2",
    "9/3",
    "9/4",
    "9/5",
    "9/6",
    "9/7",
    "9LM",
    "9M",
    "10/2",
    "10/3",
    "10/4",
    "10/5",
    "10LM",
    "10M",
    "11",
    "12",
]

faecher = {}
file_path = "information.json"

def create_faecher_dict():
    if len(sys.argv) > 1:
        user_input = sys.argv
        user_input.pop(0)
        user_input = user_input[0].split(" ")
    else:
        user_input = "No input provided"

    for fach in user_input:
        for key, value in shortform_faecher.items():
            if key in fach:
                faecher[fach] = value

    create_json_file(faecher)

def create_json_file(faecher):
    if not os.path.exists(file_path): # Create the file if it doesn't exist
        with open(file_path, "w") as file:
            json.dump({'faecher': faecher}, file, indent=4)
    else: # laod and update file if it exists
        with open(file_path, "r") as file:
            try:
                data = json.load(file)  # Load existing JSON data
            except json.JSONDecodeError:
                # If the file is empty or corrupted, initialize it
                data = {}
        
        # Add or update the data under the key
        data['faecher'] = faecher
        
        # Write the (updated) data back to the file
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

def download_pdf(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
    else:
        print(f"Fehler beim Download von {url}")


def remove_password(input_pdf, output_pdf, password):
    reader = PdfReader(input_pdf)
    if reader.is_encrypted:
        reader.decrypt(password)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)

    os.remove(input_pdf)
    os.rename(output_pdf, "Stundenplan.pdf")


def get_class_from_pdf(pdf_path):
    class_grade = "12"
    class_number = ""

    while True:
        # class_grade = input("Gib deine Klassenstufe an (7-12): ")
        class_grade = "12"

        if int(class_grade) <= 10 and int(class_grade) >= 7:
            class_number = input(f"Gib deine Klassennummer an (1-7 / LM / M): ")
            break

        input_class_name = ""

        if int(class_grade) == 11 or int(class_grade) == 12:
            input_class_name = class_grade
        elif class_number == "LM" or class_number == "M":
            input_class_name = class_grade + class_number
        else:
            input_class_name = class_grade + "/" + class_number

        if input_class_name in valid_classes:
            get_correct_page(input_class_name)
            break
        else:
            print("Invalid class. Please try again.")


def get_correct_page(input_class_name):
    reader = pypdf.PdfReader("Stundenplan.pdf")

    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")
        class_info = lines[4].split(" ")

        class_name = class_info[0]

        if class_name != input_class_name:
            continue
        else:
            return extract_plan_infos(page)

        print("failed to get correct page. Please enter your class again.")
        get_class_from_pdf(pdf_path)


def extract_plan_infos(page):
    page_array = page.extract_text().split("\n")
    page_infos = page.extract_text().split("16:40")[1]

    periods = page_infos.split("Block")

    for period in periods:
        period = period.split("\n")
        period.pop(0)

        # print("Period: ")
        # print(period)

    # 1 - 6 unnötig
    # 7 - 36 stundenplanzeiten

    # block
    # Raum von unten nach oben bis auf die ersten 3 Zeilen
    # von unten nach oben Lehrer bis auf 3 und dann oben nach unten Lehrer die anderen 3


if __name__ == "__main__":
    create_faecher_dict()

    download_pdf(url, "splan.pdf")

    remove_password("splan.pdf", "splan1_dec.pdf", password)

    get_class_from_pdf(pdf_path)
