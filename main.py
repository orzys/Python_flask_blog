from flask import Flask, render_template, url_for, request, redirect, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'baza_blog'
mongo = PyMongo(app)

#config
app.config.update(
    DEBUG = True,
    SECRET_KEY='sekretny_klucz'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self,id):
        self.id=id
        self.name="user"+str(id)
        self.password=self.name+"_secret"

    def __repr__(self):
        return "%d/%s/%s" %(self.id,self.name,self.password)

#generacja uzytkownikow
users = [User(id) for id in range (1,10)]

@app.route("/logout")
@login_required
def logout():
    logout_user()
    tytul='Wylogowanie'
    return render_template('logout.html',tytul=tytul)

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route("/login", methods=["GET", "POST"])
def login():
    tytul='Zaloguj się'
    if request.method=='POST':
        username=request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(url_for("index"))
        else:
            return abort(401)
    else:
        return render_template('login.html', tytul = tytul)

@app.route('/about')
def about():
    return render_template('omnie.html')

@app.route('/')
def index():
    posts = mongo.db.posts.find()
    return render_template('index.html', posts=posts)

@app.route('/add', methods= ['POST', 'GET'])
def add():
    if request.method == 'POST':
        tytul = request.form['tytul']
        post = request.form['post']
        data=datetime.utcnow().replace(microsecond=0)
        mongo.db.posts.insert_one({'tytul': tytul, 'post' : post, 'data' : data})
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<string:id>', methods= ['POST', 'GET'])
def delete(id):
    mongo.db.posts.remove({"_id" : ObjectId(id)})
    return redirect(url_for('index'))
    

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        tytul = request.form['tytul']
        post = request.form['post']
        data=datetime.utcnow().replace(microsecond=0)
        mongo.db.posts.update({"_id" : ObjectId(id)}, {"$set": {"tytul" : tytul, "post" : post, "data" : data}})
        return redirect(url_for('index'))
    post = mongo.db.posts.find_one({ '_id' : ObjectId(id)})
    return render_template('edit.html', post = post)

@app.route('/addcomment/<string:id>', methods=['GET', 'POST'])
def addcomment(id):
    if request.method == 'POST':
        #tytul = request.form['tytul']
        #post = request.form['post']
        komentarz = request.form['komentarz']
        #data=datetime.utcnow().replace(microsecond=0)
        mongo.db.posts.update({"_id": ObjectId(id)}, {"$push" : {"komentarz":komentarz}})
        return redirect(url_for('index'))
    posts = mongo.db.posts.find({ '_id' : ObjectId(id)})
    return render_template('addcomment.html', posts=posts)
    



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        if password==confirm: 
            mongo.db.users.insert_one({'username' : username, 'password' : password})
            flash("Użytkownik utworzony!")
        else:
            flash("Hasła nie są takie same")
    return render_template('register.html')


if __name__ == "__main__":
    app.run()