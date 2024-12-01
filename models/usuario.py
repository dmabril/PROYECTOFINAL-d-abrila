

from flask_login import UserMixin
from models import db 



class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    
    Id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    is_empleado = db.Column(db.Boolean, default=False)
    


    def get_id(self):
        return str(self.Id_usuario) 