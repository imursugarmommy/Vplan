import requests
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta
import os
import json

# URLs der PDFs
urls = [
    "https://www.barnim-gymnasium.de/fileadmin/schulen/barnim-gymnasium/Dokumente/Pl%C3%A4ne/vplan.pdf",
    "https://www.barnim-gymnasium.de/fileadmin/schulen/barnim-gymnasium/Dokumente/Pl%C3%A4ne/vplan1.pdf",
]

# Passwort für die PDFs
password = "schule"

pdf_path = "./Vertretungsplan.pdf"
wochentage = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]
faecher = {
    "LMa1": "Mathe",
    "GDe6": "Deutsch",
    "LEn3": "Englisch",
    "GGe1": "Geschichte",
    "GGeo5": "Geographie",
    "GBi4": "Biologie",
    "GKu1": "Kunst",
    "GSp6t": "Sport",
    "GIf": "Informatik",
    "Sk Sp": "Seminarkurs Eventmanagement",
}
lehrer = {
    "ak": "Hr. Ak",
    "kr": "Fr. Krakau",
    "an": "Hr. Arnold",
    "kp": "Hr. Kripylo",
    "bah": "Fr. Bahr Paz",
    "bog": "Hr. Boger",
    "lr": "Fr. Langrock",
    "bn": "Hr. Bönisch",
    "ln": "Hr. Lenken",
    "bot": "Fr. Böttcher",
    "mas": "Fr. Maas",
    "bt": "Fr. Borchert",
    "mk": "Fr. Malack",
    "buk": "Hr. Bunk",
    "mar": "Hr. Markhoff",
    "bur": "Hr. Burau",
    "mey": "Fr. Meyer",
    "caz": "Fr. Chazal",
    "mis": "Hr. Mißfeldt",
    "das": "Hr. Dr. Daske",
    "ml": "Fr. Müller",
    "fs": "Fr. Feeser",
    "mro": "Hr. Mrosek",
    "fel": "Fr. Felber",
    "nid": "Hr. Niedermeier",
    "fi": "Hr. Finger",
    "ofh": "Fr. Ofenheusle",
    "flh": "Fr. Flöhr",
    "opz": "Fr. Opitz",
    "fr": "Fr. Freitag",
    "op": "Fr. Oppen",
    "ft": "Hr. Frücht",
    "pex": "Fr. Peix",
    "fch": "Fr. Fuchs",
    "pek": "Fr. Peschke",
    "gz": "Fr. Göritz",
    "pf": "Fr. Pfeiffer",
    "goe": "Fr. Götze",
    "pg": "Hr. Pfennig",
    "gra": "Fr. Gravenkamp",
    "rm": "Hr. Rathmann",
    "gro": "Hr. Großmann",
    "rh": "Hr. Dr. Rauhut",
    "gh": "Fr. Groth",
    "rt": "Fr. Richter",
    "gun": "Hr. Gunia",
    "rit": "Fr. Richter",
    "gu": "Fr. Gust",
    "rik": "Fr. Rick",
    "gut": "Fr. Gutmann",
    "riv": "Fr. Rivetta-Weigelt",
    "hm": "Fr. Hallmann",
    "rk": "Fr. Rückert",
    "hae": "Fr. Hänsel",
    "san": "Fr. Sandring",
    "hg": "Fr. Hennig",
    "sa": "Fr. Samland",
    "her": "Hr. Herz",
    "ser": "Hr. Dr. Serwatka",
    "hs": "Hr. Höser",
    "sca": "Fr. Schaale",
    "hy": "Hr. Hoyer",
    "sz": "Hr. Schaetz",
    "jan": "Fr. Jankow",
    "sae": "Hr. Schauer",
    "js": "Fr. Jensen",
    "si": "Fr. Schieck",
    "jos": "Fr. Joswich",
    "sif": "Fr. Siefke",
    "jg": "Hr. Juergens",
    "sl": "Fr. Schlecht",
    "kap": "Hr. Kaping",
    "seb": "Fr. Schulte-Ebbert",
    "kee": "Fr. Keeling",
    "sk": "Hr. Schwarzkopf",
    "ke": "Hr. Kentzler",
    "spi": "Fr. Spinty",
    "kip": "Fr. Kipper",
    "koc": "Fr. Koch",
    "tin": "Fr. Tinius",
    "kop": "Hr. Koop",
    "wi": "Hr. Wick",
    "kor": "Fr. Koriath",
    "zar": "Fr. Zaremba",
    "kw": "Fr. Kowalski",
    "zim": "Fr. Zimmermann",
    "ko": "Fr. Koza",
    "zij": "Fr. Zimmermann",
    "kra": "Hr. Kraus",
}


# Stundenplan: [Start[Hour, Minute], End[...], BreakStart[...], BreakEnd[...]]
times = {
  "Montag": [[7, 25], [15, 15]],
  "Dienstag": [[8, 20], [12, 50]],
  "Mittwoch": [[7, 25], [14, 50], [9, 50], [12, 5]],
  "Donnerstag": [[7, 25], [12, 50], [9, 50], [12, 5]],
  "Freitag": [[8, 20], [12, 50]]
}

def download_pdf(url, filename):
    if os.path.exists(filename):
        os.remove(filename)
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


def get_weekday_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    all_lines = []
    index = 0

    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")
        all_lines.extend(lines)

    for line in all_lines:
        for day in wochentage:
            if day in line:
                return day


