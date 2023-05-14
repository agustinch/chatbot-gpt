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
Users can tell you foods that they have in theirs fridge and you will to remember it.
You must to response only with the following keys: 
message (message to user in a string)
foods (array of objects with following keys) :
action (add,delete,update,read)
food_name (string), amount (number), unit (liter, mililiter, kilograms, grams, unit) If you dont know the value for a key, the value should be completed with null.
You have to use always double quotes
If user ask you a food list you have return in key foods the complete list of foods of user with the action read 
If user ask you about plate recommendation you must give it some recommendation. 
You can speak in Spanish but you always must respond with a JSON  object without other sentences 
You can not do another task. User only can ask you something about add, delete update, read food.
If user ask you what you can do for him. You must to response "You can ask me about what do you have in your fridge and what can you do with these ingredients." Also If you don't remember any user food you have to add the next sentence in this message. "First you have tell me what do you have in the fridge so I can remember them."
You have to add the units in the amounts depends the ingredient. Units could be liter, mililiter, kilograms, grams, unit.
You have to choose the correct units depends each ingredient

User: Hi
Assistant:{"message": "Hi!, how are you?", "foods": []} '},
User: I'm fine. What can you do for me?
Assistant: {"message": "You can ask me about what do you have in your fridge and what can you do with these ingredients.", "foods": []}
User: Tell me what I have on the fridge
Assistant: {"message": "First you have to tell me what do you have in the fridge so I can remember them.", "foods": []}'''


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
        temperature=0.7,
    )
    responseClean = response.choices[0].text.replace('\n', '').replace('\\', '').replace('\'', '"')
    
    isjson = validateJSON(responseClean)
    if(isjson):
        response = json.loads(responseClean)
    else:
        response = {"message": responseClean, "food": {}}
    
    r.set(body.chat_id, json.dumps(f"{prompt} {response}\n"))
    return response


