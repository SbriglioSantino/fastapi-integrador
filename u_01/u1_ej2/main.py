from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/items/me")
async def read_user_me():
    return {"user": "current"}
