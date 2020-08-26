from flask import Flask,render_template,redirect, request, url_for, flash, session, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from forms import RegistrationForm, LoginForm, Addproducts
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os
import secrets


app = Flask(__name__)
# file upload location
basedir = os.path.abspath(os.path.dirname(__file__))

#database connenction
app.secret_key = 'Secrete_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mysite.db'
    #'mysql://root:''@localhost/bestbuy'
# for connecting with this database called mysqlphpadmin we must download this pip install Flask-MySQLdb for flask
app.config['SECRET_KEY'] = 'crud secrate'
# image uploads file
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app) # database imgrate
bcrypt = Bcrypt(app) # passwor security


# database table cration
class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(30), unique=True)
    username    = db.Column(db.String(50), unique=True)
    email       = db.Column(db.String(120), unique=True)
    password    = db.Column(db.String(120), unique=False)
    profile     = db.Column(db.String(120), unique=True)
# table for brands
class Brand(db.Model):  # chiled table
    __tablename__ = 'brand'
    id      = db.Column(db.Integer, primary_key = True)
    name    = db.Column(db.String(30), nullable = False, unique = True)
    #brand = db.relationship('Product', backref='Product', lazy=True)

# table for category
class Category(db.Model):  # chiled table
    __tablename__ = 'category'
    id      = db.Column(db.Integer, primary_key = True)
    name    = db.Column(db.String(30), unique = True)
    #category = db.relationship('Product', backref='Product', lazy=True)
    #category = db.relationship('Addproduct',  back_populates="Addproduct" )



# this table is used for addproduct  # parent table
class Product(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80), nullable=False)
    price       = db.Column(db.Numeric(10,2), nullable=False)
    discount    = db.Column(db.Integer, default = 0)
    stock       = db.Column(db.Integer, nullable=False)
    colors      = db.Column(db.Text, nullable=False)
    pub_date    = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    brand_id    = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand       = db.relationship("Brand", backref=db.backref("brand", uselist=False))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category    = db.relationship("Category", backref=db.backref("category", uselist=False))

    image_1     = db.Column(db.String(150),nullable=False, default = 'image.jpg')
    image_2     = db.Column(db.String(150),nullable=False, default='image.jpg')
    image_3     = db.Column(db.String(150),nullable=False, default='image.jpg')

    def __repr__(self):
        return '<Addproduct %r>' % self.name


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).paginate(page=page, per_page=8)
    #brand = Product.query.all()
    brands = Brand.query.join(Product, (Brand.id == Product.brand_id)).all()
    category = Category.query.join(Product, (Category.id == Product.category_id)).all()
    return render_template('home.html',  brands = brands, category = category, products = products)

@app.route('/product-details/<int:id>')
def product_details(id):
    product = Product.query.get_or_404(id)
    brands = Brand.query.join(Product, (Brand.id == Product.brand_id)).all()
    category = Category.query.join(Product, (Category.id == Product.category_id)).all()
    return render_template('product-details.html', product = product, brands= brands, category=category)

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type=int)
    get_b = Brand.query.filter_by(id=id).first_or_404()
    brand = Product.query.filter_by(brand=get_b).paginate(page=page, per_page=6)
    brands = Brand.query.join(Product, (Brand.id == Product.brand_id)).all()
    category = Category.query.join(Product, (Category.id == Product.category_id)).all()
    return render_template('home.html', brands = brands, brand = brand, category =  category, get_b = get_b)

@app.route('/category/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Product.query.filter_by(category= get_cat).paginate(page=page, per_page=6)
    brands = Brand.query.join(Product, (Brand.id == Product.brand_id)).all()
    category = Category.query.join(Product, (Category.id == Product.category_id)).all()
    return render_template('home.html', get_category = get_cat_prod, category = category, brands = brands, get_cat = get_cat)

@app.route('/admin')
def admin():
    #if 'email' not in session:
      #  flash(f' please login', 'danger')
       # return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('index.html', title = 'admin page', products = products )

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        password_hashed = bcrypt.generate_password_hash(form.password.data)
        user = User(name = form.name.data,
                    username = form.username.data,
                    email =  form.email.data,
                   password =  password_hashed)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.name.data} Please Longin to site', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# login for route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            #session['email'] = form.email.data
            return redirect(url_for('admin'))
            flash(f'Welcome {form.email.data} You are logedin now', 'success')

        else:
            flash('Worng Password try again', 'danger')
    return render_template('login.html', form = form, title = 'Login Form')


