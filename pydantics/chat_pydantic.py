from pydantic import Field

class ChatPydantic:
    from pydantic import BaseModel

    class ChatRequest(BaseModel):
        prompt: str = Field(..., example="Hello, ChatGPT!")

    class ChatResponse(BaseModel):
        response: str