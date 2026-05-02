from database import get_connection
from models.tree import TreeNode

class HospitalController:

    def __init__(self):
        self.root = TreeNode("Hospital")
        self.load_structure()

    def load_structure(self):
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch all departments with doctor in charge
        cursor.execute("""
            SELECT d.id, d.name, d.total_beds, doc.name
            FROM departments d
            LEFT JOIN doctors doc ON d.id = doc.department_id AND doctor_in_charge = 1
        """)
        departments = cursor.fetchall()

        for dept in departments:
            dept_id, dept_name, total_beds, doc_in_charge = dept
            dept_data = {
                "id": dept_id,
                "name": dept_name,
                "total_beds": total_beds,
                "doctor_in_charge": doc_in_charge or "None"
            }
            dept_node = TreeNode(dept_name, dept_data)

            # Fetch doctors
            cursor.execute("SELECT id, name FROM doctors WHERE department_id=%s", (dept_id,))
            doctors = cursor.fetchall()
            for d in doctors:
                doctor_data = {"id": d[0], "name": d[1]}
                doctor_node = TreeNode(d[1], doctor_data)
                dept_node.add_child(doctor_node)

            # Fetch patients
            cursor.execute("""
                SELECT p.id, p.name, p.age, p.status, doc.name
                FROM patients p
                LEFT JOIN doctors doc ON p.doctor_id = doc.id
                WHERE p.department_id=%s
            """, (dept_id,))
            patients = cursor.fetchall()
            for p in patients:
                patient_data = {
                    "id": p[0],
                    "name": p[1],
                    "age": p[2],
                    "status": p[3],
                    "doctor_in_charge": p[4] or "None"
                }
                patient_node = TreeNode(p[1], patient_data)
                dept_node.add_child(patient_node)

            # Add department node to hospital root
            self.root.add_child(dept_node)

        cursor.close()
        conn.close()

    # Optional: Get departments as list of dicts for templates
    def get_departments_list(self):
        result = []
        for dept_node in self.root.children:
            dept_dict = dept_node.data.copy()
            dept_dict["doctors"] = [c.data for c in dept_node.children if "id" in c.data and "name" in c.data and "doctor_in_charge" not in c.data]
            dept_dict["patients"] = [c.data for c in dept_node.children if "status" in c.data]
            result.append(dept_dict)
        return result
