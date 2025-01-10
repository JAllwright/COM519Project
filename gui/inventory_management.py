import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, messagebox, ttk
from utils.database import Database


class InventoryManagement:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager  # NavigationManager instance
        self.inventory_window = Toplevel(self.parent)
        self.parent.withdraw()  # Hide the parent window
        self.inventory_window.title("Inventory Management")
        self.inventory_window.geometry("800x500")
        self.create_widgets()

    def create_widgets(self):
        Label(self.inventory_window, text="Inventory Management", font=("Arial", 16)).pack(pady=10)

        # Filters Section
        filter_frame = tk.Frame(self.inventory_window)
        filter_frame.pack(pady=10, padx=10, fill="x")

        Label(filter_frame, text="Branch ID:").grid(row=0, column=0, padx=5, pady=5)
        self.branch_filter = Entry(filter_frame)
        self.branch_filter.grid(row=0, column=1, padx=5, pady=5)

        Label(filter_frame, text="Product ID:").grid(row=0, column=2, padx=5, pady=5)
        self.product_filter = Entry(filter_frame)
        self.product_filter.grid(row=0, column=3, padx=5, pady=5)

        Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(row=0, column=4, padx=5, pady=5)
        Button(filter_frame, text="Clear Filters", command=self.clear_filters).grid(row=0, column=5, padx=5, pady=5)

        # Inventory Table
        columns = ("BranchID", "ProductID", "StockQuantity")
        self.inventory_table = ttk.Treeview(self.inventory_window, columns=columns, show="headings")
        for col in columns:
            self.inventory_table.heading(col, text=col)
            self.inventory_table.column(col, width=150)
        self.inventory_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Back Button
        Button(self.inventory_window, text="Back",
               command=lambda: self.navigation_manager.back(self.inventory_window)).pack(pady=10)

        # Populate Table
        self.populate_inventory_table()

    def populate_inventory_table(self, branch_id=None, product_id=None):
        """Fetch and display inventory records, with optional filtering."""
        try:
            records = Database.fetch_inventory(branch_id, product_id)
            self.inventory_table.delete(*self.inventory_table.get_children())  # Clear existing rows
            for record in records:
                self.inventory_table.insert("", "end", values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch inventory: {e}")

    def apply_filters(self):
        """Apply filters for branch and product."""
        branch_id = self.branch_filter.get().strip()
        product_id = self.product_filter.get().strip()

        try:
            branch_id = int(branch_id) if branch_id else None
            product_id = int(product_id) if product_id else None
        except ValueError:
            messagebox.showerror("Error", "Branch ID and Product ID must be numeric.")
            return

        self.populate_inventory_table(branch_id, product_id)

    def clear_filters(self):
        """Clear all filters and display the full inventory."""
        self.branch_filter.delete(0, tk.END)
        self.product_filter.delete(0, tk.END)
        self.populate_inventory_table()
