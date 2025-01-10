import tkinter as tk

from tkinter import StringVar, Toplevel, Label, ttk, Button, messagebox, StringVar

from utils.database import Database

class ViewBasket:
    def __init__(self, parent, basket, navigation_manager, customer_id):
        self.parent = parent
        self.basket = basket  # Pass the basket dictionary
        self.navigation_manager = navigation_manager
        self.customer_id = customer_id  # Store the customer_id
        self.basket_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.basket_window.title("Current Basket")
        self.basket_window.geometry("700x400")  # Adjusted for the additional column
        print(f"Basket content at ViewBasket init: {self.basket}")  # Debugging
        self.create_widgets()

    def create_widgets(self):
        Label(self.basket_window, text="Current Basket", font=("Arial", 16)).pack(pady=10)

        columns = ("ProductID", "ProductName", "Quantity", "TotalPrice")
        self.basket_table = ttk.Treeview(self.basket_window, columns=columns, show="headings")
        for col in columns:
            self.basket_table.heading(col, text=col)
            self.basket_table.column(col, width=150)
        self.basket_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Calculate and display total price
        total_price = 0
        for product_id, item in self.basket.items():
            product = item['product']
            quantity = item['quantity']
            price = product[3] * quantity
            self.basket_table.insert("", "end", values=(product_id, product[1], quantity, f"£{price:.2f}"))
            total_price += price

        self.total_price_label = Label(self.basket_window, text=f"Total: £{total_price:.2f}", font=("Arial", 12))
        self.total_price_label.pack(pady=10)

        Button(self.basket_window, text="Checkout", command=self.checkout).pack(pady=10)
        Button(self.basket_window, text="Back", command=self.go_back).pack(pady=10)

    def go_back(self):
        """Navigate back to the previous window."""
        self.basket_window.destroy()  # Close the basket window
        self.parent.deiconify()  # Show the parent window

    def checkout(self):
        try:
            if not self.basket:
                messagebox.showinfo("Notice", "Your basket is empty.")
                return

            try:
                # Process checkout for all items in the basket
                order_id = Database.add_customer_order(self.customer_id, self.basket)

                # Clear the basket after successful checkout
                self.basket.clear()

                # Notify the user of the successful order
                messagebox.showinfo("Success", f"Checkout completed successfully. Order ID: {order_id}")
                self.refresh_basket()  # Refresh the basket display

            except Exception as e:
                print(f"Error during checkout processing: {e}")
                messagebox.showerror("Error", f"Failed to complete checkout: {e}")

        except Exception as e:
            print(f"Error during checkout: {e}")
            messagebox.showerror("Error", f"Failed to checkout: {e}")

    def clear_basket(self, branch_id):
        """Remove items from the basket for the selected branch."""
        try:
            # Filter out items from the selected branch
            self.basket = {pid: item for pid, item in self.basket.items() if item['branch'] != branch_id}
            print(f"Basket after clearing for BranchID={branch_id}: {self.basket}")  # Debugging output
        except Exception as e:
            print(f"Error while clearing basket: {e}")

    def process_checkout(self, branch_id):
        """Process the checkout for a specific branch."""
        try:
            # Filter basket items for the selected branch
            branch_items = {pid: item for pid, item in self.basket.items() if item['branch'] == branch_id}

            if not branch_items:
                messagebox.showerror("Error", "No items in basket for the selected branch.")
                return

            # Insert orders into CustomerOrders table
            for product_id, item in branch_items.items():
                Database.add_customer_order(
                    customer_id=self.customer_id,
                    branch_id=branch_id,
                    product_id=product_id,
                    quantity=item['quantity']
                )

            # Remove items from the basket for the selected branch
            self.basket = {pid: item for pid, item in self.basket.items() if item['branch'] != branch_id}

            messagebox.showinfo("Success", f"Checkout completed for branch ID: {branch_id}.")
            self.go_back()

        except Exception as e:
            print(f"Error during process_checkout: {e}")
            messagebox.showerror("Error", f"Failed to checkout: {e}")

    def refresh_basket(self):
        """Refresh the basket display in the Treeview widget."""
        # Clear the Treeview widget
        for item in self.basket_table.get_children():
            self.basket_table.delete(item)

        # Re-add items from the basket
        total_price = 0
        for product_id, item in self.basket.items():
            product = item['product']
            quantity = item['quantity']
            price = product[3] * quantity
            self.basket_table.insert("", "end", values=(product_id, product[1], quantity, f"£{price:.2f}"))
            total_price += price

        # Update the total price label
        self.total_price_label.config(text=f"Total: £{total_price:.2f}")
