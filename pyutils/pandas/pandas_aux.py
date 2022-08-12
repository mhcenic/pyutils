from typing import Union

import pandas as pd
from pandas import DataFrame


class PandasModel:

    def __init__(self, *columns: str):
        self._data_dict = {column: [] for column in columns}

    @property
    def as_data_frame(self) -> DataFrame:
        return pd.DataFrame(self._data_dict)

    def add(self, *values: Union[str, float, int, bool]):
        assert len(self._data_dict) == len(values), "Incorrect number of values to add."

        for column, value in zip(self._data_dict, values):
            self._data_dict[column].append(value)
