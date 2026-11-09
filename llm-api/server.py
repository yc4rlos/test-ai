from fastapi import FastAPI
from chat.chat import ask_gemini
from pydantic import BaseModel

class ChatRequestDto(BaseModel):
    message: str

app = FastAPI()

@app.get("/")
def hello_world():
    return {"Hello": "World"}

@app.post("/chat")
async def chat(request: ChatRequestDto):
    response = await ask_gemini(request.message)
    return {"response": response}
