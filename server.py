from typing import Union
import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import (Column, DateTime, Integer, String, create_engine, func,)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


PG_DSN = 'postgresql://POSTGRES_USER:POSTGRES_PASSWORD@localhost:5432/POSTGRES_DB'
app = Flask("app")
engine = create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class AdModel(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String(255), index=True, nullable=False)


Base.metadata.create_all(engine)


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


class AdView(MethodView):
    def get(self, id_ad: int):
        with Session() as session:
            ad = session.query(AdModel).filter(AdModel.id == id_ad).first()
            if id_ad != AdModel.id:
                raise HTTPError(400, 'error')
            return jsonify({
                'id': ad.id,
                'title': ad.title,
                'created_at': ad.created_at,
                'description': ad.description,
                'owner': ad.owner,
            })

    def post(self):
        json_data = dict(request.json)
        try:
            json_data_validate = CreateAdModel(**json_data).dict()
        except pydantic.ValidationError as er:
            raise HTTPError(400, 'error')

        with Session() as session:
            ads = AdModel(**json_data_validate)
            session.add(ads)
            session.commit()
            return jsonify({
                'id': ads.id,
                'title': ads.title,
                'owner': ads.owner,
                'description': ads.description,
            })

    def delete(self, id_ad: str):
        try:
            with Session() as session:
                ad = session.query(AdModel).filter(AdModel.id == id_ad).first()
                session.delete(ad)
                session.commit()
                return jsonify({
                    'status': 'success'
                })
        except pydantic.ValidationError as er:
            raise HTTPError(400, 'error')


app.add_url_rule("/advertisements/<int:id_ad>/", view_func=AdView.as_view('advertisements_delete'),
                 methods=['DELETE', 'GET'])
app.add_url_rule("/advertisements", view_func=AdView.as_view('advertisements_create'), methods=['POST'])
