import requests
from app.config import OLLAMA_URL, MODEL_NAME

def generate_from_ollama(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1,
            "keep_alive": "20m",
            "options": {
                "num_predict": 700,
                "top_p": 0.9
            }
        },
        timeout=600
    )

    return response.json()["response"]