import os
from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap5
from werkzeug.utils import secure_filename
from app import config
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

# --- CONFIGURACIÓN DE LA APP ---
app = Flask(__name__)
app.config.from_object(config)
bootstrap = Bootstrap5(app)

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- BASE DE DATOS Y MODELOS ---
from app.models import Articulos, Categorias, Usuarios, db
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

# --- PUENTE PARA EL HTML (Evita el error is_admin is undefined) ---
@app.context_processor
def inject_permissions():
    def is_admin():
        return current_user.is_authenticated and current_user.admin
    return dict(is_admin=is_admin)


# Importar rutas aquí

@app.route('/')
@app.route('/categoria/<id>')
def inicio(id='0'):
    categoria = Categorias.query.get(id)
    if id=='0':
        articulos=Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(categoria_id=id)
    categorias = Categorias.query.all()
    return render_template('inicio.html', articulos = articulos, categorias=categorias, categoria=categoria)
@app.route('/categorias')
def categorias():
    categorias = Categorias.query.all()
    return render_template('categorias.html', categorias=categorias)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',error="Pagina no encontrada....  :)"), 404

@app.route('/articulo/new', methods=['GET','POST'])
def articulos_new():

    """ if not is_admin():
        abort(404) """
    
    if not current_user.is_admin():
        abort(404)
    
    from app.form import formArticulo
    form=formArticulo()
    categorias = [(c.id, c.nombre) for c in Categorias.query.all()[0:]]
    form.categoria_id.choices = categorias
    if form.validate_on_submit():
        try:
            f=form.imagen.data
            nombre_fichero = secure_filename(f.filename)
            f.save(app.root_path + "/static/img/" + nombre_fichero)
        except :
            nombre_fichero = ""
        art = Articulos()
        form.populate_obj(art)
        art.image= nombre_fichero
        db.session.add(art)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template('articulos_new.html', form=form)

@app.route('/categorias/new', methods=['GET','POST'])
def categorias_new():
    """ if not is_admin():
        abort(404) """
    
    if not current_user.is_admin():
        abort(404)
    

    from app.form import formCategoria
    form=formCategoria()
    if form.validate_on_submit():
        cat = Categorias()
        form.populate_obj(cat)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('categorias'))
    else:
        return render_template('categorias_new.html', form=form)
    


@app.route('/articulos/<id>/edit', methods=["get","post"])
def articulos_edit(id):
    """ if not is_admin():
        abort(404) """
    if not current_user.is_admin():
        abort(404)
    

    from app.form import formArticulo
    art=Articulos.query.get(id)
    if art is None:
        abort(404)
    
    form=formArticulo(obj=art)
    categorias=[(c.id, c.nombre) for c in Categorias.query.all()[0:]]
    form.categoria_id.choices = categorias
    
    if form.validate_on_submit():
        if form.imagen.data: # Borramos la imagen anterior si hemos subido una nueva
            if art.image:
                os.remove(app.root_path+"/static/img/"+art.image)
            try:
                f = form.imagen.data
                nombre_fichero=secure_filename(f.filename)
                f.save(app.root_path+"/static/img/"+nombre_fichero)
            except:
                nombre_fichero=""
        else:
            nombre_fichero=art.image
            
        form.populate_obj(art)
        art.image=nombre_fichero
        db.session.commit()
        return redirect(url_for("inicio"))
        
    return render_template("articulos_new.html",form=form)

@app.route('/articulos/<id>/delete', methods=["post","get"])
def articulos_delete(id):
    from app.form import formSINO
    art=Articulos.query.get(id)
    if art is None:
        abort(404)
    form=formSINO()
    if form.validate_on_submit():
        if form.si.data:
            if art.image!="":
                os.remove(app.root_path+"/static/img/"+ art.image)
            db.session.delete(art)
            db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_delete.html", form=form, art=art)


@app.route('/categorias/<id>/delete', methods=["post","get"])
def categorias_delete(id):
    """ if not is_admin():
        abort(404) """
    if not current_user.is_admin():
        abort(404)

    from app.form import formSINO
    cat=Categorias.query.get(id)
    if cat is None:
        abort(404)
    form=formSINO()
    if form.validate_on_submit():
        if form.si.data:
            db.session.delete(cat)
            db.session.commit()
        return redirect(url_for("categorias"))
    return render_template("categorias_delete.html", form=form, cat=cat)

