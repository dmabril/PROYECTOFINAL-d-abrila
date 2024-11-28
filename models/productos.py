


from models import db
from sqlalchemy.orm import relationship



class Productos(db.Model):
    __tablename__ = 'productos'

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    tipo_vaso = db.Column(db.String(50), nullable=False)
    volumen = db.Column(db.Float, nullable=False)
    tipo_producto =  db.Column(db.String(50), nullable=False)

    

   

    def __repr__(self):
        return f"<Productos {self.nombre}>"