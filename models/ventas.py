


from models import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey



class Ventas(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    id_heladeria = db.Column(db.Integer, ForeignKey('heladeria.id_heladeria'))
    id_producto = db.Column(db.Integer, ForeignKey('productos.id_producto'))
    cantidad_productos = db.Column(db.Integer, nullable=False)
    precio_producto = db.Column(db.Float, nullable=False)
    fecha_venta = db.Column(db.Date, nullable=False)

    heladeria = relationship("Heladeria", backref="ventas")
    producto = relationship("Productos", backref="ventas")
    
    def __repr__(self):
        return f"<Ventas {self.id}>"
    
