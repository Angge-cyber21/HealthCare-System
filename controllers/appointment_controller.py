# controllers/appointment_controller.py
from database import get_connection

class AppointmentController:
    def __init__(self):
        pass

    def get_queue(self):
        """
        Returns all appointments with patient and doctor names
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT a.id, a.patient_id, a.doctor_id, a.appointment_time, a.status,
                   p.name AS patient_name,
                   d.name AS doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            ORDER BY a.appointment_time ASC
        """)

        queue = cursor.fetchall()
        cursor.close()
        conn.close()
        return queue

    def add_to_queue(self, patient_id, doctor_id, appointment_time):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_time, status)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, doctor_id, appointment_time, 'Pending'))
        conn.commit()
        cursor.close()
        conn.close()