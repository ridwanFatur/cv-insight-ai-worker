import vertexai
from google import genai

from utils.config import LOCATION, PROJECT_ID

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)

ai_client = genai.Client(vertexai=vertexai)