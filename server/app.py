from flask import Flask
from routes.admin_routes import admin_bp
from routes.student_routes import student_bp
from flask import render_template
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")
csrf = CSRFProtect(app)

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
