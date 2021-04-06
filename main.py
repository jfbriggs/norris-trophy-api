import fastapi
from scripts.data_preprocess import generate_seasons, get_current_data

app = fastapi.FastAPI()


@app.get("/")
async def main() -> str:
    return "Welcome to the home of Norris Trophy predictions."


@app.get("/update")
async def update() -> dict:
    seasons = generate_seasons()
    current_year = seasons[-1][-4:]
    get_current_data(current_year)

    return {"message": f"Data updated for the {seasons[-1]} season."}