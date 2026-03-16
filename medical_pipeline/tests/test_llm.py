import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

# Մեր սիմուլյացիոն բժշկական տեքստը
text = """
Patient Name: Hakobyan Colak. Date of Birth: 02.10.1956. 
The patient visited the clinic. 
Diagnosis: Mild hypertension, observation required.
"""

prompt = f"""
Extract the patient name, date of birth, and diagnosis from the text.
Return ONLY a valid JSON object with keys: "name", "dob", and "diagnosis".
Do not include any other text.

Text: {text}
"""

print("Ուղարկում ենք հարցումը լոկալ Llama 3-ին... Սպասիր մի քանի վայրկյան...")

response = requests.post(OLLAMA_URL, json={
    "model": "llama3",
    "prompt": prompt,
    "format": "json",
    "stream": False,
    "options": {"temperature": 0.0}
})

parsed_data = json.loads(response.json()["response"])
print("\n✅ Հաջողվեց: Ահա Ollama-ի վերադարձրած մաքուր JSON-ը.\n")
print(json.dumps(parsed_data, indent=4))
