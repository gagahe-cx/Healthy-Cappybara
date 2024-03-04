'''
Written by: Yue (Luna) Jian
'''

import re
import json

def clean_name(title):
    pattern = r"^(.*?)[,|-]"
    match = re.search(pattern, title)
    if match:
        return match.group(1).strip()  
    else:
        return None  

def clean_specialty(specialties):   
    pattern = r":\s*(.+)"
    match = re.search(pattern, specialties)
    extracted_specialty = match.group(1) if match else None

    return extracted_specialty

def clean_zipcode(address):
    zip_code_pattern = r"(\d{5}(-\d{4})?)"
    combined_zip_matches = re.findall(zip_code_pattern, address)
    combined_zip_codes = [match[0] for match in combined_zip_matches] 
    if len(combined_zip_codes) == 1:
        return int(combined_zip_codes[0])
    return combined_zip_codes


def clean_rating(rating_strings):
    pattern = r"(\d+\.\d+)"  
    match = re.search(pattern, rating_strings)
    
    if match:
        return float(match.group(1))
    else:
        return None
    
def clean_num_rating(rating_strings):
    pattern = r"\((\d+) ratings\)"
    match = re.search(pattern, rating_strings)
    if match:
        return int(match.group(1))  
    else:
        return None 


def clean_procedures(text):
    procedures_pattern = r":\s*([A-Za-z\s\(\)\-\.]+)(?:,|$)"
    procedures = re.findall(procedures_pattern, text)
    clean_procuedures = "".join(list(set(procedures))).split
    
    return list(set(procedures))

def clean_conditions(conditions):
    conditions_pattern = r":\s*([A-Za-z\s\(\)\-\.]+)(?:,|$)"
    conditions = re.findall(conditions_pattern, conditions)

    return list(set(conditions))

def clean_doctor(doctor):
    cleaned = {
        "name": clean_name(doctor.get("title", "")),
        "address": doctor.get("address", ""),
        "zipcode": clean_zipcode(doctor.get("address", "")),
        "specialty": clean_specialty(doctor.get("specialties", [])),
        "clean_procedures": clean_procedures(doctor.get("procedures", [])),
        "clean_conditions": clean_conditions(doctor.get("conditions", [])),
        "rating_score": clean_rating(doctor.get("ratings", [])),
        "clean_num_rating": clean_num_rating(doctor.get("ratings", []))
    }
    return cleaned

def flatten_and_clean(element, cleaned_doctors):
    # If element is a dictionary, clean it using the clean_doctor function
    if isinstance(element, dict):
        cleaned_doctors.append(clean_doctor(element))
    # If element is a list, iterate over each item
    elif isinstance(element, list):
        for item in element:
            flatten_and_clean(item, cleaned_doctors)

def clean(filepath):
    with open(filepath, "r") as f:
        doctors = json.load(f)

    cleaned_doctors = []
    flatten_and_clean(doctors, cleaned_doctors)  

    output_file_path = filepath.replace('.json', '_normalized.json')
    with open(output_file_path, "w") as f:
        json.dump(cleaned_doctors, f, indent=4)