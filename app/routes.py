from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_connection
from controllers.hospital_controller import HospitalController
from controllers.patient_controller import PatientController
from controllers.appointment_controller import AppointmentController
import hashlib
import random


app = Flask(__name__)
app.secret_key = 'secret_key_here'

hospital_ctrl = HospitalController()
patient_ctrl = PatientController()
appt_ctrl = AppointmentController()

# ---------------- Home ----------------
@app.route('/')
def home():
    return render_template('home.html')


# ---------------- Admin Registration ----------------
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)",
                           (username, hashed_password))
            conn.commit()
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return f"Error: {str(e)}"
        cursor.close()
        conn.close()
        return redirect(url_for('login', role='admin'))

    return render_template('register_admin.html')


# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'patient')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM departments")
    departments = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        if role == 'patient':
            name = request.form['name']
            department_id = int(request.form['department_id'])

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id FROM patients WHERE name=%s AND department_id=%s",
                (name, department_id)
            )
            patient = cursor.fetchone()
            cursor.close()
            conn.close()

            if patient:
                session['user'] = {'id': patient['id'], 'name': name, 'role': 'patient'}
                return redirect(url_for('patient_dashboard'))
            else:
                flash("Patient not found!", "error")

        else:
            username = request.form['username']
            password = request.form['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM admins WHERE username=%s AND password=%s",
                (username, hashed_password)
            )
            admin = cursor.fetchone()
            cursor.close()
            conn.close()

            if admin:
                session['user'] = {'role': 'admin', 'username': username}
                session['admin_name'] = admin['username']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', role=role, departments=departments, error="Invalid username or password")

    return render_template('login.html', role=role, departments=departments)


