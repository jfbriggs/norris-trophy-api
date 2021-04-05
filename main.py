import fastapi

app = fastapi.FastAPI()


@app.get("/")
async def main():
    return {"message": "Hello, world!"}
