import requests
import json
import threading
import sys
import os

OLLAMA_URL = "https://ollama.com/api"
API_KEY = "72e74515942743bdb5cb607204dee87d.2V6U6vAKNAk3liyxEuhpra_V"

if not API_KEY:
    print("[ERROR] Set OLLAMA_API_KEY environment variable first.")
    print("Currently => PowerShell:  $env:OLLAMA_API_KEY={API_KEY}")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

messages = [
    {
        "role": "system",
        "content": (
            "Respond in plain text only. Do not use any markdown formatting "
            "such as #, ##, **, *, ```, tables, or bullet points with *. "
            "Use plain dashes - for lists if needed. Try to keep your responses "
            "concise and to the point. Avoid unnecessary explanations or "
            "elaborations unless until told so. If you don't know the answer, "
            "simply say 'I don't know' or 'I'm not sure'."
        )
    }
]

def loading_animation(stop_event):
    dots = 0
    while not stop_event.is_set():
        dots = (dots % 3) + 1
        sys.stdout.write(f"\rMARK 1: {'.' * dots}{'   '}")
        sys.stdout.flush()
        stop_event.wait(0.5)
    sys.stdout.write("\rMARK 1: ")
    sys.stdout.flush()

print("MARK 1 - Type /exit to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "/exit":
        print("Goodbye!")
        break

    if not user_input:
        print("(empty input, try again)")
        continue

    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": "gemma4:31b",
        "messages": messages,
        "stream": True
    }

    stop_event = threading.Event()
    loader = threading.Thread(target=loading_animation, args=(stop_event,))
    loader.start()

    try:
        response = requests.post(f"{OLLAMA_URL}/chat", headers=headers, json=payload,stream=True,timeout=120)
        if response.status_code != 200:
            stop_event.set()
            loader.join()
            print(f"\r[ERROR] {response.status_code}: {response.text}")
            messages.pop()
            continue

    except requests.exceptions.ConnectionError:
        stop_event.set()
        loader.join()
        print("[ERROR Can't reach the Server, Check your Internet Connection]")
        messages.pop()
        continue
    except requests.exceptions.RequestException as e:
        stop_event.set()
        loader.join()
        print("[ERROR Failed Request : {e} ]")
        messages.pop()
        continue

    full_response = ""
    error_occured = False

    try:
        for line in response.iter_lines():
            if not line:
                continue
            # Stop animation on first chunk
            if not stop_event.is_set():
                stop_event.set()
                loader.join()
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "error" in chunk:
                print(f"\n[ERROR] {chunk['error']}")
                messages.pop()
                error_occurred = True
                break
            if chunk.get("done"):
                break
            token = chunk.get("message", {}).get("content", "")
            print(token, end="", flush=True)
            full_response += token

    finally: 
        if not stop_event.is_set():
            stop_event.set()
            loader.join()

    if not error_occured:
        messages.append({"role": "assistant", "content": full_response})

    print()