def decide_pdf():
    now = datetime.now()
    current_weekday = wochentage[now.weekday()]
    hour, minute = now.hour, now.minute

    pdf_days = {
        "vplan1_dec.pdf": get_weekday_from_pdf("vplan1_dec.pdf"),
        "vplan2_dec.pdf": get_weekday_from_pdf("vplan2_dec.pdf"),
    }
    
    selected_pdf = None

    dayEndHour = times[current_weekday][1][0]
    dayEndMinute = times[current_weekday][1][1]

    # * montag - freitag
    if current_weekday in ["Montag", "Dienstag", "Mittwoch", "Donnerstag"]:
        # vor schluss
        if hour < dayEndHour or (hour == dayEndHour and minute < dayEndMinute):
            selected_pdf = get_pdf_for_today(current_weekday, pdf_days)
        # nach schluss
        else:
            selected_pdf = get_pdf_for_next_day(current_weekday, pdf_days)
    # * montag - freitag
    elif current_weekday == "Freitag":
        # vor schluss
        if hour < dayEndHour or (hour == dayEndHour and minute <= dayEndMinute):
            selected_pdf = get_pdf_for_today(current_weekday, pdf_days)
        # nach schluss
        else:
            selected_pdf = get_pdf_for_today("Montag", pdf_days)
    # * samstag - sonntag
    elif current_weekday in ["Samstag", "Sonntag"]:
        selected_pdf = get_pdf_for_today("Montag", pdf_days)

    # * default / fallback if pdf is not available yet
    if selected_pdf is None:
        selected_pdf = list(pdf_days.keys())[0]

    if os.path.exists("Vertretungsplan.pdf"):
        os.remove("Vertretungsplan.pdf")

    os.rename(selected_pdf, "Vertretungsplan.pdf")
    cleanup_files(["vplan1.pdf", "vplan2.pdf", "vplan1_dec.pdf", "vplan2_dec.pdf"])


def get_pdf_for_today(day, pdf_days):
    for pdf, assigned_day in pdf_days.items():
        if assigned_day == day:
            return pdf

    return None


def get_pdf_for_next_day(current_day, pdf_days):
    next_index = (wochentage.index(current_day) + 1) % 7
    next_day = wochentage[next_index]
    return get_pdf_for_today(next_day, pdf_days)


def cleanup_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def extract_substitution_infos(pdf_path):
    reader = PdfReader(pdf_path)
    all_lines = []
    changes_count = 0

    dayDate = ""
    weekday = ""
    output_prompt = ""

    # * splits pdf into lines and saves it in a list
    for page in reader.pages:
      text = page.extract_text()
      lines = text.split("\n")
      all_lines.extend(lines)

    # * goes through all lines and picks out the subjects i have saved in the faecher dict
    for line in all_lines:
      if all_lines.index(line) == 3:
        weekday = line.split(" ")[4]
        dayDate = line.split(" ")[2]

      for index, (key, subject) in enumerate(faecher.items()):
        if key in line and " 12 " in line:
          filtered_teachers = line.split(key)[1]

          new_teacher = filtered_teachers.split(" ")[2]
          if new_teacher == "+":
              new_teacher = filtered_teachers.split(" ")[1]

          filtered_info = line.split(key)[2]
          filtered_and_divided_info = filtered_info.split(" ")

          # * edge case where the room is splitted into two words (just these two)
          if len(filtered_and_divided_info) > 2 and filtered_and_divided_info[1] == "zu" and filtered_and_divided_info[2] == "Hause":
            filtered_and_divided_info[1] = "zu Hause" 
            del filtered_and_divided_info[2]

          # * contains all viable information for the output prompt
          subject = subject
          teacher = lehrer[new_teacher]
          room = filtered_and_divided_info[1]
          typeOfChange = filtered_and_divided_info[2]

          # * to get one flowing text, add an and if there is more than one change
          if changes_count > 0:
              output_prompt += " und "

          # * increase here to keep track of how many changes there are
          changes_count += 1

          # * compose all output promps for different situations
          if typeOfChange == "Vertretung" or typeOfChange == "Betreuung":
            output_prompt += teacher + " vertritt heute " + subject
          elif typeOfChange == "Raum-Vertretung":
            output_prompt += subject + " findet heute in" + room
          elif typeOfChange == "Stillarbeit":
            output_prompt += (
                subject + " findet heute zuhause statt (" + room + ")"
            )
          elif typeOfChange == "Entfall":
            output_prompt += (
              subject
              + " bei "
              + teacher
              + " findet heute nicht statt ("
              + room
              + ")"
            )
          else:
            output_prompt += (
              subject
              + " hat eine Abwandlung (" 
              + typeOfChange 
              + ", " 
              + teacher 
              + ")"
            )

    # * custom message for when there is no change
    if output_prompt == "":
      output_prompt = "Keine Stundenplanabwandlungen"

    # * return in json format so you can get it afterwards
    return {"substitutionPlan": output_prompt, "weekday": weekday + " der " + dayDate}


if __name__ == "__main__":
    # PDFs herunterladen
  download_pdf(urls[0], "vplan1.pdf")
  download_pdf(urls[1], "vplan2.pdf")

  # Passwortschutz entfernen
  remove_password("vplan1.pdf", "vplan1_dec.pdf", password)
  remove_password("vplan2.pdf", "vplan2_dec.pdf", password)

  # PDF auswählen und speichern
  decide_pdf()

# * formatted and ready to collect json data
substitutionPlan = json.dumps(extract_substitution_infos(pdf_path))
print(substitutionPlan)
