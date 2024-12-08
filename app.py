from flask import Flask, render_template, redirect, url_for, request, jsonify, Blueprint,flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models.usuario import Usuario
from models.heladeria import Heladeria
from models.ingredientes import Ingredientes
from models.productos import Productos
from models.productosingredientes import Productosingredientes
from models.ventas import Ventas
from funciones import conteo_calorias,validacion_sano, abastecer 
from models import db
from datetime import datetime
import requests
import os
from sqlalchemy import func
from flask import render_template, jsonify
from babel.numbers import format_currency



app = Flask(__name__, template_folder='views')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SECRET_KEY'] = os.urandom(24)

# Inicializar la base de datos
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/')
def index():
    heladeria = Heladeria.query.first()  
    
    return render_template('index.html', heladeria=heladeria)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Usuario.query.filter_by(username=username).first()
        if user and user.password == password:  
            login_user(user)
            return redirect(url_for('rutalogueada'))

        return "Username or Password is invalid"

    return render_template("login.html")

@app.route('/ventas/resumen', methods=['GET'])
def resumen_ventas():
    resumen = db.session.query(
        Productos.nombre,
        Ventas.fecha_venta.label('fecha'),
        func.sum(Ventas.cantidad_productos).label('cantidad_vendida'),
        func.sum(Ventas.cantidad_productos * Ventas.precio_producto).label('total_venta')
    ).join(Ventas, Ventas.id_producto == Productos.id_producto) \
    .group_by(Productos.id_producto, Ventas.fecha_venta).all()

    return render_template('ventas_resumen.html', resumen=resumen)

@app.route('/rutalogueada')
@login_required
def rutalogueada():

    productos = Productos.query.all()
    

    if current_user.is_admin: 
        return render_template("dashboardadmin.html", username=current_user.username, user=current_user, productos=productos)
    elif current_user.is_empleado:
        return render_template("dashboardempleado.html", username=current_user.username, user=current_user)
    else:

        return render_template("dashboardcliente.html", username=current_user.username, user=current_user, productos=productos)

    

@app.route('/noautorizado')
def noautorizado():
    return render_template('noautorizado.html')


@app.route('/productoslist')
@login_required
def productoslist():
    productos = Productos.query.all() 
    return render_template('productoslist.html', productos=productos)

@app.route('/productosadmin')
@login_required
def productosadmin():
    productosadmin = Productos.query.all() 
    return render_template('productosadmin.html', productosadmin=productosadmin)


@app.route('/productosempleado')
@login_required
def productosempleado():
    productosempleado = Productos.query.all() 
    return render_template('productosempleado.html', productosempleado=productosempleado)


@app.route('/productoscliente')
@login_required
def productoscliente():
    productoscliente = Productos.query.all() 
    return render_template('productoscliente.html', productoscliente=productoscliente)


@app.route('/ingredientesadmin')
@login_required
def ingredientesadmin():
    ingredientesadmin = Ingredientes.query.all() 
    return render_template('ingredientesadmin.html', ingredientesadmin=ingredientesadmin)


@app.route('/ingredientescliente')
@login_required
def ingredientescliente():
    ingredientescliente = Ingredientes.query.all() 
    return render_template('ingredientescliente.html', ingredientescliente=ingredientescliente)

@app.route('/ventas')
@login_required
def ventas():
    ventas = Ventas.query.all() 
    return render_template('ventas.html', ventas=ventas)


@app.route('/logout')
@login_required
def logout():
    logout_user()  
    return redirect(url_for('index'))

"""
if __name__ == '__main__':
    app.run(debug=True)
"""
#Consultar todos los productos
@app.route('/api/heladeria/productos', methods=['GET'])
@login_required
def get_productos():
    productos = Productos.query.all()  
    productos_list = [{
        "id_producto": producto.id_producto,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "tipo_vaso": producto.tipo_vaso,
        "volumen": producto.volumen,
        "tipo_producto": producto.tipo_producto
    } for producto in productos]

    return jsonify({"productos": productos_list})


