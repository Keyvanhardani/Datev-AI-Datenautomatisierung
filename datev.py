import os
import base64
import requests
import re
import time
import json
from openai import OpenAI

# OpenAI API Key
api_key = "sk-XXX"

client = OpenAI(api_key=api_key)

# Ordner mit den JPG-Dateien
source_folder = "./path_to_files"

max_retries = 3  # Maximale Anzahl der Wiederholungsversuche
max_restarts = 5  # Maximale Anzahl der Neustarts des Skripts

def main_process():
    for restart_count in range(max_restarts):
        try:
            process_files()
            break  # Wenn alles erfolgreich ist, beende die Schleife
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Dateien: {e}. Neustart {restart_count + 1} von {max_restarts}.")
            if restart_count == max_restarts - 1:
                print("Maximale Anzahl von Neustarts erreicht. Beende Skript.")
                break

def process_files():
    for file in os.listdir(source_folder):
        if file.endswith(".jpg"):
            image_path = os.path.join(source_folder, file)
            base64_image = encode_image(image_path)
            vision_response = query_vision_api(base64_image)
            if vision_response:
                process_vision_response(image_path, vision_response)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def query_vision_api(image_base64, retry=0):
    if retry >= max_retries:
        print("Maximale Anzahl von Wiederholungsversuchen erreicht.")
        return None
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What’s the date on this image and what is it about?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Anfrage an die API: {e}. Versuch {retry+1} von {max_retries}.")
        return query_vision_api(image_base64, retry+1)

def rename_file(original_path, date, invoicetyp, company_name, target_folder="./path_to_renamed_files"):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    new_name = f"{date}_{company_name}_{invoicetyp}.jpg"
    new_path = os.path.join(target_folder, new_name)
    os.rename(original_path, new_path)

    return json.dumps({"status": "success", "message": f"Renamed '{original_path}' to '{new_path}'"})


def process_vision_response(image_path, vision_response):
    #print("Empfangene Daten: ", image_path, vision_response)
    message_content = f"Rename the file at original_path= '{image_path}' to include the date 'date' and invoicetyp 'invoicetyp', and company_name 'company_name' here is the content: '{vision_response}'"

    messages = [
        {"role": "user", "content": message_content}
    ]

    #print(message_content)

    # Extrahiere das Datum und den Typ aus der Vision-Antwort
    tools = [
        {
            "type": "function",
            "function": {
                "name": "rename_file",
                "description": "Rename a file based on the date and invoice type extracted from the image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "original_path": 
                        {"type": "string",
                            "description": "The original file path of the image to be renamed.",
                        },

                        "date": 
                        {"type": "string",
                            "description": "The date extracted from the image, used for renaming the file. take the highters value, please use date format like: 25.02.2023 - Please provide the output in German.",
                        },
                        
                        "invoicetyp": 
                        {"type": "string",
                            "description": "The type of document (e.g., invoice, receipt) extracted from the image, used for renaming the file. Please provide the output in German.",

                        },
                        "company_name": 
                        {"type": "string",
                            "description": "The company name of the document (e.g., apple, MVV etc..) extracted from the image, used for renaming the file. Please provide the output in German.",

                        }
                    },
                    "required": ["original_path", "date", "invoicetyp", "company_name"]
                }
            }
        }
    ]
    
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    
    tool_calls = response_message.tool_calls

    if tool_calls:

        available_functions = {
            "rename_file": rename_file,
        }
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                original_path=function_args['original_path'],
                date=function_args['date'],
                invoicetyp=function_args['invoicetyp'],
                company_name=function_args['company_name'],
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
            
            print("Endgültige Antwort: ", response_message)

            return response_message
            
            
if __name__ == "__main__":
    main_process()