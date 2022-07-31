import pydantic
from flask import jsonify, request
from flask.views import MethodView
from models import Session, AdModel
from server import HTTPError, CreateAdModel


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