#Consultar un producto según su ID
@app.route('/api/heladeria/productos/id_producto/<int:id_producto>', methods=['GET'])
@login_required
def get_producto_by_id(id_producto):
    producto = Productos.query.get(id_producto)  
    if producto:
        return jsonify({
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "tipo_vaso": producto.tipo_vaso,
            "volumen": producto.volumen,
            "tipo_producto": producto.tipo_producto
        })
    else:
        return jsonify({"message": "Producto no encontrado"}), 404


#Consultar un producto según su nombre
@app.route('/api/heladeria/productos/nombre/<string:nombre>', methods=['GET'])
@login_required
def get_producto_by_name(nombre):
    producto = Productos.query.filter(Productos.nombre.ilike(f'%{nombre.strip()}%')).first()  
    if producto:
        return jsonify({
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "tipo_vaso": producto.tipo_vaso,
            "volumen": producto.volumen,
            "tipo_producto": producto.tipo_producto
        })
    else:
        return jsonify({"message": "Producto no encontrado"}), 404



#Consultar las calorías de un producto según su ID
@app.route('/api/heladeria/productos/id_producto/<int:id_producto>/calorias', methods=['GET'])
@login_required
def get_calorias(id_producto):
    # Llamar a la función para calcular las calorías totales del producto
    calorias_totales = conteo_calorias(id_producto)
    
    if calorias_totales is not None:
        return jsonify({"calorias_totales": calorias_totales})
    else:
        return jsonify({"message": "Producto no encontrado"}), 404



#Consultar la rentabilidad de un producto según su ID
@app.route('/api/heladeria/productos/id_producto/<int:id_producto>/rentabilidad', methods=['GET'])
@login_required
def get_rentabilidad(id_producto):

    producto = Productos.query.get(id_producto)
    if producto:
        ingredientes_productos = Productosingredientes.query.filter_by(id_producto=id_producto).all()


        costo_produccion = 0
        for ingrediente_producto in ingredientes_productos:
            ingrediente = Ingredientes.query.get(ingrediente_producto.id_ingrediente)
            costo_produccion += ingrediente.precio  

        rentabilidad = 0
        if costo_produccion > 0:
            rentabilidad = ((producto.precio - costo_produccion) / costo_produccion) * 100
            rentabilidad = round(rentabilidad, 2)

        return jsonify({
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "costo_produccion": costo_produccion,
            "rentabilidad": rentabilidad
        })
    else:
        return jsonify({"message": "Producto no encontrado"}), 404


#Consultar el costo de producción de un producto según su ID
@app.route('/api/heladeria/productos/id_producto/<int:id_producto>/costo_produccion', methods=['GET'])
@login_required
def get_costo_produccion(id_producto):
    producto = Productos.query.get(id_producto)
    if producto:

        ingredientes_productos = Productosingredientes.query.filter_by(id_producto=id_producto).all()

        costo_produccion = 0
        for ingrediente_producto in ingredientes_productos:
            ingrediente = Ingredientes.query.get(ingrediente_producto.id_ingrediente)
            costo_produccion += ingrediente.precio  

        return jsonify({
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "costo_produccion": costo_produccion
        })
    else:
        return jsonify({"message": "Producto no encontrado"}), 404


#Consultar todos los Ingredientes
@app.route('/api/heladeria/ingredientes', methods=['GET'])
@login_required
def get_ingredientes():
    ingredientes = Ingredientes.query.all()  
    ingredientes_list = [{
        "id_ingrediente":ingrediente.id_ingrediente,
        "nombre":ingrediente.nombre,
        "precio":ingrediente.precio,
        "numero_calorias":ingrediente.numero_calorias,
        "es_vegetarianos":ingrediente.es_vegetarianos,
        "sabor":ingrediente.sabor,
        "tipo_ingrediente":ingrediente.tipo_ingrediente,
        "inventario":ingrediente.inventario,
    } for ingrediente in ingredientes]

    return jsonify({"ingredientes": ingredientes_list})


