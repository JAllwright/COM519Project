import tkinter as tk
from tkinter import Toplevel, Label, Button, messagebox, ttk
from utils.database import Database


class ManageCustomers:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager  # NavigationManager instance
        self.manage_customers_window = Toplevel(self.parent)
        self.parent.withdraw()  # Hide the parent window
        self.manage_customers_window.title("Manage Customers")
        self.manage_customers_window.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        Label(self.manage_customers_window, text="Manage Customers", font=("Arial", 16)).pack(pady=10)

        # Customer Table
        columns = ("CustomerID", "FirstName", "Surname", "ContactNumber", "MembershipLevelID")
        self.customer_table = ttk.Treeview(self.manage_customers_window, columns=columns, show="headings")
        for col in columns:
            self.customer_table.heading(col, text=col)
            self.customer_table.column(col, width=100)
        self.customer_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        Button(self.manage_customers_window, text="Edit Customer", command=self.edit_customer_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_customers_window, text="Delete Customer", command=self.delete_customer_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_customers_window, text="Back",
               command=lambda: self.navigation_manager.back(self.manage_customers_window)).pack(side="left", padx=10, pady=10)

        # Populate Table
        self.populate_customer_table()

    def populate_customer_table(self):
        """Fetch and display all customers in the table."""
        try:
            records = Database.fetch_all_customers()
            self.customer_table.delete(*self.customer_table.get_children())  # Clear existing rows
            for record in records:
                self.customer_table.insert("", "end", values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch customers: {e}")

    def edit_customer_ui(self):
        """Open a form to edit the selected customer."""
        selected_item = self.customer_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No customer selected.")
            return

        customer_data = self.customer_table.item(selected_item, "values")
        edit_window = Toplevel(self.manage_customers_window)
        edit_window.title("Edit Customer")
        edit_window.geometry("400x300")

        # Editable fields
        fields = ["ContactNumber", "MembershipLevelID"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(edit_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = tk.Entry(edit_window)
            entry.insert(0, customer_data[3 + idx])  # Pre-fill with current data
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        def submit_edit():
            try:
                # Collect updated data
                updates = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in updates.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                # Call the database function to update customer
                Database.update_customer(
                    int(customer_data[0]),  # CustomerID
                    updates["ContactNumber"],
                    int(updates["MembershipLevelID"]),
                )
                messagebox.showinfo("Success", "Customer updated successfully.")
                edit_window.destroy()
                self.populate_customer_table()  # Refresh the table
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {e}")

        Button(edit_window, text="Submit", command=submit_edit).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_customer_ui(self):
        """Delete the selected customer."""
        selected_item = self.customer_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No customer selected.")
            return

        customer_data = self.customer_table.item(selected_item, "values")
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete CustomerID {customer_data[0]}?")
        if not confirm:
            return

        try:
            # Call the database function to delete customer
            Database.delete_customer(int(customer_data[0]))
            messagebox.showinfo("Success", "Customer deleted successfully.")
            self.populate_customer_table()  # Refresh the table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {e}")
