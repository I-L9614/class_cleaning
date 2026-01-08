from flask import Blueprint, request, render_template, redirect, url_for, flash
from server.models import Students, Classes
student_bp = Blueprint('student', __name__, template_folder='../templates')

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        class_id = request.form['class_id']
        Students.insert_one({
            "name": name,
            "email": email,
            "class_id": class_id,
            "unavailable_weeks": []
        })
        flash("נרשמת בהצלחה!", "success")
        return redirect(url_for('student.register'))

    classes = Classes.find()
    return render_template('register.html', classes=classes)
