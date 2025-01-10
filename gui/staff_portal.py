import tkinter as tk
from tkinter import Toplevel, Label, Button, StringVar, Entry, messagebox
import os
import sqlite3

from gui.inventory_management import InventoryManagement
from gui.manage_customers import ManageCustomers
from gui.manage_products import ManageProducts
from gui.manage_staff import ManageStaff
from gui.place_orders import PlaceOrders
from utils.encryption import verify_password


class StaffPortal:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.staff_portal_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.staff_portal_window.title("Staff Portal")
        self.staff_portal_window.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        Label(self.staff_portal_window, text="Staff Portal", font=("Arial", 16)).pack(pady=20)

        Button(self.staff_portal_window, text="Login", command=self.login, width=20).pack(pady=10)
        Button(self.staff_portal_window, text="Back",
               command=lambda: self.navigation_manager.back(self.staff_portal_window), width=20).pack(pady=10)

    def login(self):
        self.navigation_manager.navigate(
            self.staff_portal_window,
            lambda: AdminLogin(self.staff_portal_window, self.navigation_manager)
        )

    def open_portal_by_role(self, job_role_id):
        if job_role_id == 1:
            self.navigation_manager.navigate(
                self.staff_portal_window,
                lambda: ManagerPortal(self.staff_portal_window, self.navigation_manager)
            )
        elif job_role_id == 2:
            self.navigation_manager.navigate(
                self.staff_portal_window,
                lambda: AssociatePortal(self.staff_portal_window, self.navigation_manager)
            )
        elif job_role_id == 3:
            self.navigation_manager.navigate(
                self.staff_portal_window,
                lambda: CleanerPortal(self.staff_portal_window, self.navigation_manager)
            )
        else:
            messagebox.showerror("Error", "Invalid role.")


class AdminLogin:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.login_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.login_window.title("Admin Login")
        self.login_window.geometry("300x200")

        self.employee_id_var = StringVar()
        self.password_var = StringVar()

        self.create_widgets()

    def create_widgets(self):
        Label(self.login_window, text="Employee ID").pack(pady=5)
        Entry(self.login_window, textvariable=self.employee_id_var).pack(pady=5)
        Label(self.login_window, text="Password").pack(pady=5)
        Entry(self.login_window, textvariable=self.password_var, show="*").pack(pady=5)

        Button(self.login_window, text="Login", command=self.authenticate_user).pack(pady=10)
        Button(self.login_window, text="Back",
               command=lambda: self.navigation_manager.back(self.login_window)).pack(pady=10)


    def authenticate_user(self):
        employee_id = self.employee_id_var.get().strip()
        password = self.password_var.get().strip()

        if not employee_id or not password:
            messagebox.showerror("Error", "Employee ID and password cannot be empty.")
            return

        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/autodatabase.db"))

        try:
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT JobRoleID, Password
                FROM Employees
                WHERE EmployeeID = ?
            """, (employee_id,))
            result = cursor.fetchone()

            if result:
                job_role_id, stored_password = result
                if verify_password(stored_password, password):
                    self.navigation_manager.navigate(
                        self.login_window,
                        lambda: StaffPortal(self.parent, self.navigation_manager).open_portal_by_role(job_role_id)
                    )
                else:
                    messagebox.showerror("Error", "Incorrect password.")
            else:
                messagebox.showerror("Error", "Employee ID not found.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()


class ManagerPortal:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.manager_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.manager_window.title("Manager Portal")
        self.manager_window.geometry("400x500")
        self.create_widgets()

    def create_widgets(self):
        Label(self.manager_window, text="Manager Portal", font=("Arial", 16)).pack(pady=20)

        Button(self.manager_window, text="Manage Staff",
               command=lambda: self.navigation_manager.navigate(
                   self.manager_window, lambda: ManageStaff(self.manager_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.manager_window, text="Manage Customers",
               command=lambda: self.navigation_manager.navigate(
                   self.manager_window, lambda: ManageCustomers(self.manager_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.manager_window, text="Manage Products",
               command=lambda: self.navigation_manager.navigate(
                   self.manager_window, lambda: ManageProducts(self.manager_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.manager_window, text="Place Orders",
               command=lambda: self.navigation_manager.navigate(
                   self.manager_window, lambda: PlaceOrders(self.manager_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.manager_window, text="Inventory Management",
               command=lambda: self.navigation_manager.navigate(
                   self.manager_window, lambda: InventoryManagement(self.manager_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.manager_window, text="Logout",
               command=lambda: self.navigation_manager.back(self.manager_window)).pack(pady=10)

class AssociatePortal:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.associate_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.associate_window.title("Associate Portal")
        self.associate_window.geometry("400x400")
        self.create_widgets()

    def create_widgets(self):
        Label(self.associate_window, text="Associate Portal", font=("Arial", 16)).pack(pady=20)

        Button(self.associate_window, text="Manage Customers",
               command=lambda: self.navigation_manager.navigate(
                   self.associate_window, lambda: ManageCustomers(self.associate_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.associate_window, text="Manage Products",
               command=lambda: self.navigation_manager.navigate(
                   self.associate_window, lambda: ManageProducts(self.associate_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.associate_window, text="Inventory Management",
               command=lambda: self.navigation_manager.navigate(
                   self.associate_window, lambda: InventoryManagement(self.associate_window, self.navigation_manager)
               )).pack(pady=10)

        Button(self.associate_window, text="Logout",
               command=lambda: self.navigation_manager.back(self.associate_window)).pack(pady=10)


class CleanerPortal:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.cleaner_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.cleaner_window.title("Cleaner Portal")
        self.cleaner_window.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        Label(self.cleaner_window, text="Cleaner Portal", font=("Arial", 16)).pack(pady=20)

        Button(self.cleaner_window, text="View System Dashboard",
               command=lambda: self.view_dashboard()).pack(pady=10)

        Button(self.cleaner_window, text="Logout",
               command=lambda: self.navigation_manager.back(self.cleaner_window)).pack(pady=10)

    def view_dashboard(self):
        messagebox.showinfo("System Dashboard", "This will display system statistics.")