#Consultar un ingrediente según su ID
@app.route('/api/heladeria/ingredientes/id_ingrediente/<int:id_ingrediente>', methods=['GET'])
@login_required
def get_ingrediente_by_id(id_ingrediente):
    ingrediente = Ingredientes.query.get(id_ingrediente)  
    if ingrediente:
        return jsonify({
             "id_ingrediente":ingrediente.id_ingrediente,
             "nombre":ingrediente.nombre,
             "precio":ingrediente.precio,
             "numero_calorias":ingrediente.numero_calorias,
             "es_vegetarianos":ingrediente.es_vegetarianos,
             "sabor":ingrediente.sabor,
             "tipo_ingrediente":ingrediente.tipo_ingrediente,
             "inventario":ingrediente.inventario
        })
    else:
        return jsonify({"message": "Ingrediente no encontrado"}), 404
    

#Consultar un ingrediente según su nombre
@app.route('/api/heladeria/ingredientes/nombre/<string:nombre>', methods=['GET'])
@login_required
def get_ingrediente_by_name(nombre):
    ingrediente = Ingredientes.query.filter(Ingredientes.nombre.ilike(f'%{nombre.strip()}%')).first()  
    if ingrediente:
        return jsonify({
             "id_ingrediente": ingrediente.id_ingrediente,
             "nombre": ingrediente.nombre,
             "precio": ingrediente.precio,
             "numero_calorias": ingrediente.numero_calorias,
             "es_vegetarianos": ingrediente.es_vegetarianos,
             "sabor": ingrediente.sabor,
             "tipo_ingrediente": ingrediente.tipo_ingrediente,
             "inventario": ingrediente.inventario
        })
    else:
        return jsonify({"message": "Ingrediente no encontrado"}), 404


@app.route('/api/heladeria/ingredientes/nombre/<string:nombre>', methods=['GET'])
@login_required
def buscar_por_nombre(nombre):
    ingredientes = Ingredientes.query.filter(Ingredientes.nombre.ilike(f"%{nombre}%")).all()
    if ingredientes:
        return jsonify([ingrediente.to_dict() for ingrediente in ingredientes])
    else:
        return jsonify({"message": "Ingrediente no encontrado"}), 404

@app.route('/api/heladeria/ingredientes/id_ingrediente/<int:id_ingrediente>/sano', methods=['GET'])
@login_required
def es_ingrediente_sano(id_ingrediente):
    ingrediente = Ingredientes.query.get(id_ingrediente)
    
    if ingrediente:
        nombre = ingrediente.nombre
        precio = ingrediente.precio
        numero_calorias = ingrediente.numero_calorias
        es_vegetarianos = ingrediente.es_vegetarianos
        sabor = ingrediente.sabor
        tipo_ingrediente = ingrediente.tipo_ingrediente
        inventario = ingrediente.inventario
        
        es_sano = validacion_sano(numero_calorias, es_vegetarianos)

        return jsonify({
            "id_ingrediente": id_ingrediente,
            "nombre": nombre,
            "precio": precio,
            "numero_calorias": numero_calorias,
            "es_vegetariano": es_vegetarianos,
            "sabor": sabor,
            "tipo_ingrediente": tipo_ingrediente,
            "inventario": inventario,
            "es_sano": es_sano
        })
    else:
        return jsonify({"message": "Ingrediente no encontrado"}), 404


@app.route('/api/heladeria/ingredientes/nombre/<string:nombre>/sano', methods=['GET'])
@login_required
def es_ingrediente_sano_nombre(id_ingrediente):
    ingrediente = Ingredientes.query.get(id_ingrediente)
    
    if ingrediente:
        nombre = ingrediente.nombre
        precio = ingrediente.precio
        numero_calorias = ingrediente.numero_calorias
        es_vegetarianos = ingrediente.es_vegetarianos
        sabor = ingrediente.sabor
        tipo_ingrediente = ingrediente.tipo_ingrediente
        inventario = ingrediente.inventario
        
        es_sano = validacion_sano(numero_calorias, es_vegetarianos)

        return jsonify({
            "id_ingrediente": id_ingrediente,
            "nombre": nombre,
            "precio": precio,
            "numero_calorias": numero_calorias,
            "es_vegetariano": es_vegetarianos,
            "sabor": sabor,
            "tipo_ingrediente": tipo_ingrediente,
            "inventario": inventario,
            "es_sano": es_sano
        })
    else:
        return jsonify({"message": "Ingrediente no encontrado"}), 404



