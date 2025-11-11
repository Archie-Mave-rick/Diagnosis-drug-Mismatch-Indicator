import pandas as pd
import json
from rapidfuzz import fuzz

# Load the claims
df = pd.read_excel("C:\\Users\\Pc\\Downloads\\training_data.xlsx")

# Load the ICD-10 codes 
with open("C:\\Users\\Pc\\Downloads\\icd10_codes.json", "r", encoding="utf-8") as f:
    icd_data = json.load(f)

# Convert ICD data into a DataFrame for easy lookup
icd_df = pd.DataFrame(icd_data)
icd_df.columns = ["ICD_Code", "ICD_Description"]  # in case columns aren't named

# Create a dictionary for quick lookup by description keyword
icd_lookup = {row["ICD_Description"].lower(): row["ICD_Code"] for _, row in icd_df.iterrows()}

# === STEP 3: Diagnosis–prescription pairs ===
valid_pairs = {
 "Malaria": ["Artemether-Lumefantrine", "Artesunate-Amodiaquine", "Dihydroartemisinin-Piperaquine", "IV Artesunate", "Quinine", "Paracetamol"],
    "Typhoid Fever": ["Azithromycin", "Ceftriaxone", "Ciprofloxacin", "Paracetamol"],
    "Cholera": ["Oral Rehydration Solution", "Azithromycin", "Doxycycline"],
    "Diarrhea": ["Oral Rehydration Solution", "Zinc", "Ciprofloxacin", "Azithromycin"],
    "Amebiasis": ["Metronidazole", "Tinidazole"],
    "Giardiasis": ["Metronidazole", "Tinidazole"],
    "Pneumonia": ["Amoxicillin", "Ceftriaxone", "Ampicillin", "Gentamicin"],
    "Bronchitis": ["Paracetamol", "Salbutamol"],
    "Otitis Media": ["Amoxicillin", "Amoxicillin-Clavulanate"],
    "Pharyngitis": ["Penicillin V", "Amoxicillin"],
    "Sinusitis": ["Amoxicillin-Clavulanate", "Amoxicillin"],
    "Meningitis": ["Ceftriaxone", "Cefotaxime", "Vancomycin"],
    "Sepsis": ["Ceftriaxone", "Gentamicin", "Metronidazole"],
    "Urinary Tract Infection": ["Nitrofurantoin", "Cotrimoxazole", "Ceftriaxone"],
    "Bacterial Vaginosis": ["Metronidazole"],
    "Trichomoniasis": ["Metronidazole"],
    "Gonorrhoea": ["Ceftriaxone"],
    "Chlamydia": ["Azithromycin", "Doxycycline"],
    "Syphilis": ["Benzathine Penicillin G"],
    "Skin Infection": ["Flucloxacillin", "Amoxicillin-Clavulanate", "Mupirocin"],
    "Scabies": ["Permethrin", "Ivermectin"],
    "Tinea Infection": ["Clotrimazole", "Terbinafine"],
    "Candidiasis": ["Nystatin", "Fluconazole"],
    "Leprosy": ["Rifampicin", "Dapsone", "Clofazimine"],
    "Schistosomiasis": ["Praziquantel"],
    "Helminth Infection": ["Albendazole", "Mebendazole"],
    "Onchocerciasis": ["Ivermectin"],
    "Tuberculosis": ["Isoniazid", "Rifampicin", "Pyrazinamide", "Ethambutol"],
    "HIV Infection": ["Tenofovir", "Lamivudine", "Dolutegravir"],
    "HIV Opportunistic Infection": ["Cotrimoxazole"],
    "Cryptococcal Meningitis": ["Amphotericin B", "Flucytosine", "Fluconazole"],
    "Eclampsia": ["Magnesium Sulfate", "Hydralazine", "Labetalol"],
    "Postpartum Haemorrhage": ["Oxytocin", "Misoprostol"],
    "Hypertension": ["Amlodipine", "Lisinopril", "Losartan", "Hydrochlorothiazide"],
    "Diabetes Mellitus": ["Metformin", "Gliclazide", "Insulin"],
    "Asthma": ["Salbutamol", "Prednisolone", "Budesonide"],
    "COPD": ["Salbutamol", "Ipratropium", "Prednisolone"],
    "Gout": ["Colchicine", "Indomethacin", "Allopurinol"],
    "Rheumatoid Arthritis": ["Methotrexate", "NSAIDs"],
    "Osteoarthritis": ["Paracetamol", "Ibuprofen"],
    "Heart Failure": ["Enalapril", "Furosemide", "Carvedilol"],
    "Anemia": ["Ferrous Sulfate", "Folic Acid"],
    "Malnutrition": ["F-75", "F-100", "Ampicillin", "Gentamicin"],
    "Depression": ["Fluoxetine"],
    "Psychosis": ["Haloperidol", "Risperidone"],
    "Epilepsy": ["Phenobarbital", "Sodium Valproate", "Carbamazepine"],
    "Migraine": ["Ibuprofen", "Sumatriptan"],
    "Prostatic Hyperplasia": ["Tamsulosin", "Finasteride"],
    "H. Pylori Infection": ["Omeprazole", "Amoxicillin", "Clarithromycin"],
    "Peptic Ulcer Disease": ["Omeprazole", "Pantoprazole"],
    "Stroke": ["Aspirin", "Clopidogrel", "Atorvastatin"],
    "Dyslipidemia": ["Atorvastatin"],
    "Allergic Reaction": ["Cetirizine", "Prednisolone"],
    "Anaphylaxis": ["Epinephrine", "Hydrocortisone"],
    "Poisoning": ["Atropine", "Pralidoxime"],
    "Snakebite": ["Antivenom", "Supportive Care"],
    "Conjunctivitis": ["Chloramphenicol"],
    "Otitis Externa": ["Ciprofloxacin Ear Drops"],
    "Trachoma": ["Azithromycin"],
    "Pelvic Inflammatory Disease": ["Ceftriaxone", "Doxycycline", "Metronidazole"],
    "Endometritis": ["Ampicillin", "Gentamicin", "Metronidazole"],
    "Hyperemesis Gravidarum": ["Metoclopramide", "Ondansetron"],
    "Insomnia": ["Temazepam"],
    "Alcohol Withdrawal": ["Diazepam", "Lorazepam"],
    "Obsessive Compulsive Disorder": ["Fluoxetine"],
    "Post-Traumatic Stress Disorder": ["Fluoxetine"],
}

