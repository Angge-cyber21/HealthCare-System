def main_menu():
    while True:
        print("\n======= ADMIN DASHBOARD =======")
        print("[1] ▸ Hospital Structure")
        print("[2] ▸ Patient Management")
        print("[3] ▸ Diagnosis Center")
        print("[4] ▸ Appointment Queue")
        print("[5] ▸ Serve Patient")
        print("[6] ▸ Exit")
        print("================================")

        choice = input("Select a section to toggle: ")

        if choice == "1":
            toggle_hospital_structure()

        elif choice == "2":
            toggle_patient_management()

        elif choice == "3":
            toggle_diagnosis_center()

        elif choice == "4":
            toggle_appointment_queue()

        elif choice == "5":
            toggle_serve_patient()

        elif choice == "6":
            print("Exiting system...")
            break

        else:
            print("Invalid option! Try again.")


# -------------------------------
#  TOGGLE SECTIONS (SUB-MENUS)
# -------------------------------

def toggle_hospital_structure():
    while True:
        print("\n--- Hospital Structure ---")
        print("1. View hospital departments")
        print("2. View doctor list")
        print("3. Back to Dashboard")

        ch = input("Choose: ")

        if ch == "1":
            print("Displaying hospital departments...")
        elif ch == "2":
            print("Displaying doctor list...")
        elif ch == "3":
            break
        else:
            print("Invalid choice!")


def toggle_patient_management():
    while True:
        print("\n--- Patient Management ---")
        print("1. Register new patient")
        print("2. View patient list")
        print("3. Back to Dashboard")

        ch = input("Choose: ")

        if ch == "1":
            register_patient_flow()
        elif ch == "2":
            print("Showing patient list...")
        elif ch == "3":
            break
        else:
            print("Invalid choice!")


def toggle_diagnosis_center():
    while True:
        print("\n--- Diagnosis Center ---")
        print("1. Add Diagnosis")
        print("2. View Diagnosis Records")
        print("3. Back to Dashboard")

        ch = input("Choose: ")

        if ch == "1":
            print("Adding diagnosis...")
        elif ch == "2":
            print("Viewing diagnosis records...")
        elif ch == "3":
            break
        else:
            print("Invalid choice!")


def toggle_appointment_queue():
    while True:
        print("\n--- Appointment Queue ---")
        print("1. Add to appointment queue")
        print("2. View queue")
        print("3. Back to Dashboard")

        ch = input("Choose: ")

        if ch == "1":
            print("Adding patient to queue...")
        elif ch == "2":
            print("Showing current queue...")
        elif ch == "3":
            break
        else:
            print("Invalid choice!")


def toggle_serve_patient():
    while True:
        print("\n--- Serve Patients ---")
        print("1. Serve next patient in queue")
        print("2. Back to Dashboard")

        ch = input("Choose: ")

        if ch == "1":
            print("Serving next patient...")
        elif ch == "2":
            break
        else:
            print("Invalid choice!")


# -------------------------
# NEW USER REGISTRATION LOGIC
# -------------------------

users_db = {}  # temporary in-memory database


def register_patient_flow():
    print("\n--- Patient Registration ---")
    username = input("Enter patient username: ")

    if username in users_db:
        print("User already exists! Proceeding to patient functions...")
        return
    else:
        print("New user detected. Registering now...")
        password = input("Enter password: ")
        fullname = input("Enter full name: ")
        age = input("Enter age: ")
        address = input("Enter address: ")

        users_db[username] = {
            "password": password,
            "fullname": fullname,
            "age": age,
            "address": address
        }

        print("Registration successful!")


# ---------------------------
# START PROGRAM
# ---------------------------

if __name__ == "__main__":
    main_menu()