@app.route('/categorias/<id>/edit', methods=["get","post"])
def categorias_edit(id):
    """ if not is_admin():
        abort(404) """
    
    if not current_user.is_admin():
        abort(404)
    

    from app.form import formCategoria
    cat=Categorias.query.get(id)
    if cat is None:
        abort(404)
    
    form=formCategoria(request.form,obj=cat)
    
    if form.validate_on_submit():
        form.populate_obj(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
        
    return render_template("categorias_new.html",form=form)

@app.route('/login', methods=["get","post"])
def login():
    """ if is_login():
        return redirect(url_for('inicio')) """
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    from app.form import loginForm
    form=loginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(username=form.username.data).first()
        if user!=None and user.verify_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('inicio'))
        form.username.errors.append("Usuario o contraseña incorrectos")
    return render_template("login.html", form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))


@app.route('/registro', methods=["get","post"])
def registro():
    """ if is_login():
        return redirect(url_for('inicio')) """
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    
    from app.form import formUsuario
    form=formUsuario()
    if form.validate_on_submit():
        existe_usuario = Usuarios.query.filter_by(username=form.username.data).first()
        if existe_usuario ==None:
            user = Usuarios()
            form.populate_obj(user)
            user.admin=False
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('inicio'))
        form.username.errors.append("El nombre de usuario ya existe")
    return render_template("usuarios_new.html", form=form)

@app.route('/perfil/<username>',methods=["get","post"])
def perfil(username):
    """ if not is_login():
        return redirect(url_for('login')) """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    from app.form import formUsuario
    user = Usuarios.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form=formUsuario(request.form,obj=user)
    del form.password
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("usuarios_new.html", form=form, perfil=True)

@app.route('/changepassword/<username>',methods=["get","post"])
@login_required
def changepassword(username):
    """ if not is_login():
        return redirect(url_for('login')) """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    from app.form import formChangePassword
    user = Usuarios.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form=formChangePassword()
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("changepassword.html", form=form)

""" 
@app.context_processor
def inject_permissions():
    return dict(is_admin=is_admin(), is_login=is_login()) """


import json 
from flask import make_response
from app.form import formCarrito
@app.route('/carrito/add/<id>',methods=['get','post'])
@login_required
def carrito_add(id):
    art=Articulos.query.get(id)
    form=formCarrito()
    form.id.data=id
    if form.validate_on_submit():
        if art.stock>=int(form.cantidad.data):
            try:
                datos=json.loads(request.cookies.get(str(current_user.id)))
            except: 
                datos = []
            actualizar = False
            for dato in datos:
                if dato["id"]==id:
                    dato["cantidad"]=form.cantidad.data
                    actualizar = True
            if not actualizar:
                datos.append({"id":form.id.data,"cantidad":form.cantidad.data})
            resp = make_response(redirect(url_for('inicio')))
            resp.set_cookie(str(current_user.id),json.dumps(datos))
            return resp
        form.cantidad.errors.append("No hay articulos suficentes")
    return render_template("carrito_add.html",form=form, art=art)

@app.route('/carrito')
@login_required
def carrito():
    try:
        datos=json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos=[]
    articulos=[]
    cantidades=[]

    total=0
    for articulo in datos:
        articulos.append(Articulos.query.get(articulo["id"]))
        cantidades.append(articulo["cantidad"])
        total=total+Articulos.query.get(articulo["id"]).precio_final()*articulo["cantidad"]
    articulos=zip(articulos,cantidades)

    return render_template("carrito.html",articulos=articulos,total=total)

@app.context_processor
def contar_carrito():
    if not current_user.is_authenticated:
        return {'num_articulos':0}
    if request.cookies.get(str(current_user.id)) is None:
        return {'num_articulos':0}
    else:
        datos=json.loads(request.cookies.get(str(current_user.id)))
        return {'num_articulos':len(datos)}