#Reabastecer un producto según su ID
@app.route('/api/heladeria/ingredientes/id_ingrediente/<int:id_ingrediente>/abastecer', methods=['POST'])
@login_required
def abastecer_ingrediente(id_ingrediente):

    ingrediente = Ingredientes.query.get(id_ingrediente)
    
    if not ingrediente:
        return jsonify({"message": "Ingrediente no encontrado"}), 404

    ingrediente.inventario = abastecer(ingrediente.tipo_ingrediente, ingrediente.inventario)
    
    db.session.commit()
    
    return jsonify({"message": "Ingrediente abastecido con éxito", "inventario": ingrediente.inventario}), 200


@app.route('/api/heladeria/productos/id_producto/<int:id_producto>/vender', methods=['POST'])
@login_required
def vender_producto(id_producto):
    producto = Productos.query.get(id_producto)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    ingredientes_productos = Productosingredientes.query.filter_by(id_producto=id_producto).all()
    
    disponibilidad = True
    for ingrediente_producto in ingredientes_productos:
        ingrediente = Ingredientes.query.get(ingrediente_producto.id_ingrediente)
        
        if not ingrediente:
            disponibilidad = False
            break
        
        cantidad_requerida = 1 if ingrediente.tipo_ingrediente == 'Complemento' else 0.2
        
        if ingrediente.inventario < cantidad_requerida:
            disponibilidad = False
            break
    
    if not disponibilidad:
        return jsonify({"message": "No hay suficiente inventario para este producto."}), 400


    for ingrediente_producto in ingredientes_productos:
        ingrediente = Ingredientes.query.get(ingrediente_producto.id_ingrediente)
        cantidad_requerida = 1 if ingrediente.tipo_ingrediente == 'Complemento' else 0.2
        ingrediente.inventario -= cantidad_requerida  


    precio_producto = producto.precio  

    nueva_venta = Ventas(
        id_heladeria=1, 
        id_producto=id_producto,
        cantidad_productos=1,  
        precio_producto=precio_producto,
        fecha_venta = datetime.now().date()
    )
    
    db.session.add(nueva_venta)
    db.session.commit()

    return jsonify({
        "message": "Producto vendido con éxito",
        "producto": producto.nombre,
        "precio": precio_producto,
        "inventario_actualizado": {ingrediente.nombre: round(ingrediente.inventario,2) for ingrediente in Ingredientes.query.all()}
    }), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 

        if not Usuario.query.first():   
            usuarios_iniciales = [
                             Usuario(Id_usuario = 1, username="diana", password="123", is_admin=True, is_empleado=True),
                             Usuario(Id_usuario = 2, username="lina", password="123", is_admin=False, is_empleado=True),
                             Usuario(Id_usuario = 3, username="marcela", password="123", is_admin=False, is_empleado=False)
                         ]
            db.session.add_all(usuarios_iniciales)  
            db.session.commit()           
            

        
        if not Heladeria.query.first():
            heladeria_iniciales = [
                                    Heladeria(id_heladeria=1, nombre="PYTHON ICE CREAM", direccion="Calle 123 # 00-00", telefono="9999999")
                                  ]
            db.session.add_all(heladeria_iniciales)
            db.session.commit()


        if not Productos.query.first():
            productos_iniciales = [
                                    Productos(id_producto=1, nombre="Samurai de fresas", precio=4900, tipo_vaso="Vaso Ecologico", volumen=52.00, tipo_producto="Copa"),
                                    Productos(id_producto=2, nombre="Samurai de mandarinas", precio=2500, tipo_vaso="Vaso Ecologico", volumen=80.00, tipo_producto="Copa"),
                                    Productos(id_producto=3, nombre="Malteda chocoespacial", precio=11000, tipo_vaso="Vaso Plastico", volumen=100.00, tipo_producto="Malteada"),
                                    Productos(id_producto=4, nombre="Cupihelado", precio=3200, tipo_vaso="Vaso Ecologico", volumen=52.00, tipo_producto="Copa")
                                  ]
            db.session.add_all(productos_iniciales)
            db.session.commit()



        if not Ingredientes.query.first():
            ingredientes_iniciales = [
                                        #Bases
                                        Ingredientes(id_ingrediente=1, nombre="Helado de Fresa", precio=1200, numero_calorias=300,es_vegetarianos=1,sabor="Fresa", tipo_ingrediente= "Base",inventario=50.0),
                                        Ingredientes(id_ingrediente=2, nombre="Helado de Mandarina", precio=1200, numero_calorias=280,es_vegetarianos=1,sabor="Mandarina", tipo_ingrediente= "Base",inventario=50.0),
                                        Ingredientes(id_ingrediente=3, nombre="Helado de Chocolate", precio=1500, numero_calorias=400,es_vegetarianos=0,sabor="Chocolate", tipo_ingrediente= "Base",inventario=50.0),
                                        Ingredientes(id_ingrediente=4, nombre="Helado de Vainilla", precio=1200, numero_calorias=300,es_vegetarianos=0,sabor="Vainilla", tipo_ingrediente= "Base",inventario=50.0),
                
                                        #Complementos
                                        Ingredientes(id_ingrediente=5, nombre="Chispas de chocolate", precio=500, numero_calorias=500,es_vegetarianos=0,sabor="", tipo_ingrediente= "Complemento",inventario=50.0),
                                        Ingredientes(id_ingrediente=6, nombre="Mani Japonés", precio=900, numero_calorias=200,es_vegetarianos=1,sabor="", tipo_ingrediente= "Complemento",inventario=50.0),
                                        Ingredientes(id_ingrediente=7, nombre="Chantilli", precio=800, numero_calorias=300,es_vegetarianos=0,sabor="", tipo_ingrediente= "Complemento",inventario=50.0),
                                        Ingredientes(id_ingrediente=8, nombre="Galletas", precio=1000, numero_calorias=430,es_vegetarianos=0,sabor="", tipo_ingrediente= "Complemento",inventario=50.0),
                                        Ingredientes(id_ingrediente=9, nombre="Leche", precio=700, numero_calorias=50,es_vegetarianos=0,sabor="", tipo_ingrediente= "Complemento",inventario=50.0),
                                        Ingredientes(id_ingrediente=10, nombre="Trozos Mandarina", precio=200, numero_calorias=10,es_vegetarianos=1,sabor="", tipo_ingrediente= "Complemento",inventario=50.0),
                                        Ingredientes(id_ingrediente=11, nombre="Trozos Cereza", precio=200, numero_calorias=10,es_vegetarianos=1,sabor="", tipo_ingrediente= "Complemento",inventario=50.0)
                                     ]
            db.session.add_all(ingredientes_iniciales)
            db.session.commit()




        # Insertar datos iniciales si no existen en la tabla Productosingredientes
        if not Productosingredientes.query.first():
            productosingredientes_iniciales = [
                                                #Producto 1
                                                Productosingredientes(id_heladeria=1,id_producto=1,id_ingrediente=1), 
                                                Productosingredientes(id_heladeria=1,id_producto=1,id_ingrediente=8), 
                                                Productosingredientes(id_heladeria=1,id_producto=1,id_ingrediente=9), 

                                                #Producto 2
                                                Productosingredientes(id_heladeria=1,id_producto=2,id_ingrediente=2),
                                                Productosingredientes(id_heladeria=1,id_producto=2,id_ingrediente=7),
                                                Productosingredientes(id_heladeria=1,id_producto=2,id_ingrediente=10),


                                                #Producto 3
                                                Productosingredientes(id_heladeria=1,id_producto=3,id_ingrediente=3),
                                                Productosingredientes(id_heladeria=1,id_producto=3,id_ingrediente=9),
                                                Productosingredientes(id_heladeria=1,id_producto=3,id_ingrediente=5),

                                                #Producto 4
                                                Productosingredientes(id_heladeria=1,id_producto=4,id_ingrediente=4),
                                                Productosingredientes(id_heladeria=1,id_producto=4,id_ingrediente=11),
                                                Productosingredientes(id_heladeria=1,id_producto=4,id_ingrediente=6)
                                              ]
            db.session.add_all(productosingredientes_iniciales)
            db.session.commit()


    app.run(debug=True)
		