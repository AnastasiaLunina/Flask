from typing import Union
import pydantic
from flask import Flask, jsonify

app = Flask("app")


class HTTPError(Exception):
    def __init__(self, status_code: int, message: Union[str, list, dict]):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def handle_invalid_usage(error):
    response = jsonify({'message': error.message})
    response.status_code = error.status_code
    return response


class CreateAdModel(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.validator("title")
    def min_max_length(cls, value: str):
        if 1 > len(value) > 50:
            raise ValueError('Title should be from 1 to 50 characters')
        return value


def validate(unvalidated_data: dict, validation_model):
    try:
        return validation_model(**unvalidated_data).dict()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())
