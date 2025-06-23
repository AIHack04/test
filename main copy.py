from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # หรือระบุ ["http://127.0.0.1:5500"] ก็ได้
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "api-key"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_page():
    with open("chat_ui.html", encoding="utf-8") as f:
        return f.read()
    
API_URL = "<url-openai>"
API_KEY = "<api-key>"

class UserMessage(BaseModel):
    content: str

@app.post("/ask-ai")
async def ask_ai(msg: UserMessage):
    
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    payload = {
        "messages": [
            { "role": "user", "content": msg.content }
        ],
        "temperature": 0.5,
        "max_tokens": 1000,
        "topProbablities":0.80,
        "pastMessagesToInclude":10,
        
        "dataSources": [
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": "<url-aisearch>",
                    "key": "",
                    "indexName": "<key-aisearch>",
                    
                    "fieldsMapping": {
                        "id": "id",
                        "content" : "content"
                    },

                    "topNDocuments": 3,
                    "queryType": "simple"
                    
                }
            }
        ]

    }

    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            
            # ดึง content ตอบกลับจาก AI
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return { "response": content }
    except httpx.HTTPStatusError as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code,
            "details": e.response.text
        }
    except Exception as e:
        return {
            "error": str(e)
        }
