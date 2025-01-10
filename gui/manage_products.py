import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, messagebox, ttk, filedialog
from utils.database import Database
import os

class ManageProducts:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager  # NavigationManager instance
        self.manage_products_window = Toplevel(self.parent)
        self.parent.withdraw()  # Hide the parent window
        self.manage_products_window.title("Manage Products")
        self.manage_products_window.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        Label(self.manage_products_window, text="Manage Products", font=("Arial", 16)).pack(pady=10)

        # Product Table
        columns = ("ProductID", "ProductName", "CategoryID", "Price")
        self.product_table = ttk.Treeview(self.manage_products_window, columns=columns, show="headings")
        for col in columns:
            self.product_table.heading(col, text=col)
            self.product_table.column(col, width=150)
        self.product_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        Button(self.manage_products_window, text="Add Product", command=self.add_product_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_products_window, text="Edit Product", command=self.edit_product_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_products_window, text="Delete Product", command=self.delete_product_ui).pack(side="left", padx=10, pady=10)
        Button(self.manage_products_window, text="Back",
               command=lambda: self.navigation_manager.back(self.manage_products_window)).pack(side="left", padx=10, pady=10)

        # Populate Table
        self.populate_product_table()

    def populate_product_table(self):
        """Fetch and display all products in the table."""
        try:
            records = Database.fetch_all_products()
            self.product_table.delete(*self.product_table.get_children())  # Clear existing rows
            for record in records:
                self.product_table.insert("", "end", values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch products: {e}")

    def add_product_ui(self):
        """Open a form to add a new product."""
        add_window = Toplevel(self.manage_products_window)
        add_window.title("Add Product")
        add_window.geometry("400x400")

        # Input fields
        fields = ["ProductName", "CategoryID", "Price"]
        entries = {}
        product_image_path = tk.StringVar()

        for idx, field in enumerate(fields):
            Label(add_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(add_window)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        # Image upload
        def upload_image():
            filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
            if filepath:
                product_image_path.set(filepath)
                messagebox.showinfo("Success", f"Image selected: {os.path.basename(filepath)}")

        Label(add_window, text="Product Image (Optional)").grid(row=len(fields), column=0, padx=10, pady=5)
        Button(add_window, text="Upload Image", command=upload_image).grid(row=len(fields), column=1, padx=10, pady=5)

        def submit_add():
            try:
                # Collect input data
                new_product = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in new_product.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                # Read the image data if uploaded
                image_data = None
                if product_image_path.get():
                    with open(product_image_path.get(), "rb") as file:
                        image_data = file.read()

                # Call the database function to add product
                Database.add_product(
                    new_product["ProductName"],
                    int(new_product["CategoryID"]),
                    float(new_product["Price"]),
                    image_data  # Pass image data
                )
                messagebox.showinfo("Success", "Product added successfully.")
                add_window.destroy()
                self.populate_product_table()  # Refresh the table
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")

        Button(add_window, text="Submit", command=submit_add).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

    def edit_product_ui(self):
        """Open a form to edit the selected product."""
        selected_item = self.product_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No product selected.")
            return

        product_data = self.product_table.item(selected_item, "values")
        edit_window = Toplevel(self.manage_products_window)
        edit_window.title("Edit Product")
        edit_window.geometry("400x300")

        # Editable fields
        fields = ["CategoryID", "Price"]
        entries = {}

        for idx, field in enumerate(fields):
            Label(edit_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(edit_window)
            entry.insert(0, product_data[2 + idx])  # Pre-fill with current data
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        def submit_edit():
            try:
                # Collect updated data
                updates = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in updates.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                # Call the database function to update product
                Database.update_product(
                    int(product_data[0]),  # ProductID
                    int(updates["CategoryID"]),
                    float(updates["Price"]),
                )
                messagebox.showinfo("Success", "Product updated successfully.")
                edit_window.destroy()
                self.populate_product_table()  # Refresh the table
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")

        Button(edit_window, text="Submit", command=submit_edit).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_product_ui(self):
        """Delete the selected product."""
        selected_item = self.product_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No product selected.")
            return

        product_data = self.product_table.item(selected_item, "values")
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ProductID {product_data[0]}?")
        if not confirm:
            return

        try:
            # Call the database function to delete product
            Database.delete_product(int(product_data[0]))
            messagebox.showinfo("Success", "Product deleted successfully.")
            self.populate_product_table()  # Refresh the table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {e}")

    def edit_product_ui(self):
        """Open a form to edit the selected product."""
        selected_item = self.product_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "No product selected.")
            return

        product_data = self.product_table.item(selected_item, "values")
        edit_window = Toplevel(self.manage_products_window)
        edit_window.title("Edit Product")
        edit_window.geometry("400x400")

        # Editable fields
        fields = ["CategoryID", "Price"]
        entries = {}
        product_image_path = tk.StringVar()

        for idx, field in enumerate(fields):
            Label(edit_window, text=field).grid(row=idx, column=0, padx=10, pady=5)
            entry = Entry(edit_window)
            entry.insert(0, product_data[2 + idx])  # Pre-fill with current data
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

        # Image upload
        def upload_image():
            filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
            if filepath:
                product_image_path.set(filepath)
                messagebox.showinfo("Success", f"Image selected: {os.path.basename(filepath)}")

        Label(edit_window, text="Product Image (Optional)").grid(row=len(fields), column=0, padx=10, pady=5)
        Button(edit_window, text="Upload Image", command=upload_image).grid(row=len(fields), column=1, padx=10, pady=5)

        def submit_edit():
            try:
                # Collect updated data
                updates = {field: entries[field].get().strip() for field in fields}
                if any(not value for value in updates.values()):
                    messagebox.showerror("Error", "All fields must be filled.")
                    return

                # Read the image data if uploaded
                image_data = None
                if product_image_path.get():
                    with open(product_image_path.get(), "rb") as file:
                        image_data = file.read()

                # Call the database function to update product
                Database.update_product(
                    int(product_data[0]),  # ProductID
                    int(updates["CategoryID"]),
                    float(updates["Price"]),
                )

                if image_data:
                    Database.update_product_image(int(product_data[0]), image_data)

                messagebox.showinfo("Success", "Product updated successfully.")
                edit_window.destroy()
                self.populate_product_table()  # Refresh the table
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")

        Button(edit_window, text="Submit", command=submit_edit).grid(row=len(fields) + 1, column=0, columnspan=2,
                                                                     pady=10)
