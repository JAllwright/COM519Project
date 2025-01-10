import io
import tkinter as tk
from tkinter import Toplevel, Label, Button, Entry, messagebox, StringVar, ttk, Frame, Canvas, Scrollbar
from PIL import Image, ImageTk
from utils.database import Database


class PlaceOrders:
    def __init__(self, parent, navigation_manager):
        self.parent = parent
        self.navigation_manager = navigation_manager
        self.branch_id = None
        self.supplier_id = None
        self.place_orders_window = Toplevel(self.parent)
        self.parent.withdraw()
        self.place_orders_window.title("Place Orders")
        self.place_orders_window.geometry("800x600")
        self.create_branch_and_supplier_selection()

    def create_branch_and_supplier_selection(self):
        Label(self.place_orders_window, text="Select Branch and Supplier to Place Orders", font=("Arial", 14)).pack(pady=10)

        branch_var = StringVar()
        supplier_var = StringVar()


        try:
            branches = Database.fetch_all_branches()
            if not branches:
                messagebox.showerror("Error", "No branches available.")
                self.navigation_manager.back(self.place_orders_window)
                return

            branch_dropdown = ttk.Combobox(self.place_orders_window, textvariable=branch_var, values=branches, state="readonly")
            branch_dropdown.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch branches: {e}")
            self.navigation_manager.back(self.place_orders_window)
            return

        try:
            suppliers = Database.fetch_all_suppliers()
            if not suppliers:
                messagebox.showerror("Error", "No suppliers available.")
                self.navigation_manager.back(self.place_orders_window)
                return

            supplier_dropdown = ttk.Combobox(self.place_orders_window, textvariable=supplier_var, values=[f"{s[0]} - {s[1]}" for s in suppliers], state="readonly")
            supplier_dropdown.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch suppliers: {e}")
            self.navigation_manager.back(self.place_orders_window)
            return

        def proceed_to_products():
            selected_branch = branch_var.get()
            selected_supplier = supplier_var.get()
            if not selected_branch or not selected_supplier:
                messagebox.showerror("Error", "Please select both a branch and a supplier.")
                return

            self.branch_id = int(selected_branch.split(" - ")[0])
            self.supplier_id = int(selected_supplier.split(" - ")[0])
            self.create_product_browsing()

        Button(self.place_orders_window, text="Proceed", command=proceed_to_products).pack(pady=10)

    def create_product_browsing(self):
        for widget in self.place_orders_window.winfo_children():
            widget.destroy()

        Label(self.place_orders_window, text="Browse Products", font=("Arial", 16)).pack(pady=10)

        filter_frame = tk.Frame(self.place_orders_window)
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

        results_label = Label(self.place_orders_window, text="", font=("Arial", 12))
        results_label.pack(pady=10)

        product_frame = Frame(self.place_orders_window)
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
                products = Database.fetch_supplier_products(
                    supplier_id=self.supplier_id,
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
                            image_data = product[-1]
                            image = Image.open(io.BytesIO(image_data))
                            image.thumbnail((100, 100))
                            photo = ImageTk.PhotoImage(image)
                            image_label = Label(product_frame, image=photo)
                            image_label.image = photo
                            image_label.pack(side="left", padx=10)
                        except Exception as e:
                            print(f"Error displaying image: {e}")
                            Label(product_frame, text="No Image", font=("Arial", 10)).pack(side="left", padx=10)

                    info_frame = Frame(product_frame)
                    info_frame.pack(side="left", fill="x", expand=True)

                    Label(info_frame, text=product[1], font=("Arial", 14, "bold")).pack(anchor="w")
                    Label(info_frame, text=f"Price: £{product[2]:.2f}", font=("Arial", 12)).pack(anchor="w")
                    Label(info_frame, text=f"ProductID: {product[0]} | CategoryID: {product[3]}",
                          font=("Arial", 10)).pack(anchor="w")

                    Button(info_frame, text="Place Order", command=lambda p=product: place_order(p)).pack(anchor="e")


            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch products: {e}")

        def place_order(product):
            quantity_var = StringVar()

            def submit_quantity():
                try:
                    quantity_text = quantity_var.get().strip()

                    print(f"Quantity Text: {quantity_text}")


                    if not quantity_text:
                        messagebox.showerror("Error", "Quantity cannot be empty.")
                        return

                    quantity = int(quantity_text)

                    print(f"Quantity (after conversion): {quantity}")
                    if quantity < 1:
                        messagebox.showerror("Error", "Quantity must be a positive integer (1).")
                        return

                    Database.place_order(
                        branch_id=self.branch_id,
                        supplier_id=self.supplier_id,
                        product_id=product[0],
                        quantity=quantity,
                    )
                    messagebox.showinfo("Success", "Order placed successfully.")
                    quantity_window.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Quantity must be a positive integer (2).")

            quantity_window = Toplevel(self.place_orders_window)
            quantity_window.title("Enter Quantity")
            Label(quantity_window, text="Enter Quantity:").pack(pady=5)
            Entry(quantity_window, textvariable=quantity_var).pack(pady=5)
            Button(quantity_window, text="Place Order", command=submit_quantity).pack(pady=10)

        populate_products_list()

        Button(self.place_orders_window, text="Back", command=lambda: self.navigation_manager.back(self.place_orders_window)).pack(pady=10)
