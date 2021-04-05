import fastapi

app = fastapi.FastAPI()


@app.get("/")
async def main() -> dict:
    return {"message": "Hello, world!"}
