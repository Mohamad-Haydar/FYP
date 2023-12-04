import os
import zipfile
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    jsonify,
    make_response,
    send_file
)
from datetime import timedelta, datetime
from functools import wraps

import pdf_processor
from functions.main_functions import process_folder
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadSignature

from config import DB_USER_NAME, DB_KEY, DB_URL

import webview
import threading
import shutil
import pdfkit

# Initialize Celery
app = Celery("your_app_name", broker="redis://localhost:6379/0")

app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(days=5)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["SECRET_KEY"] = "1MvQbI07sSgoPEnMeXUFHQmzuLmlkYWt"
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "zip"}
db_path = os.path.join(os.path.dirname(__file__), 'FYP.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# app.config[
#     "SQLALCHEMY_DATABASE_URI"
# ] = f"mysql+pymysql://mohamad:%23%40%2176Mohamad612@127.0.0.1/FYP"
# f"mysql+pymysql://{DB_USER_NAME}:{DB_KEY}@{DB_URL}"
# for local connection "mysql+pymysql://mohamad:%23%40%2176Mohamad612@127.0.0.1/FYP"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# mail cofiguration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "mfh313haydar@gmail.com"
app.config["MAIL_PASSWORD"] = "izqvtyldeiaravru"

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.config["SECRET_KEY"])


def verify_token(token):
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(token, salt=app.config["SECRET_KEY"], max_age=3600)
        return email
    except BadSignature:
        return None


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"<Student {self.firstname}>"


class RegisterForm(FlaskForm):
    name = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username", "autocomplete": "off"},
    )
    email = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Email", "autocomplete": "off"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password", "autocomplete": "off"},
    )
    submit = SubmitField("Register")

    def validate_email(self, email):
        existing_user_email = Users.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                {"email": "That user already exist. Please choose a different one."}
            )


