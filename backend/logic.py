import speech_recognition as sr
import os
import webbrowser
import datetime
import time
import requests
import pywhatkit
import numpy as np
import json
from dotenv import load_dotenv
load_dotenv()

chatStr = ""
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash-lite"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

contacts = {
    "umair": {"name": "Umair", "number": "+923023763524"},
    "zain": {"name": "Zain", "number": "+923009733239"},
    "ahmad": {"name": "Ahmad", "number": "+923087134626"},
    "obaida": {"name": "Obaida", "number": "+923339659499"},
    "saad": {"name": "Saad", "number": "+923247702141"}
}
sites = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "wikipedia": "https://www.wikipedia.org",
}


def chat(query):
    global chatStr
    chatStr += f"User: {query}\nJarvis: "
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": query}]}]}

    response = requests.post(ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        chat_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        chatStr += chat_response + "\n"
        return chat_response
    return "Sorry, I couldn't process your request."


def ai(prompt):
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        text = f"Error: {response.status_code}\n{response.text}"

    if not os.path.exists("ai"):
        os.mkdir("ai")

    filename = f"ai/{''.join(prompt.lower().split(' using artificial intelligence')[0]).strip()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Gemini response for Prompt: {prompt}\n\n{text}")

    return text


def say(text):
    os.system(f'say "{text}"')


def handle_command(query):
    app, search = extract_open_command_info(query)
    if app in sites:
        if search:
            if app == "google":
                webbrowser.open(f"https://www.google.com/search?q={search}")
            elif app == "youtube":
                webbrowser.open(f"https://www.youtube.com/results?search_query={search}")
            elif app == "wikipedia":
                webbrowser.open(f"https://en.wikipedia.org/wiki/{search.replace(' ', '_')}")
            return f"Searching {app} for {search}..."
        else:
            webbrowser.open(sites[app])
            return f"Opening {app}..."

    if query.lower().startswith("play "):
        song_name = query[5:].strip()
        pywhatkit.playonyt(song_name)
        return f"Playing {song_name}..."

    elif "time" in query.lower():
        now = datetime.datetime.now()
        return f"The time is {now.strftime('%H')} hours and {now.strftime('%M')} minutes"

    elif "open " in query.lower():
        application = query.split("open ")[-1].strip().capitalize()
        os.system(f"open '/Applications/{application}.app'")
        return f"Opening {application}..."

    elif "message" in query.lower():
        name, message = extract_message_info(query)
        if name in contacts:
            number = contacts[name]["number"]
            webbrowser.open(f"https://wa.me/{number}?text={message}")
            return f"Opening chat with {contacts[name]['name']} and messaging: {message}"
        else:
            return "Contact not found."

    elif "using artificial intelligence" in query.lower():
        ai(query)
        return "Okay, I have done your task."

    elif "reset chat" in query.lower():
        global chatStr
        chatStr = ""
        return "I have reset the chat successfully."

    elif "jarvis" in query.lower():
        return chat(query + " in few lines.")

    return "Command not recognized."


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source)
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User Said: {query}")
            return query
        except sr.UnknownValueError:
            return "Sorry, I could not understand your voice."
        except Exception:
            return "Some Error Occurred. Sorry from Jarvis."


def extract_message_info(query):
    prompt = f"""
You are an assistant that extracts structured information from voice commands.

From the user's input:
"{query}"

Extract the name (receiver) and message content.

Return JSON ONLY in this format:
{{
  "name": "<name>",
  "message": "<message>"
}}
If unsure or missing parts, use:
{{"name": "", "message": ""}}
"""
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    for _ in range(3):
        try:
            response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                result = json.loads(result_text)
                return result.get("name", "").lower(), result.get("message", "")
        except Exception as e:
            time.sleep(1)

    return "", ""


def extract_open_command_info(query):
    prompt = f"""
You are an assistant that extracts structured info from voice commands to open apps or search online.

From the user's input:
"{query}"

Extract:
- "app": the name of the app or site to open (e.g. youtube, google, wikipedia)
- "search": what to search (optional)

Return JSON only in this format:
{{
  "app": "<app>",
  "search": "<search_query>"
}}

If nothing found, return:
{{"app": "", "search": ""}}
"""
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            return parsed.get("app", "").lower(), parsed.get("search", "")
    except Exception:
        pass

    return "", ""
