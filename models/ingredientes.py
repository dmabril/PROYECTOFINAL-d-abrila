

from models import db  
from sqlalchemy.orm import relationship


class Ingredientes(db.Model):
    __tablename__ = 'ingredientes'

    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    numero_calorias = db.Column(db.Integer, nullable=False)
    es_vegetarianos = db.Column(db.Boolean, nullable=False)
    #es_sano = db.Column(db.Boolean, nullable=False)
    sabor = db.Column(db.String(50), nullable=False) 
    tipo_ingrediente =  db.Column(db.String(50), nullable=False)
    inventario = db.Column(db.Float, nullable=False)


    def __repr__(self):
        return f"<Ingrediente {self.nombre}>"
    