# ---------------- Admin Dashboard ----------------
@app.route('/index')
def index():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login', role='admin'))

    admin_name = session.get('admin_name', 'Admin')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.name, p.age, p.status, p.department_id,
               d.name AS department_name,
               doc.name AS doctor_name,
               doc.specialization
        FROM patients p
        LEFT JOIN departments d ON p.department_id = d.id
        LEFT JOIN doctors doc ON p.doctor_id = doc.id
    """)
    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', admin_name=admin_name, patients=patients)


# ---------------- Patients ----------------
@app.route('/patients')
def patients():
    patients_list = patient_ctrl.get_all_patients()  # <-- use get_all_patients()
    return render_template('patients.html', patients=patients_list)



# ---------------- Doctor API (for modal popup) ----------------
import random  # make sure this is imported at the top

@app.route('/api/patient/<int:patient_id>/doctor')
def api_patient_doctor(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.name AS patient_name,
               d.name AS doctor_name,
               d.specialization,
               d.contact
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.id
        WHERE p.id = %s
    """, (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Random bio based on specialization
    bio_pool = {
        "Cardiologist": [
            "Passionate about heart health and patient care.",
            "Over 15 years of experience treating cardiac patients.",
            "Focused on preventive cardiology and lifestyle guidance."
        ],
        "Dermatologist": [
            "Expert in skin care and cosmetic treatments.",
            "Committed to helping patients achieve healthy skin.",
            "Specializes in both medical and cosmetic dermatology."
        ],
        # add more specializations as needed
    }
    spec = patient.get("specialization") or ""
    patient['bio'] = random.choice(bio_pool.get(spec, ["Experienced doctor."]))

    response = {
        "patient_name": patient.get("patient_name", "Unknown"),
        "doctor_name": patient.get("doctor_name") or "Not Assigned",
        "specialization": patient.get("specialization") or "-",
        "contact": patient.get("contact") or "-",
        "bio": patient.get("bio") or "Experienced doctor."
    }

    return jsonify(response)


# ---------------- Add Diagnosis ----------------
@app.route('/add_diagnosis/<int:patient_id>', methods=['GET', 'POST'])
def add_diagnosis(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE id=%s", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        cursor.close()
        conn.close()
        flash("Patient not found", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        cursor.execute(
            "INSERT INTO diagnoses (patient_id, diagnosis) VALUES (%s, %s)",
            (patient_id, diagnosis)
        )
        conn.commit()
        flash("Diagnosis added successfully!", "success")

    cursor.execute("SELECT * FROM diagnoses WHERE patient_id=%s", (patient_id,))
    diagnoses = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('add_diagnosis.html', patient=patient, diagnoses=diagnoses)


# ---------------- Patient Dashboard ----------------
@app.route('/patient/dashboard', methods=['GET'])
def patient_dashboard():
    if 'user' not in session or session['user']['role'] != 'patient':
        return redirect(url_for('login', role='patient'))

    patient_id = session['user']['id']
    patient_name = session['user']['name']

    diagnoses = patient_ctrl.get_diagnoses(patient_id)
    all_queue = appt_ctrl.get_queue()
    queue = [q for q in all_queue if q['patient_id'] == patient_id]

    return render_template('patient_dashboard.html',
                           patient_name=patient_name,
                           diagnoses=diagnoses,
                           queue=queue)


# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


# ---------------- Hospitals ----------------
@app.route('/hospitals', methods=['GET', 'POST'])
def hospitals():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form.get('name')
        age = int(request.form.get('age'))
        department_id = int(request.form.get('department_id'))
        doctor_id = request.form.get('doctor_id') or None

        cursor.execute(
            "INSERT INTO patients (name, age, status, department_id, doctor_id) VALUES (%s, %s, %s, %s, %s)",
            (name, age, 'Active', department_id, doctor_id)
        )
        conn.commit()

    cursor.execute("""
        SELECT d.*, doc.name AS doctor_name, doc.id AS doctor_id
        FROM departments d
        LEFT JOIN doctors doc ON d.doctor_in_charge_id = doc.id
        ORDER BY d.id
    """)
    departments = cursor.fetchall()
    department_data = []

    for dept in departments:
        dept_id = dept['id']
        cursor.execute("""
            SELECT p.id, p.name, p.age, p.status, p.doctor_id,
                   doc.name AS doctor_name, doc.specialization
            FROM patients p
            LEFT JOIN doctors doc ON p.doctor_id = doc.id
            WHERE p.department_id=%s
        """, (dept_id,))
        patients = cursor.fetchall()

        cursor.execute("SELECT id, name FROM doctors WHERE department_id=%s", (dept_id,))
        doctors = cursor.fetchall()

        department_data.append({
            "id": dept_id,
            "name": dept['name'],
            "total_beds": dept.get('total_beds', 0),
            "doctor_in_charge": dept.get('doctor_name'),
            "doctor_in_charge_id": dept.get('doctor_id'),
            "patients": patients,
            "doctors": doctors
        })

    cursor.close()
    conn.close()
    return render_template('hospitals.html', departments=department_data)


# ---------------- Add Patient ----------------
@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        name = request.form['name']
        age = request.form['age']
        department_id = request.form['department_id']
        doctor_id = request.form.get('doctor_id')

        patient_id = patient_ctrl.add_patient(name, age, department_id, doctor_id)
        doctor_name = None

        if doctor_id:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name FROM doctors WHERE id=%s", (doctor_id,))
            row = cursor.fetchone()
            doctor_name = row['name'] if row else None
            cursor.close()
            conn.close()

        if patient_id:
            return jsonify({'success': True, 'patient': {
                'id': patient_id,
                'name': name,
                'age': age,
                'status': 'Active',
                'doctor_name': doctor_name
            }})
        else:
            return jsonify({'success': False, 'error': 'Failed to add patient'})

    except Exception as e:
        print("Error adding patient:", e)
        return jsonify({'success': False, 'error': str(e)})


# ---------------- Remove Patient ----------------
@app.route('/remove_patient/<int:patient_id>', methods=['POST'])
@app.route('/remove_patient/<int:patient_id>', methods=['POST'])
def remove_patient(patient_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Delete related diagnoses
        cursor.execute("DELETE FROM diagnoses WHERE patient_id=%s", (patient_id,))

        # Delete related appointments
        cursor.execute("DELETE FROM appointments WHERE patient_id=%s", (patient_id,))

        # Delete the patient
        cursor.execute("DELETE FROM patients WHERE id=%s", (patient_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})

    except Exception as e:
        print("Error removing patient:", e)
        return jsonify({"success": False, "error": str(e)})


# ---------------- Update Status ----------------
@app.route('/update_status/<int:patient_id>', methods=['POST'])
def update_status(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM patients WHERE id=%s", (patient_id,))
    patient = cursor.fetchone()
    if patient:
        new_status = 'Observation' if patient['status'] == 'Active' else 'Active'
        cursor.execute("UPDATE patients SET status=%s WHERE id=%s", (new_status, patient_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "new_status": new_status})
    return jsonify({"success": False})

@app.route('/update_appointment_status/<int:appt_id>', methods=['POST'])
def update_appointment_status(appt_id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify(success=False, error="Access denied")

    new_status = request.json.get('status')
    if new_status not in ['Pending','Confirmed','Cancelled']:
        return jsonify(success=False, error="Invalid status")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status=%s WHERE id=%s", (new_status, appt_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(success=True)

# ---------------- Patient Departments ----------------
@app.route('/patient_department')
def patient_department():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments ORDER BY id")
    departments = cursor.fetchall()

    # Bio pool by specialization
    bio_pool = {
        "Cardiologist": [
            "Expert in heart health and cardiac care.",
            "Specializes in preventive cardiology and heart disease management.",
            "Focused on innovative treatments for cardiovascular conditions."
        ],
        "Neurologist": [
            "Expert in diagnosing and treating nervous system disorders.",
            "Specializes in stroke and epilepsy treatment.",
            "Focuses on neurological health and patient well-being."
        ],
        "Pediatrician": [
            "Provides comprehensive child healthcare.",
            "Specializes in preventive care and vaccinations.",
            "Caring pediatrician focused on growth and development."
        ],
        "Dermatologist": [
            "Focus on skin care and cosmetic procedures.",
            "Expert in acne and skin health management.",
            "Specializes in dermatological treatments and patient education."
        ]
    }

    department_data = []
    for dept in departments:
        cursor.execute("SELECT id, name, specialization FROM doctors WHERE department_id=%s", (dept['id'],))
        doctors = cursor.fetchall()
        # Assign a random matching bio to each doctor
        for doc in doctors:
            spec = doc['specialization']
            doc['bio'] = random.choice(bio_pool.get(spec, ["Experienced doctor."]))
            doc['email'] = f"{doc['name'].replace(' ','').lower()}@hospital.com"
            doc['phone'] = "+63 912 000 000"
            doc['office'] = "Room 100"
            doc['exp'] = f"{random.randint(5,20)} years"
            doc['edu'] = "Top Medical University"
            doc['avatar'] = "https://static.vecteezy.com/system/resources/previews/028/753/278/large_2x/doctor-icon-isolate-on-transparent-background-file-png.png"

        department_data.append({
            'id': dept['id'],
            'name': dept['name'],
            'doctor_in_charge': dept.get('doctor_in_charge') or 'None',
            'doctors': doctors
        })

    cursor.close()
    conn.close()

    # Get patient appointments
    queue = appt_ctrl.get_queue()
    return render_template('patient_department.html', departments=department_data, queue=queue)


# ---------------- Patient Appointment Submission ----------------
@app.route('/patient_appointments', methods=['POST'])
def patient_appointments():
    if 'user' not in session or session['user']['role'] != 'patient':
        return jsonify(success=False, error="Not logged in")

    patient_id = session['user']['id']
    doctor_id = request.form.get('doctor_id')
    appt_datetime = request.form.get('appt_datetime')

    if not doctor_id or not appt_datetime:
        return jsonify(success=False, error="Missing doctor or datetime")

    try:
        appt_ctrl.add_to_queue(patient_id, doctor_id, appt_datetime)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

# ---------------- Patient Doctor Overview ----------------
@app.route('/patient/<int:patient_id>/doctor')
def patient_doctor(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.name AS patient_name, d.name AS doctor_name, d.specialization, d.contact
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.id
        WHERE p.id = %s
    """, (patient_id,))
    patient = cursor.fetchone()
    conn.close()

    if not patient:
        flash("Patient or doctor not found", "error")
        return redirect(url_for('patient_dashboard'))

    return render_template('doctor_overview.html', patient=patient)



    cursor.close()
    conn.close()

    return render_template('appointments.html', queue=queue)
# ---------------- Appointments (Admin view) ----------------
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if 'user' not in session:
        return jsonify(success=False, error="Not logged in") if request.method == 'POST' else redirect(url_for('login'))

    if session['user']['role'] != 'admin':
        return jsonify(success=False, error="Access denied") if request.method == 'POST' else redirect(url_for('patient_dashboard'))

    if request.method == 'POST':
        try:
            patient_id = int(request.form.get('patient_id'))
            doctor_id = int(request.form.get('doctor_id'))
            appointment_time = request.form.get('appt_datetime')

            appt_ctrl.add_to_queue(patient_id, doctor_id, appointment_time)
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))

    # GET: render admin view
    # Fetch all appointments with patient and doctor names
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.patient_id, p.name AS patient_name,
               a.doctor_id, d.name AS doctor_name,
               a.appointment_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.appointment_time ASC
    """)
    queue = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('appointments.html', queue=queue)
