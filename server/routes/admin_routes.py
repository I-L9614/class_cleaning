from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Classes, Students, Admins
from utils import run_lottery, hash_password, verify_password
admin_bp = Blueprint('admin', __name__, template_folder='../templates')

# Login/logout
@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admins.find_one({"email": email})
        if admin and verify_password(password, admin['password']):
            session['admin_email'] = email
            return redirect(url_for('admin.dashboard'))
        flash("פרטי התחברות שגויים", "danger")
    return render_template('admin_dashboard.html', login=True)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_email', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
def dashboard():
    if 'admin_email' not in session:
        return redirect(url_for('admin.login'))
    classes = Classes.find()
    return render_template('admin_dashboard.html', classes=classes, login=False)

@admin_bp.route('/create_class', methods=['POST'])
def create_class():
    name = request.form['name']
    Classes.insert_one({"name": name})
    flash("כיתה נוצרה בהצלחה", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/run_lottery/<class_id>')
def run_class_lottery(class_id):
    run_lottery(class_id)
    flash("הגרלה רצה בהצלחה!", "success")
    return redirect(url_for('admin.dashboard'))
