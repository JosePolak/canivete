from datetime import datetime

from extensions import db


class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moeda_origem = db.Column(db.String(50), nullable=False)
    moeda_destino = db.Column(db.String(50), nullable=False)
    valor_entrada = db.Column(db.Float, nullable=False)
    valor_saida = db.Column(db.Float, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now)
