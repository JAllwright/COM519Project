from tkinter import Toplevel, Label, ttk, Button, messagebox
from utils.database import Database

class ViewPastOrders:
    def __init__(self, parent, customer_id, navigation_manager):
        self.parent = parent
        self.customer_id = customer_id
        self.navigation_manager = navigation_manager
        self.past_orders_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.past_orders_window.title("Past Orders")
        self.past_orders_window.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        Label(self.past_orders_window, text="Past Orders", font=("Arial", 16)).pack(pady=10)

        columns = ("OrderID", "ProductName", "OrderQuantity", "TotalPrice", "OrderDate")
        orders_table = ttk.Treeview(self.past_orders_window, columns=columns, show="headings")
        for col in columns:
            orders_table.heading(col, text=col)
            orders_table.column(col, width=100)
        orders_table.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            # Fetch past orders for the customer
            orders = Database.fetch_past_orders(self.customer_id)
            for order in orders:
                orders_table.insert("", "end", values=order)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch past orders: {e}")

        Button(self.past_orders_window, text="Back",
               command=lambda: self.navigation_manager.back(self.past_orders_window)).pack(pady=10)
