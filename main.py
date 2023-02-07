from flask import Flask, render_template, redirect, url_for, flash,g,abort,request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm,CreateUserForm,LoginForm,CommentForm
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


##CONFIGURE TABLES

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer,ForeignKey("users.id"))
    author = relationship("User",back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment",back_populates="post_parent")


class User(db.Model,UserMixin):
    __tablename__ = "users"
    id= db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250),unique=True, nullable=False)
    comments = relationship("Comment",back_populates="comment_author")
    posts = relationship("BlogPost",back_populates="author")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer,ForeignKey("users.id"))
    comment_author = relationship("User",back_populates="comments")
    post_id = db.Column(db.Integer,ForeignKey("blog_posts.id"))
    post_parent = relationship("BlogPost",back_populates="comments")
    body = db.Column(db.Text)
    # db.drop_all()




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#
# db.drop_all()
# db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts,current_user=current_user)


@app.route('/register',methods=["POST","GET"])
def register():
    form = CreateUserForm()
    if form.validate_on_submit():
        email_input = form.email.data
        user_mail =db.session.query(User).filter_by(email=email_input).first()
        if user_mail:
            flash("This user already exist. You can log in!")
            return redirect(url_for("login"))
        else:
            name_input = form.name.data
            password_input = form.password.data
            new_user = User(
                name=name_input,
                email=email_input,
                password = generate_password_hash(password_input,method="pbkdf2:sha256",salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts",current_user=current_user))
    return render_template("register.html",form=form,current_user=current_user)


@app.route('/login',methods=["POST","GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        entered_email = form.email.data
        entered_password = form.password.data
        user = db.session.query(User).filter_by(email=entered_email).first()
        if user:
            if check_password_hash(pwhash=user.password,password=entered_password):
                login_user(user)
                return redirect(url_for("get_all_posts",current_user=current_user))
            else:
                flash("Invalid password.")
                return redirect(url_for("login",current_user=current_user))
        else:
            flash("This email does not exist.")
            return redirect(url_for("login"))
    return render_template("login.html",form=form,current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>",methods=["POST","GET"])
def show_post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Login or Register in order to comment.")
            return redirect(url_for("login"))
        new_comment = Comment(
            body=form.body.data,
            )
        db.session.add(new_comment)
        db.session.commit()
    comments = Comment.query.all()
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post, current_user=current_user, form=form, all_comments=comments)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")




def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function



@app.route("/new-post",methods=["POST","GET"])
@admin_only
def add_new_post():

    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@admin_only
def edit_post(post_id):

    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    # db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
