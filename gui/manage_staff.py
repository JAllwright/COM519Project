import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, messagebox, ttk
import re
from utils.database import Database
from utils.encryption import hash_password


class ManageStaff:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.manage_staff_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.manage_staff_window.title("Manage Staff")
        self.manage_staff_window.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        Label(self.manage_staff_window, text="Manage Staff", font=("Arial", 16)).pack(pady=10)


        columns = ("EmployeeID", "FirstName", "Surname", "ContactNumber", "BranchID", "JobRoleID")
        self.staff_table = ttk.Treeview(self.manage_staff_window, columns=columns, show="headings")
        for col in columns:
            self.staff_table.heading(col, text=col)
            self.staff_table.column(col, width=100)
        self.staff_table.pack(fill="both", expand=True, padx=10, pady=10)


        Button(self.manage_staff_window, text="Add Staff", command=self.add_staff_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_staff_window, text="Edit Staff", command=self.edit_staff_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_staff_window, text="Delete Staff", command=self.delete_staff_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_staff_window, text="Back",
               command=lambda: self.navigation_manager.back(self.manage_staff_window)).pack(side="left", padx=10, pady=10)


        self.populate_staff_table()

    def populate_staff_table(self):
        try:
            records = Database.fetch_all_staff()
            self.staff_table.delete(*self.staff_table.get_children())
            for record in records:
                self.staff_table.insert("", "end", values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch staff records: {e}")

    def validate_and_format_name(self, name):
        if not re.match(r"^[a-zA-Z- ]+$", name):
            return None
        return " ".join(
            part.capitalize()
            for part in re.split(r"(-| )", name.lower())
        )

    def validate_contact_number(self, contact):
        return re.match(r"^\d{10,15}$", contact)

    def add_staff_ui(self):
        add_window = Toplevel(self.manage_staff_window)
        add_window.title("Add Staff")
        add_window.geometry("400x400")


        fields = ["FirstName", "Surname", "ContactNumber", "BranchID", "JobRoleID", "Password"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(add_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(add_window, show="*" if field == "Password" else None)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        def submit_add():
            try:

                new_staff = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in new_staff.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return


                formatted_first_name = self.validate_and_format_name(new_staff["FirstName"])
                if not formatted_first_name:
                    messagebox.showerror("Error", "Invalid first name. Only letters, spaces, and hyphens are allowed.")
                    return

                formatted_surname = self.validate_and_format_name(new_staff["Surname"])
                if not formatted_surname:
                    messagebox.showerror("Error", "Invalid surname. Only letters, spaces, and hyphens are allowed.")
                    return


                if not self.validate_contact_number(new_staff["ContactNumber"]):
                    messagebox.showerror("Error", "Contact number must be 10-15 digits.")
                    return


                hashed_password = hash_password(new_staff["Password"])


                Database.add_staff(
                    formatted_first_name,
                    formatted_surname,
                    new_staff["ContactNumber"],
                    int(new_staff["BranchID"]),
                    int(new_staff["JobRoleID"]),
                    hashed_password
                )
                messagebox.showinfo("Success", "Staff added successfully.")
                add_window.destroy()
                self.populate_staff_table()
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add staff: {e}")

        Button(add_window, text="Submit", command=submit_add).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_staff_ui(self):
        selected_item = self.staff_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No staff member selected.")
            return

        staff_data = self.staff_table.item(selected_item, "values")
        edit_window = Toplevel(self.manage_staff_window)
        edit_window.title("Edit Staff")
        edit_window.geometry("400x300")


        fields = ["ContactNumber", "BranchID", "JobRoleID"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(edit_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(edit_window)
            entry.insert(0, staff_data[3 + idx])
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        def submit_edit():
            try:

                updates = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in updates.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return


                Database.update_staff(
                    int(staff_data[0]),
                    updates["ContactNumber"],
                    int(updates["BranchID"]),
                    int(updates["JobRoleID"]),
                )
                messagebox.showinfo("Success", "Staff updated successfully.")
                edit_window.destroy()
                self.populate_staff_table()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update staff: {e}")

        Button(edit_window, text="Submit", command=submit_edit).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_staff_ui(self):
        selected_item = self.staff_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No staff member selected.")
            return

        staff_data = self.staff_table.item(selected_item, "values")
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete EmployeeID {staff_data[0]}?")
        if not confirm:
            return

        try:

            Database.delete_staff(int(staff_data[0]))
            messagebox.showinfo("Success", "Staff deleted successfully.")
            self.populate_staff_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete staff: {e}")
