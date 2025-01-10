import tkinter as tk
from tkinter import Toplevel, Label, Button, StringVar, Entry, messagebox, ttk
import re
from utils.database import Database
from gui.view_past_orders import ViewPastOrders
from gui.view_basket import ViewBasket
from gui.browse_products import BrowseProducts


class CustomerPortal:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.basket = {}
        self.customer_portal_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.customer_portal_window.title("Customer Portal")
        self.customer_portal_window.geometry("500x400")
        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.customer_portal_window.winfo_children():
            widget.destroy()

        Label(self.customer_portal_window, text="Customer Portal", font=("Arial", 16)).pack(pady=10)

        Button(self.customer_portal_window, text="Login", command=self.open_login).pack(pady=10)
        Button(self.customer_portal_window, text="Sign Up", command=self.open_signup).pack(pady=10)
        Button(self.customer_portal_window, text="Back", command=self.back_to_main).pack(pady=10)

    def create_dashboard(self, customer):
        for widget in self.customer_portal_window.winfo_children():
            widget.destroy()

        Label(self.customer_portal_window, text=f"Welcome {customer['FirstName']} {customer['Surname']}",
              font=("Arial", 16)).pack(pady=10)
        Label(self.customer_portal_window, text=f"Membership Level: {customer['MembershipLevelID']}",
              font=("Arial", 12)).pack(pady=5)

        Button(self.customer_portal_window, text="View Past Orders",
               command=lambda: self.navigation_manager.navigate(
                   self.customer_portal_window,
                   ViewPastOrders,
                   self.customer_portal_window,
                   customer["CustomerID"],
                   self.navigation_manager
               )).pack(pady=10)

        Button(self.customer_portal_window, text="View Current Basket",
               command=lambda: self.navigation_manager.navigate(
                   self.customer_portal_window,
                   ViewBasket,
                   self.customer_portal_window,
                   self.basket,
                   self.navigation_manager,
                   customer["CustomerID"]
               )).pack(pady=10)

        Button(self.customer_portal_window, text="Browse Products",
               command=lambda: self.navigation_manager.navigate(
                   self.customer_portal_window,
                   BrowseProducts,
                   self.customer_portal_window,
                   customer["CustomerID"],
                   self.navigation_manager,
                   self.basket,
                   customer["BranchID"]
               )).pack(pady=10)

        Button(self.customer_portal_window, text="Logout", command=self.logout_user).pack(pady=10)

    def logout_user(self):
        try:
            print(f"Basket at logout: {self.basket}")
            for product_id, item in self.basket.items():
                print(f"Processing ProductID={product_id}, Item={item}")
                quantity = item['quantity']
                branch_id = item['branch']

                if not isinstance(branch_id, int):
                    print(f"Invalid BranchID for product {product_id}: {branch_id}")
                    messagebox.showwarning("Warning",
                                           f"Invalid branch for product {product_id}. Skipping stock adjustment.")
                    continue

                try:
                    Database.adjust_stock_quantity(branch_id, product_id, quantity)
                except Exception as e:
                    print(f"Error adjusting stock for ProductID={product_id}, BranchID={branch_id}: {e}")
                    messagebox.showerror("Error", f"Failed to adjust stock for product {product_id}")
                    return

            self.basket.clear()
            messagebox.showinfo("Success", "You have been logged out and stock reinstated.")
        except Exception as e:
            print(f"Error during logout: {e}")
            messagebox.showerror("Error", f"Failed to log out properly: {e}")
        finally:
            self.create_login_screen()

    def open_login(self):
        login_window = Toplevel(self.customer_portal_window)
        self.customer_portal_window.withdraw()
        login_window.title("Customer Login")
        login_window.geometry("400x300")

        email_var = StringVar()
        password_var = StringVar()

        Label(login_window, text="Email").pack(pady=5)
        Entry(login_window, textvariable=email_var).pack(pady=5)
        Label(login_window, text="Password").pack(pady=5)
        Entry(login_window, textvariable=password_var, show="*").pack(pady=5)

        def submit_login():
            email = email_var.get().strip()
            password = password_var.get().strip()
            if not email or not password:
                messagebox.showerror("Error", "Email and password cannot be empty.")
                return

            try:
                customer = Database.authenticate_customer(email, password)
                if customer:
                    messagebox.showinfo("Success", f"Welcome, {customer['FirstName']}!")
                    login_window.destroy()
                    self.customer_portal_window.deiconify()
                    self.create_dashboard(customer)
                else:
                    messagebox.showerror("Error", "Invalid Email or Password.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to login: {e}")

        Button(login_window, text="Login", command=submit_login).pack(pady=10)
        Button(login_window, text="Back", command=lambda: self.back_to_customer_portal(login_window)).pack(pady=10)

    def open_signup(self):
        signup_window = Toplevel(self.customer_portal_window)
        self.customer_portal_window.withdraw()
        signup_window.title("Sign Up")
        signup_window.geometry("400x500")

        fields = ["First Name", "Last Name", "Email", "Password", "Contact Number"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(signup_window, text=field).pack(pady=5)
            entry = Entry(signup_window, show="*" if field == "Password" else None)
            entry.pack(pady=5)
            entries[field] = entry

        Label(signup_window, text="Membership Level").pack(pady=5)
        membership_level_var = StringVar(value="1")
        membership_dropdown = tk.OptionMenu(signup_window, membership_level_var, "1", "2")
        membership_dropdown.pack(pady=5)

        Label(signup_window, text="Branch").pack(pady=5)
        branch_var = StringVar()
        branches = Database.fetch_all_branches()
        branch_dropdown = ttk.Combobox(signup_window, textvariable=branch_var, values=branches, state="readonly")
        branch_dropdown.pack(pady=5)

        def validate_and_format_name(name):
            if not re.match(r"^[a-zA-Z- ]+$", name):
                return None
            return " ".join(
                part.capitalize()
                for part in re.split(r"(-| )", name.lower())
            )

        def validate_email(email):
            return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

        def validate_contact_number(contact):
            return re.match(r"^\d{10,15}$", contact)

        def submit_signup():
            try:
                data = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in data.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                formatted_first_name = validate_and_format_name(data["First Name"])
                if not formatted_first_name:
                    messagebox.showerror("Error", "Invalid first name. Only letters, spaces, and hyphens are allowed.")
                    return

                formatted_last_name = validate_and_format_name(data["Last Name"])
                if not formatted_last_name:
                    messagebox.showerror("Error", "Invalid last name. Only letters, spaces, and hyphens are allowed.")
                    return

                if not validate_email(data["Email"]):
                    messagebox.showerror("Error", "Invalid email address.")
                    return

                if not validate_contact_number(data["Contact Number"]):
                    messagebox.showerror("Error", "Contact number must be 10-15 digits.")
                    return

                branch_selection = branch_var.get()
                if not branch_selection:
                    messagebox.showerror("Error", "Please select a branch.")
                    return

                branch_id = int(branch_selection.split(" - ")[0])

                membership_level_id = int(membership_level_var.get())

                Database.signup_customer(
                    formatted_first_name,
                    formatted_last_name,
                    data["Contact Number"],
                    membership_level_id,
                    data["Email"],
                    data["Password"],
                    branch_id
                )
                messagebox.showinfo("Success", "Account created successfully.")
                self.back_to_customer_portal(signup_window)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to sign up: {e}")

        Button(signup_window, text="Submit", command=submit_signup).pack(pady=10)
        Button(signup_window, text="Back", command=lambda: self.back_to_customer_portal(signup_window)).pack(pady=10)

    def back_to_customer_portal(self, window):
        window.destroy()
        self.customer_portal_window.deiconify()

    def back_to_main(self):
        self.navigation_manager.back(self.customer_portal_window)
