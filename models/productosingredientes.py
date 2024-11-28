


from sqlalchemy import ForeignKey
from models import db  
from sqlalchemy.orm import relationship
from models.heladeria import Heladeria
from models.productos import Productos
from models.ingredientes import Ingredientes


class Productosingredientes(db.Model):
    __tablename__ = 'productosingredientes'

    id = db.Column(db.Integer, primary_key=True)
    id_heladeria = db.Column(db.Integer, ForeignKey('heladeria.id_heladeria'))
    id_producto = db.Column(db.Integer, ForeignKey('productos.id_producto'))
    id_ingrediente = db.Column(db.Integer, ForeignKey('ingredientes.id_ingrediente'))

    
    heladeria = relationship("Heladeria", backref="productos_ingredientes")
    producto = relationship("Productos", backref="productosingredientes")
    ingrediente = relationship("Ingredientes", backref="productosingredientes")


    def __repr__(self):
        return f"<Productosingredientes {self.id}>"