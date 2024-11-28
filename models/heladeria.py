

from models import db
from sqlalchemy.orm import relationship



class Heladeria(db.Model):
    __tablename__ = 'heladeria'

    id_heladeria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)


    def __repr__(self):
        return f"<Heladeria {self.nombre}>"