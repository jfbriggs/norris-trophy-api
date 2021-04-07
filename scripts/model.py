import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from typing import List


class NorrisModel:
    def __init__(self, estimator=GradientBoostingRegressor) -> None:
        self.estimator = estimator()

    def fit(self, data: pd.DataFrame) -> None:
        # separate features from target variable in train data
        X_train, y_train = data.drop(["norris_point_pct", "name", "season"], axis=1), data["norris_point_pct"]

        # fit instantiated estimator on features and target in train data
        self.estimator.fit(X_train, y_train)

    def predict(self, data: pd.DataFrame) -> List[dict]:
        predictions = self.estimator.predict(data)

        # add prediction values as column, and display sorted descending
        data["predicted_point_pct"] = predictions
        top_ten = data[["name", "predicted_point_pct"]].sort_values(by="predicted_point_pct", ascending=False).head(10)

        # convert top 10 results to a list of dicts
        top_ten_list = top_ten.to_dict("records")

        return top_ten_list
