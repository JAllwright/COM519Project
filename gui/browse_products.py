import io
import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, messagebox, StringVar, ttk, Frame, Scrollbar, Canvas
from PIL import Image, ImageTk
from utils.database import Database


class BrowseProducts:
    def __init__(self, parent, customer_id, navigation_manager, basket, branch_id):
        self.parent = parent
        self.customer_id = customer_id
        self.navigation_manager = navigation_manager
        self.branch_id = branch_id  # Directly use the customer's branch ID
        self.basket = basket  # Pass the shared basket
        self.browse_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.browse_window.title("Browse Products")
        self.browse_window.geometry("800x600")

        # Skip branch selection and go directly to browsing products
        self.create_product_browsing()

    def create_product_browsing(self):
        for widget in self.browse_window.winfo_children():
            widget.destroy()

        Label(self.browse_window, text="Browse Products", font=("Arial", 16)).pack(pady=10)

        # Filters and search
        filter_frame = tk.Frame(self.browse_window)
        filter_frame.pack(pady=10, padx=10, fill="x")

        search_var = StringVar()
        category_var = StringVar()
        min_price_var = StringVar()
        max_price_var = StringVar()

        Label(filter_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5)
        Entry(filter_frame, textvariable=search_var).grid(row=0, column=1, padx=5, pady=5)

        Label(filter_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
        category_dropdown = ttk.Combobox(filter_frame, textvariable=category_var, state="readonly")
        category_dropdown.grid(row=0, column=3, padx=5, pady=5)

        Label(filter_frame, text="Min Price:").grid(row=1, column=0, padx=5, pady=5)
        Entry(filter_frame, textvariable=min_price_var).grid(row=1, column=1, padx=5, pady=5)

        Label(filter_frame, text="Max Price:").grid(row=1, column=2, padx=5, pady=5)
        Entry(filter_frame, textvariable=max_price_var).grid(row=1, column=3, padx=5, pady=5)

        Button(filter_frame, text="Apply Filters", command=lambda: populate_products_list()).grid(row=2, column=0, columnspan=4, pady=10)

        try:
            categories = Database.fetch_all_categories()
            category_dropdown["values"] = [category[1] for category in categories]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch categories: {e}")

        # Product display area
        results_label = Label(self.browse_window, text="", font=("Arial", 12))
        results_label.pack(pady=10)

        product_frame = Frame(self.browse_window)
        product_frame.pack(fill="both", expand=True)

        canvas = Canvas(product_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(product_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        inner_frame = Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def populate_products_list():
            for widget in inner_frame.winfo_children():
                widget.destroy()

            search = search_var.get().strip()
            selected_category = category_var.get().strip()
            category_id = None
            if selected_category:
                category_id = next((category[0] for category in categories if category[1] == selected_category), None)
            min_price = float(min_price_var.get()) if min_price_var.get().strip() else None
            max_price = float(max_price_var.get()) if max_price_var.get().strip() else None

            try:
                products = Database.fetch_available_products(
                    branch_id=self.branch_id,  # Filter by the customer's branch
                    search=search,
                    category_id=category_id,
                    min_price=min_price,
                    max_price=max_price,
                )
                results_label.config(text=f"{len(products)} results found.")

                for product in products:
                    product_frame = Frame(inner_frame, borderwidth=1, relief="solid", pady=10, padx=10)
                    product_frame.pack(fill="x", pady=5)

                    if product[-1]:
                        try:
                            image_data = io.BytesIO(product[-1])
                            image = Image.open(image_data)
                            image.thumbnail((100, 100))
                            photo = ImageTk.PhotoImage(image)
                            image_label = Label(product_frame, image=photo)
                            image_label.image = photo
                            image_label.pack(side="left", padx=10)
                        except Exception as e:
                            print(f"Error displaying image for ProductID {product[0]}: {e}")
                            Label(product_frame, text="No Image", font=("Arial", 10)).pack(side="left", padx=10)
                    else:
                        Label(product_frame, text="No Image", font=("Arial", 10)).pack(side="left", padx=10)

                    info_frame = Frame(product_frame)
                    info_frame.pack(side="left", fill="x", expand=True)

                    Label(info_frame, text=product[1], font=("Arial", 14, "bold")).pack(anchor="w")
                    Label(info_frame, text=f"Price: £{product[3]:.2f}", font=("Arial", 12)).pack(anchor="w")
                    Label(info_frame, text=f"ProductID: {product[0]} | CategoryID={product[4]} | Stock={product[2]}",
                          font=("Arial", 10)).pack(anchor="w")

                    Button(info_frame, text="Add to Basket", command=lambda p=product: self.open_quantity_dialog(p)).pack(anchor="e")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch products: {e}")

        populate_products_list()

        Button(self.browse_window, text="Back", command=lambda: self.navigation_manager.back(self.browse_window)).pack(pady=10)

    def open_quantity_dialog(self, product):
        quantity_window = Toplevel(self.browse_window)
        quantity_window.title("Enter Quantity")
        Label(quantity_window, text="Enter Quantity:").pack(pady=5)

        quantity_var = StringVar()
        Entry(quantity_window, textvariable=quantity_var).pack(pady=5)

        def submit_quantity():
            try:
                quantity = int(quantity_var.get())
                if quantity < 1 or quantity > product[2]:
                    messagebox.showerror("Error", "Invalid quantity.")
                    return

                self.add_to_basket(product, quantity)
                quantity_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid integer quantity.")

        Button(quantity_window, text="Add", command=submit_quantity).pack(pady=10)

    def add_to_basket(self, product, quantity):
        """Add a product to the in-memory basket and adjust stock."""
        product_id = product[0]
        branch_id = self.branch_id

        # Check stock availability
        try:
            stock_quantity = Database.fetch_stock_quantity(branch_id, product_id)
            if stock_quantity < quantity:
                messagebox.showerror("Error", "Insufficient stock.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch stock: {e}")
            return

        # Adjust stock in the database
        try:
            Database.adjust_stock_quantity(branch_id, product_id, -quantity)  # Reduce stock
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {e}")
            return

        # Update in-memory basket
        if product_id in self.basket:
            self.basket[product_id]['quantity'] += quantity
        else:
            self.basket[product_id] = {'product': product, 'quantity': quantity, 'branch': branch_id}

        print(f"Basket after adding: {self.basket}")  # Debugging
        messagebox.showinfo("Success", f"Added {quantity} of {product[1]} to basket.")
