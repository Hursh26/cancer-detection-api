from fastapi import FastAPI, Request
import google.generativeai as genai
import os
import shutil
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


# Configuring Gemini API key
genai.configure(api_key="AIzaSyCkfEwKNJQY3oedqiSA9dWcTSPZFf6wpZQ")

app = FastAPI()

# Allow CORS for all origins
origins = ["https://pulmo-carcinalyzer.vercel.app/"]  # Replace with your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/genomic")
async def genomic_testing(request: Request):
    form_data = await request.json()

    # Extract data from the form
    age = form_data.get("age")
    smoke = form_data.get("smoke")
    alcohol = form_data.get("alcohol")
    alcoholHabit = form_data.get("alcoholHabit")
    familyHistory = form_data.get("familyHistory")
    genomicTesting = form_data.get("genomicTesting")
    tumorMarkerTesting = form_data.get("tumorMarkerTesting")
    pulmonaryDisorder = form_data.get("pulmonaryDisorder")
    symptoms = form_data.get("symptoms")
    genomicTests = form_data.get("genomicTests")
    tumorMarkers = form_data.get("tumorMarkers")

    # Construct the prompt for Gemini
    prompt = f"""
criteria for cancer detection:
"1. Markers and Imaging:

CT scan: A highly sensitive imaging test that can detect lung nodules and other abnormalities.

PET scan: Uses a radioactive tracer to detect metabolic activity in the body, which can help identify cancerous tumors.

Chest X-ray: A less sensitive but still valuable tool for initial screening.

Lung function tests: Can help assess the extent of lung damage, especially in cases of lung cancer.

2. Laboratory Tests:

Blood tests: Can measure levels of markers like CEA, NSE, SCC, ProGRP, CA 125, NY-ESO-1, and Cyfra 21-1, which may be elevated in lung cancer.

Sputum cytology: Examination of mucus coughed up from the lungs to look for cancer cells.

2. Markers and Biopsy:

Biopsy: A procedure where a small sample of tissue is taken for microscopic examination. This is the most definitive way to diagnose lung cancer.

Thoracentesis: A procedure to remove fluid from the chest cavity for testing.

Bronchoscopy: A procedure where a thin tube with a camera is inserted through the nose or mouth to examine the airways. It can be used to obtain biopsy samples.

3. Multiple Markers:

Combining multiple tumor markers: Using a panel of markers can increase the diagnostic accuracy, especially in early-stage lung cancer.



4. Clinical History and Symptoms:

Risk factors: A history of smoking, exposure to environmental pollutants, or family history of lung cancer can increase the likelihood.

Symptoms: Persistent cough, chest pain, shortness of breath, or coughing up blood can be indicative of lung cancer.

5. Genetic Testing:

Genetic mutations: Certain genetic mutations, such as EGFR and ALK, are more common in lung cancer patients. Testing for these mutations can help guide treatment decisions."


step-by-step process:
Initial Assessment:
Clinical History and Symptoms

Initial Screening:
Chest X-ray

Further Investigation:
CT scan
PET scan
Lung function tests

Obtaining a Diagnosis:
Sputum cytology
Bronchoscopy
Thoracentesis
Biopsy

Further Testing (If cancer is diagnosed):
Blood tests for tumor markers
Genetic testing

analyse above information and accordingly predict cancer for below patient:

Analyze the following patient information for lung cancer risk:

    Age: {age}
    Smoke: {smoke}
    Alcohol: {alcohol}
    """
    if alcohol == "yes":
        prompt += f"Alcohol Consumption Habit: {alcoholHabit}\n"
    prompt += f"""Family History of Lung Cancer: {familyHistory}
    Genomic Testing: {genomicTesting}
    """
    if genomicTesting == "yes":
        prompt += "Genomic Tests:\n"
        for test in genomicTests:
            prompt += f"  - {test.get('test')}: {test.get('value')}\n"
    prompt += f"""Tumor Marker Testing: {tumorMarkerTesting}
    """
    if tumorMarkerTesting == "yes":
        prompt += "Tumor Marker Tests:\n"
        for marker in tumorMarkers:
            prompt += f"  - {marker.get('marker')}: {marker.get('value')}\n"
    prompt += f"""Pulmonary Disorder: {pulmonaryDisorder}
    Symptoms: {', '.join(symptoms) if symptoms else 'None'}

    Return a risk level from 0 to 3, where:
    - 0: Very low risk
    - 1: Low-moderate risk
    - 2: Moderate risk
    - 3: High risk

    Also, provide specific instructions not more than 50 words for the patient based on their risk level. 
For example, suggest further screening that are not done like: suggest markers test if not done.

response format
risk: 
instruction:

stick to this response format
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    print(response)
    # Extract the risk level and instructions from Gemini's response
    try:
        risk_level = response.text.split("risk:")[1].split("instruction:")[0].strip()
        instructions = response.text.split("instruction:")[1].strip()
    except:
        risk_level = "Error processing response"
        instructions = "Error processing response"

    return JSONResponse({"riskLevel": risk_level, "instructions": instructions})


# @app.post("/api/imaging")
# async def image_testing(file: UploadFile = File(...)):
#     # Save the uploaded ZIP file
#     filepath = "uploads/" + file.filename
#     with open(filepath, "wb") as f:
#         f.write(file.file.read())
#
#     # Extract images from the ZIP file
#     with zipfile.ZipFile(filepath, 'r') as zip_ref:
#         zip_ref.extractall("uploads/")
#
#     new_model = load_model('models/imageclassifier.keras')
#     new_model.predict(np.expand_dims(resize / 255, 0))
#
#     predicted_class_index = np.argmax(yhat)
#
#     # Your list of class names (make sure this is updated as mentioned before)
#     class_names = ["normal",
#                    "squamous.cell.carcinoma_left.hilum_T1_N2_M0_IIIa",
#                    "adenocarcinoma_left.lower.lobe_T2_N0_M0_Ib",
#                    "large.cell.carcinoma_left.hilum_T2_N2_M0_IIIa"]
#
#     # Get the predicted class name
#     predicted_class = class_names[predicted_class_index]
#
#     print(f"Predicted class is: {predicted_class}")
#
#     results = {
#         "cancer_detected": True,  # Replace with actual detection result
#         "location": "Upper lobe of left lung",  # Replace with actual location
#         "stage": "Stage II"  # Replace with actual stage
#     }
#
#     # Remove the uploaded files
#     os.remove(filepath)
#     for filename in os.listdir("uploads/"):
#         file_path = os.path.join("uploads/", filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path)
#             elif os.path.isdir(file_path):
#                 shutil.rmtree(file_path)
#         except Exception as e:
#             print(f'Failed to delete {file_path}. Reason: {e}')
#
#     return JSONResponse({"results": results})