class LoginForm(FlaskForm):
    name = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={
            "placeholder": "Username",
            "autocomplete": "off",
        },
    )
    email = StringField(
        validators=[InputRequired(), Length(min=4, max=80)],
        render_kw={"placeholder": "Email", "autocomplete": "off"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password", "autocomplete": "off"},
    )
    submit = SubmitField("Login")

    def validate_name(self, name):
        user = Users.query.filter_by(name=name.data).first()
        if not user:
            raise ValidationError(
                {"name": "This User Name doesn't exist. Please choose a different one."}
            )

    def validate_email(self, email):
        existing_user_email = Users.query.filter_by(email=email.data).first()
        if existing_user_email and existing_user_email.name != self.name.data:
            raise ValidationError(
                {"name": "This User Name doesn't match the provided email."}
            )
        if not existing_user_email:
            raise ValidationError(
                {"email": "This Email doesn't exist. Please choose a different one."}
            )


class MyModel(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    text = db.Column(db.Text)
    entities = db.Column(db.Text)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    if verify_token(token):
        user_data = session.get("new_user")
        if user_data:
            hashed_password = user_data["password"]
            new_user = Users(
                name=user_data["name"],
                email=user_data["email"],
                password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Email verified successfully. You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid or expired verification link.", "error")
    else:
        flash("Invalid or expired verification link.", "error")

    return redirect(url_for("login"))


@app.route("/home")
@app.route("/")
def home():
    return render_template(
        "home.html", current_route=request.path, users=Users.query.all()
    )


# For login
@app.route("/login", methods=["GET", "POST"])
def login():
    pass_error = ""
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash(f"You Are Logged In Successfully!", "sucsess")
                return redirect(url_for("home"))
            else:
                pass_error = "Wrong Password!"
    return render_template(
        "login.html",
        form=form,
        current_route=request.path,
        pass_error=pass_error,
    )


#  user = Users.query.filter_by(email=form.email.data).first()
# For Register
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Generate verification token
        verification_token = generate_verification_token(form.email.data)

        # Create verification link
        verification_link = url_for(
            "verify_email", token=verification_token, _external=True
        )

        # Compose email message
        subject = "Email Verification"
        recipients = [form.email.data]
        html_body = render_template(
            "verification_email.html", verification_link=verification_link
        )
        message = Message(
            subject,
            sender="mfh313haydar@gmail.com",
            recipients=recipients,
            html=html_body,
        )

        # Send email
        mail.send(message)

        # Store user details in session or temporary database table
        session["new_user"] = {
            "name": form.name.data,
            "email": form.email.data,
            "password": bcrypt.generate_password_hash(form.password.data),
            "verification_token": verification_token,
        }

        flash(
            "A verification email has been sent to your email address. Please check your inbox to verify your account.",
            "success",
        )
        return redirect(url_for("login"))

    return render_template(
        "register.html", form=form, current_route=request.path, pass_error="pass_error"
    )


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/process", methods=["POST"])
def upload():

    # to make sure that uploads folder is empty before starting the process
    items = os.listdir("uploads")

    for item in items:
        item_path = os.path.join("uploads", item)
        if os.path.isfile(item_path):
            # If it's a file, remove it
            os.remove(item_path)
        elif os.path.isdir(item_path):
            # If it's a directory, remove it recursively
            shutil.rmtree(item_path)

    # Access the uploaded file using the Flask request object
    folder = request.files.get("certificate")
    model_name = request.form.get("model_name")
    certificate_type = request.form.get("type")

    folder_path = os.path.join("uploads", folder.filename)
    if(os.path.splitext(folder_path)[1] != ".zip"):
        return render_template(
            "error.html",
            data="Sorry, you need to enter a zip file to make the process!!!!"
        )
    folder.save(folder_path)

    # Extract the uploaded zip file
    with zipfile.ZipFile(folder_path, "r") as zip_ref:
        zip_ref.extractall("uploads")

    # Optionally, you can remove the uploaded zip file
    os.remove(folder_path)

    folder_path = "uploads"

    # folder_path = os.path.splitext(folder_path)[0]
    result = process_folder(folder_path, model_name, certificate_type)

    items = os.listdir(folder_path)

    for item in items:
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            # If it's a file, remove it
            os.remove(item_path)
        elif os.path.isdir(item_path):
            # If it's a directory, remove it recursively
            shutil.rmtree(item_path)

    count = 0
    for key in result:
        for test in result[key]["tested"]:
            if result[key]["summary"][test] > 0:
                count += 1
    return render_template(
        "results.html",
        result=result,
        current_route=request.path,
        certificate_type=certificate_type,
        count=count
    )

@app.route('/generate-pdf',  methods=["POST"])
def generate_pdf():
    # Get the "result" data from the submitted form
    result_data =  eval(request.form.get('result'))
    # Render the generate-pdf.html template with the "result" data
    count = 0
    for key in result_data:
        for test in result_data[key]["tested"]:
            if result_data[key]["summary"][test] > 0:
                count += 1
        

    rendered_html = render_template('generate-pdf.html', result=result_data, count=count)

    # Generate PDF using the "result" data
    if os.name == 'posix':  # 'posix' represents Linux/Unix-based systems
        wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'
    elif os.name == 'nt':  # 'nt' represents Windows
        wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    name = "Compliance Result for " + result_data[0]["user_input"] + ".pdf"
    pdfkit.from_string(rendered_html, name,configuration=config)

    # Download the PDF
    return send_file(name, as_attachment=True)

@app.route("/send_report", methods=["POST"])
def send_report():
    email = request.form.get("email")
    # data = request.form.get("data")
    # certificate_type = request.form.get("certificate_type")
    # user_input = request.form.get("user_input")
    # model = request.form.get("model")
    # range = request.form.get("range")
    # manufactor = request.form.get("manufactor")
    # tested = request.form.get("tested")
    # tested = eval(tested)
    # ceritificate_test = request.form.get("case")
    result = request.form.get("result")
    result = eval(result)

    # create the report for the compatible certificate
    html_body = render_template(
        "report.html",
        result=result
        # data=data,
        # user_input=user_input,
        # model=model,
        # range=range,
        # manufactor=manufactor,
        # current_route=request.path,
        # tested=tested,
        # certificate_type=certificate_type,
        # ceritificate_test=ceritificate_test,
    )

    msg = Message(
        "Report for the compatibility check of the",
        sender="mfh313haydar@gmail.com",
        recipients=[email],
        html=html_body,
    )
    mail.send(msg)
    flash(
        "The report was sent successfully!",
        "success",
    )
    return render_template(
        "home.html",
    )


# to redirect to the home page if we go to the process page via get request
@app.route("/process", methods=["GET"])
def to_home():
    return redirect(url_for("home"))


# the train page
@app.route("/train", methods=["GET"])
def train():
    if not current_user.is_authenticated:
        flash(f"Please Login To Access The Train Page", "error")
        return redirect(url_for("home"))
    else:
        return render_template("train.html", current_route=request.path, success=False)


@app.route("/train", methods=["POST"])
def send_labels():
    data = request.get_json()
    text = data.get("text")
    entities = data.get("entities")
    new_record = MyModel(user_id=current_user.id, text=text, entities=entities)
    db.session.add(new_record)
    db.session.commit()
    flash(
        f"Thank You {current_user.name} For Your Work! The Data Was Added Successfuly.",
        "success",
    )
    return jsonify(redirect_url="/")


@app.route("/about")
def aboutPage():
    return render_template("about.html")


# 404 page
@app.errorhandler(404)
def page_not_found(error):
    return (
        render_template(
            "error.html", data="404. Page Not Found!", current_route=request.path
        ),
        404,
    )


def run_flask():
    app.run()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
    # flask_thread = threading.Thread(target=run_flask)
    # flask_thread.start()

    # webview.create_window("PV System Processor", "http://localhost:5000")
    # webview.start()