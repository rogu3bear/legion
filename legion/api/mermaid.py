from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

app = FastAPI()

# Placeholder functions

def get_message_embedding(content):  # TODO
    pass

def retrieve_memories(embedding):    # TODO
    pass

def summarize_memories(memories):    # TODO
    pass

def build_prompt(sys, summary, hist, user):  # TODO
    pass

def call_llm(messages):             # TODO
    pass

def post_to_discord(reply):         # TODO
    pass

def store_memories(data):           # TODO
    pass

@app.post("/message")
def post_message(content: str = Body(..., embed=True)):
    # Stub: Accepts a message, does nothing
    return JSONResponse({"status": "received", "content": content})

@app.get("/health")
def get_health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("legion.api.mermaid:app", host="127.0.0.1", port=8000, reload=True) 