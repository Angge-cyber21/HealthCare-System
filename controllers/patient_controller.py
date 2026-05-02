from database import get_connection
from models.linked_list import LinkedList

class PatientController:
    def __init__(self, appointment_queue=None):
        self.appointment_queue = appointment_queue  # AppointmentController instance

    def add_patient(self, name, age, department_id, doctor_id=None):
        """
        Add patient to DB and optionally assign doctor.
        """
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO patients (name, age, department_id, doctor_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, age, department_id, doctor_id))
            patient_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return patient_id
        return None

    def get_all_patients(self):
        """
        Returns all patients including assigned doctor name (if any).
        """
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT 
                    p.id,
                    p.name,
                    p.age,
                    p.department_id,
                    p.doctor_id,
                    d.name AS doctor_name
                FROM patients p
                LEFT JOIN doctors d
                    ON p.doctor_id = d.id
                ORDER BY p.id DESC
            """

            cursor.execute(sql)
            rows = cursor.fetchall()

            cursor.close()
            conn.close()
            return rows

        return []

    def get_diagnoses(self, patient_id):
        """
        Fetch all diagnoses for a patient using LinkedList and return as list of dicts
        """
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM diagnoses WHERE patient_id = %s", (patient_id,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            ll = LinkedList()
            for row in rows:
                ll.append(row['diagnosis'])

            return [{'diagnosis': diag} for diag in ll.to_list()]
        return []

    def add_diagnosis(self, patient_id, diagnosis):
        """
        Add a diagnosis to the database
        """
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO diagnoses (patient_id, diagnosis) VALUES (%s, %s)",
                (patient_id, diagnosis)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