@app.route('/brands')
def brands():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('brand.html', brands = brands)


@app.route('/updatedcategory/<int:id>', methods = ['GET', 'POST'])
def updatedcategory(id):
    updatedcategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        updatedcategory.name = category
        flash(f'data was updated sucessfully', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('updatedbrand.html', updatedcategory = updatedcategory )

# this route is used for the update the brand data
@app.route('/updatedbrand/<int:id>', methods = ['GET', 'POST'])
def updatedbrand(id):
    updatedbrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == 'POST':
        updatedbrand.name = brand
        flash(f'data was updated sucessfully', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('updatedbrand.html', updatedbrand = updatedbrand )

# this route is used for the delete the data from the brand
@app.route('/deletebrand/<int:id>', methods = ['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand{brand.name} was deleted from your database', 'success')
        return redirect(url_for('brands'))
    flash(f' The brand{brand.name} cant deleted', 'warning')
    return redirect(url_for('brands'))



@app.route('/category')
def categories():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('brand.html', categories = categories)


# this route is used for the delete the data from the Category
@app.route('/deletecategory/<int:id>', methods = ['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        flash(f'The Category {category.name} was deleted from your database', 'success')
        return redirect(url_for('categories'))
    flash(f' The Category {category.name} cant deleted', 'warning')
    return redirect(url_for('categories'))


@app.route('/addbrand', methods = ['GET', 'POST'])
def addbrand():
    if request.method == 'POST':
        getbrand = request.form.get('brand')
        brand = Brand(name = getbrand)
        db.session.add(brand)
        flash(f' The Brand {getbrand} was added to your list', 'success')
        db.session.commit()
        return redirect('addbrand')
    return render_template('addbrand.html', brands = 'brands')

@app.route('/addcat', methods = ['GET', 'POST'])
def addcat():
    if request.method == 'POST':
        getcategory = request.form.get('category')
        category = Category(name = getcategory)
        db.session.add(category)
        flash(f' The Brand {getcategory} was added to your list', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('addbrand.html', category = 'category')



# add products and products route
@app.route('/addproduct', methods = ['GET', 'POST'])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method == 'POST':
        name        = form.name.data
        price       = form.price.data
        discount    = form.discount.data
        stock       = form.stock.data
        colors      = form.colors.data
        brand       = request.form.get('brand')
        category    = request.form.get('category')
        image_1     = photos.save(request.files.get('image_1'), secrets.token_hex(10) + '.')
        image_2     = photos.save(request.files.get('image_2'), secrets.token_hex(10) + '.')
        image_3     = photos.save(request.files.get('image_3'), secrets.token_hex(10) + '.')
        addproduct  = Product(name= name, price = price, discount = discount, stock = stock,
                                        colors = colors, brand_id = brand, category_id = category,
                                        image_1 = image_1,  image_2 = image_2, image_3 = image_3)

        db.session.add(addproduct)
        db.session.commit()
        flash(f'The Product {name} has been added to your database', 'success')
        return redirect(url_for('admin'))
    return render_template('addproduct.html', form = form, brands = brands, categories = categories)


@app.route('/updateproduct/<int:id>', methods = ['POST', 'GET'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Product.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name = secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name = secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name = secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name = secrets.token_hex(10) +".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name = secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name = secrets.token_hex(10) + ".")

        db.session.commit()
        return redirect(url_for('admin'))
    flash(f' Your Product has been updated', 'success')
    form.name.data = product.name
    form.price.data = product.price
    form.stock.data = product.stock
    form.discount.data = product.discount
    form.colors.data = product.colors
    return render_template('updateproduct.html', form = form, brands = brands, category = categories, product = product )

@app.route('/deleteproduct/<int:id>', methods = ['POST'])
def deleteproduct(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
         try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
         except Exception as e:
            print(e)
         db.session.delete(product)
         db.session.commit()
         flash(f' product data was deleted', 'success')
         return redirect(url_for('admin'))

    flash(f' cant delte the product', 'danger')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
