from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.current_data import get_current_data
from src.data_preprocess import generate_seasons, merge_process
from src.model import NorrisModel
import uvicorn
from typing import Optional


app = FastAPI()

origins = ["http://localhost:8080", "http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup():
    print("Activating server and updating current season data...")
    seasons = generate_seasons()
    current_year = seasons[-1][-4:]
    get_current_data(current_year)
    print("Current data updated.  Processing data and training model.")

    train_data, curr_data = merge_process('nhl_data')
    est = NorrisModel()
    est.fit(train_data)

    print("Model trained.  Ready for prediction requests.")
    return est, curr_data


@app.get("/")
async def main() -> str:
    return "Welcome to the home of Norris Trophy predictions."


@app.get("/update")
async def update() -> dict:
    global model
    global current_data
    model, current_data = setup()

    return {"message": "Data updated."}


@app.get("/predict")
async def make_predictions(refresh: Optional[bool] = False):
    if refresh:
        await update()

    top_ten = model.predict(current_data)

    results = {}

    for i in range(10):
        results[i + 1] = top_ten[i]

    return {"results": results}


model, current_data = setup()

if __name__ == "__main__":
    uvicorn.run(app, port=8500)
