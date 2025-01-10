import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, messagebox, ttk
import re
from utils.database import Database
from utils.encryption import hash_password  # Import hash_password


class ManageStaff:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager  # NavigationManager instance
        self.manage_staff_window = Toplevel(self.parent)
        self.parent.withdraw()  # Hide the parent window
        self.manage_staff_window.title("Manage Staff")
        self.manage_staff_window.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        Label(self.manage_staff_window, text="Manage Staff", font=("Arial", 16)).pack(pady=10)

        # Staff Table
        columns = ("EmployeeID", "FirstName", "Surname", "ContactNumber", "BranchID", "JobRoleID")
        self.staff_table = ttk.Treeview(self.manage_staff_window, columns=columns, show="headings")
        for col in columns:
            self.staff_table.heading(col, text=col)
            self.staff_table.column(col, width=100)
        self.staff_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        Button(self.manage_staff_window, text="Add Staff", command=self.add_staff_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_staff_window, text="Edit Staff", command=self.edit_staff_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_staff_window, text="Delete Staff", command=self.delete_staff_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_staff_window, text="Back",
               command=lambda: self.navigation_manager.back(self.manage_staff_window)).pack(side="left", padx=10, pady=10)

        # Populate Table
        self.populate_staff_table()

    def populate_staff_table(self):
        """Fetch and display all staff records in the table."""
        try:
            records = Database.fetch_all_staff()
            self.staff_table.delete(*self.staff_table.get_children())  # Clear existing rows
            for record in records:
                self.staff_table.insert("", "end", values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch staff records: {e}")

    def validate_and_format_name(self, name):
        """Validate the name and capitalise properly."""
        if not re.match(r"^[a-zA-Z- ]+$", name):  # Allow letters, spaces, and hyphens
            return None
        return " ".join(
            part.capitalize()
            for part in re.split(r"(-| )", name.lower())  # Split by spaces or hyphens
        )

    def validate_contact_number(self, contact):
        """Validate contact number to ensure it is 10-15 digits."""
        return re.match(r"^\d{10,15}$", contact)

    def add_staff_ui(self):
        """Open a form to add a new staff member."""
        add_window = Toplevel(self.manage_staff_window)
        add_window.title("Add Staff")
        add_window.geometry("400x400")

        # Input fields
        fields = ["FirstName", "Surname", "ContactNumber", "BranchID", "JobRoleID", "Password"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(add_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(add_window, show="*" if field == "Password" else None)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        def submit_add():
            try:
                # Collect input data
                new_staff = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in new_staff.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                # Validate and format names
                formatted_first_name = self.validate_and_format_name(new_staff["FirstName"])
                if not formatted_first_name:
                    messagebox.showerror("Error", "Invalid first name. Only letters, spaces, and hyphens are allowed.")
                    return

                formatted_surname = self.validate_and_format_name(new_staff["Surname"])
                if not formatted_surname:
                    messagebox.showerror("Error", "Invalid surname. Only letters, spaces, and hyphens are allowed.")
                    return

                # Validate contact number
                if not self.validate_contact_number(new_staff["ContactNumber"]):
                    messagebox.showerror("Error", "Contact number must be 10-15 digits.")
                    return

                # Hash the password
                hashed_password = hash_password(new_staff["Password"])

                # Call the database function to add staff
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
                self.populate_staff_table()  # Refresh the table
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))  # Display validation errors
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add staff: {e}")

        Button(add_window, text="Submit", command=submit_add).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_staff_ui(self):
        """Open a form to edit the selected staff member."""
        selected_item = self.staff_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No staff member selected.")
            return

        staff_data = self.staff_table.item(selected_item, "values")
        edit_window = Toplevel(self.manage_staff_window)
        edit_window.title("Edit Staff")
        edit_window.geometry("400x300")

        # Editable fields
        fields = ["ContactNumber", "BranchID", "JobRoleID"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(edit_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(edit_window)
            entry.insert(0, staff_data[3 + idx])  # Pre-fill with current data
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        def submit_edit():
            try:
                # Collect updated data
                updates = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in updates.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                # Call the database function to update staff
                Database.update_staff(
                    int(staff_data[0]),  # EmployeeID
                    updates["ContactNumber"],
                    int(updates["BranchID"]),
                    int(updates["JobRoleID"]),
                )
                messagebox.showinfo("Success", "Staff updated successfully.")
                edit_window.destroy()
                self.populate_staff_table()  # Refresh the table
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update staff: {e}")

        Button(edit_window, text="Submit", command=submit_edit).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_staff_ui(self):
        """Delete the selected staff member."""
        selected_item = self.staff_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No staff member selected.")
            return

        staff_data = self.staff_table.item(selected_item, "values")
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete EmployeeID {staff_data[0]}?")
        if not confirm:
            return

        try:
            # Call the database function to delete staff
            Database.delete_staff(int(staff_data[0]))
            messagebox.showinfo("Success", "Staff deleted successfully.")
            self.populate_staff_table()  # Refresh the table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete staff: {e}")
