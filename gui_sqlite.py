import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
from cryptography.fernet import Fernet
from custom_xml_utils.etree.ElementTree import Element, tostring, fromstring

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Database connection
def connect_db():
    return sqlite3.connect('database/autodatabase.db')

# Insert data
def insert_customer(name, email, membership_level):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (FirstName, Email, MembershipLevelID) VALUES (?, ?, ?)",
                       (name, email, membership_level))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error adding customer: {str(e)}")

# GUI setup
def setup_gui():
    root = tk.Tk()
    root.title("AutoFlix Management System")

    # Customer Management Frame
    customer_frame = ttk.LabelFrame(root, text="Customer Management")
    customer_frame.grid(row=0, column=0, padx=10, pady=10)

    ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(customer_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(customer_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
    email_entry = ttk.Entry(customer_frame)
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(customer_frame, text="Membership Level:").grid(row=2, column=0, padx=5, pady=5)
    membership_entry = ttk.Entry(customer_frame)
    membership_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(customer_frame, text="Add Customer",
               command=lambda: insert_customer(name_entry.get(), email_entry.get(), membership_entry.get())).grid(row=3, column=0, columnspan=2, pady=10)

    root.mainloop()

setup_gui()

def validate_customer_input(name, email, membership_level):
    if not name.isalpha():
        raise ValueError("Name must contain only letters.")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email format.")
    if membership_level not in ["1", "2"]:  # Assuming 1: Standard, 2: Premium
        raise ValueError("Invalid membership level.")

def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data):
    return cipher.decrypt(data.encode()).decode()

def upload_image(product_id):
    filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png")])
    if filepath:
        with open(filepath, 'rb') as file:
            image_blob = file.read()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Products SET Image = ? WHERE ProductID = ?", (image_blob, product_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Image uploaded successfully!")

def export_to_xml():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    rows = cursor.fetchall()

    root = Element("Customers")
    for row in rows:
        customer = Element("Customer")
        root.append(customer)
        Element("ID").text = str(row[0])
        Element("Name").text = row[1]
        Element("Email").text = row[2]

    with open("customers.custom_xml_utils", "wb") as file:
        file.write(tostring(root))
    conn.close()
