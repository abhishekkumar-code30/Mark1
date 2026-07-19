import requests

OLLAMA_URL = "https://ollama.com/api"
API_KEY = "72e74515942743bdb5cb607204dee87d.2V6U6vAKNAk3liyxEuhpra_V"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

prompt = input("Ask something: ")
payload = {
    "model": "gemma4:31b",
    "prompt": prompt,
    "stream": False
}

response = requests.post(f"{OLLAMA_URL}/generate", headers=headers, json=payload)
result = response.json()
print(result["response"])