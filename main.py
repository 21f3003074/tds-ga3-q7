"""
Q12: Function Calling - FastAPI endpoint
GET /execute?q=... that maps natural language queries to function calls.
Uses AI Pipe with OpenAI for function calling.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_PIPE_TOKEN = os.getenv("AI_PIPE_TOKEN")

# Define the tools/functions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_status",
            "description": "Get the status of an IT support ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer", "description": "The ticket ID number"}
                },
                "required": ["ticket_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a meeting in a specific room",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Meeting date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Meeting time in HH:MM format"},
                    "meeting_room": {"type": "string", "description": "Name of the meeting room"}
                },
                "required": ["date", "time", "meeting_room"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_balance",
            "description": "Get the expense reimbursement balance for an employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "The employee ID number"}
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_performance_bonus",
            "description": "Calculate performance bonus for an employee for a specific year",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "The employee ID number"},
                    "current_year": {"type": "integer", "description": "The year for bonus calculation"}
                },
                "required": ["employee_id", "current_year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_office_issue",
            "description": "Report an office issue for a department",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_code": {"type": "integer", "description": "The issue code number"},
                    "department": {"type": "string", "description": "The department name"}
                },
                "required": ["issue_code", "department"]
            }
        }
    }
]


@app.get("/execute")
async def execute(q: str = Query(...)):
    """Map a natural language query to a function call using LLM."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://aipipe.org/openrouter/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {AI_PIPE_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4.1-nano",
                "messages": [
                    {"role": "system", "content": "You are a function routing assistant. Map the user query to the appropriate function call."},
                    {"role": "user", "content": q}
                ],
                "tools": TOOLS,
                "tool_choice": "required",
            },
            timeout=30.0,
        )

    result = response.json()
    tool_call = result["choices"][0]["message"]["tool_calls"][0]["function"]

    return {
        "name": tool_call["name"],
        "arguments": tool_call["arguments"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
