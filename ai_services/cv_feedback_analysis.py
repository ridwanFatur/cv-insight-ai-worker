from google.genai import types
from ai_services.client import ai_client

def parse_gcs_url(file_link: str) -> str:
    file_link = file_link.strip("'\"")
    if not file_link.startswith("https://storage.googleapis.com/"):
        raise ValueError("Invalid URL")
    path = file_link.replace("https://storage.googleapis.com/", "")
    file_uri = f"gs://{path}"
    return file_uri


def get_feedback(file_link):
    prompt = """
		Analyze if the attached PDF is a CV/Resume. 

		If YES:
		Directly provide a concise, bulleted review focusing ONLY on high-impact improvements (Structure, Wording, and Skills). 
		DO NOT include any introductory confirmation (e.g., do not say "Yes, this is a CV" or "Here is a review"). 
		Start immediately with the bullet points.
		Keep the feedback brief and actionable. Use the same language as the CV.

		If NO:
		State only: "This tool is exclusively for CV/Resume reviews."
	"""
    file_uri = parse_gcs_url(file_link)
    generation_config = types.GenerateContentConfig(
		max_output_tokens=500, 
		temperature=0.7,        
	)
    response = ai_client.models.generate_content(
		model="gemini-2.0-flash",
		contents=[
			types.Part.from_uri(
				file_uri=file_uri,
				mime_type="application/pdf"
			),
			prompt
		],
		config=generation_config
	)
    return response.text
    