# Define helper functions 

def get_icd_info(diagnosis):
    """Get ICD code and description from lookup"""
    diagnosis_lower = diagnosis.lower()
    best_match = None
    best_score = 0
    best_code = "N/A"
    best_description = "N/A"
    for desc, code in icd_lookup.items():
        score = fuzz.partial_ratio(diagnosis_lower, desc)
        if score > best_score:
            best_score = score
            best_code = code
            best_description = desc
    if best_score > 80:
        return best_code, best_description
    return best_code, best_description


def check_match(diagnosis, prescription):
    """Check if diagnosis and prescription match"""
    if pd.isna(diagnosis) or pd.isna(prescription) or diagnosis.strip() == "" or prescription.strip() == "":
        return "Empty Cell"

    if diagnosis not in valid_pairs:
        return "Unknown Diagnosis"

    allowed = valid_pairs[diagnosis]
    for drug in allowed:
        score = fuzz.partial_ratio(prescription.lower(), drug.lower())
        if score > 85:
            return "Match✅"
    return "Mismatch❌"

# Apply logic
df["ICD_Code"], df["ICD_Description"] = zip(*df["Diagnosis"].map(get_icd_info))
df["Check_Result"] = df.apply(lambda x: check_match(x["Diagnosis"], x["Prescription"]), axis=1)

# Display and export 
print("🔍 FULL VERIFICATION RESULTS:")
print(df[["Diagnosis", "ICD_Code", "ICD_Description", "Prescription", "Check_Result"]])

print("\n SUMMARY COUNTS:")
print(df["Check_Result"].value_counts(dropna=False))

output_file = "claims_checked_with_icd.xlsx"
df.to_excel(output_file, index=False)
print(f"\n✅ File exported successfully as: {output_file}")
