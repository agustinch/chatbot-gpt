from fastapi import FastAPI
import os
import openai
from dotenv import load_dotenv, find_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import json
from dotenv import load_dotenv

load_dotenv()

OPENAPI_KEY = os.getenv('OPENAPI_KEY')

def convert_to_object(text):
    obj = {}
    pairs = text.split(' ')
    for pair in pairs:
        key_value = pair.split(':')
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip()
            if value == 'null':
                value = None
            obj[key] = value
    return obj

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        print(err)
        return False
    return True

class ChatPrompt(BaseModel):
    prompt: str
    chat_id: int

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

openai.api_key  = OPENAPI_KEY

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

default_text = '''You are an assistant in a food app.
Users can tell you the food they have in their fridge and you will remember it.
You must respond only with the following keys:
message (message to the user in a string)
food (array of objects with the following keys):
action (add, delete, update, read)
food_name(string), quantity(number), unit(liter, milliliter, kilograms, grams, unit) If you do not know the value of a key, the value must be filled with null.
You should always use double quotes in json keys
If the user asks you for a list of foods, you should return in foods key the user's full list of foods with the read action
If the user asks you about the recommendation of the board, you must give him some recommendation.
You can speak in Spanish but you must always reply with a JSON object without other sentences
You can't do another task. The user can only ask you something about add, delete update, read feed.
If the user asks you what you can do for him. You should answer "You can ask me what you have in your fridge and what you can do with these ingredients." Also, if you don't remember any user feed, you should add the following sentence in this message. "First you have to tell me what you have in the fridge so I can remember them."
You have to add the units in the quantities depending on the ingredient. Units can be liters, milliliters, kilograms, grams, unit.
You have to choose the correct units depends on each ingredient

User: Hi
Assistant:{"message": "Hi!, how are you?", "foods": []} '},
User: I'm fine. What can you do for me?
Assistant: {"message": "You can ask me about what do you have in your fridge and what can you do with these ingredients.", "foods": []}
User: Tell me what I have on the fridge
Assistant: {"message": "First you have to tell me what do you have in the fridge so I can remember them.", "foods": []} '''


@app.post("/chatbot")
async def chatbot_endpoint(body: ChatPrompt):

    history_chat = r.get(body.chat_id)
    if(history_chat):
        text = json.loads(history_chat)
    else:
        text = default_text

    prompt = f"{text}\nUser: {body.prompt}\nAssistant:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0,
    )
    responseClean = response.choices[0].text.replace('\n', '').replace("'", '"')
    print(response)
    isjson = validateJSON(responseClean)
    if(isjson):
        response = json.loads(responseClean)
    else:
        response = {"message": responseClean, "foods": []}
    
    
    r.set(body.chat_id, json.dumps(f"{prompt} {response}\n"))
    return response


