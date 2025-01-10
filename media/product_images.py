import sqlite3
from tkinter import filedialog, messagebox
import os

class ProductImages:
    @staticmethod
    def save_image_to_database(product_id):
        """Saves an image file as a BLOB in the Products table."""
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if not filepath:
            messagebox.showwarning("Warning", "No file selected.")
            return

        with open(filepath, "rb") as file:
            blob_data = file.read()

        conn = sqlite3.connect("database/autodatabase.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE Products SET ProductImage = ? WHERE ProductID = ?", (blob_data, product_id))
            conn.commit()
            messagebox.showinfo("Success", "Image saved successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
        finally:
            conn.close()

    @staticmethod
    def retrieve_image_from_database(product_id, save_folder="media/product_images"):
        """Retrieves an image file from the database and saves it locally."""
        conn = sqlite3.connect("database/autodatabase.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT ProductImage FROM Products WHERE ProductID = ?", (product_id,))
            result = cursor.fetchone()
            if not result or not result[0]:
                messagebox.showwarning("Warning", "No image found for this product.")
                return

            os.makedirs(save_folder, exist_ok=True)
            filepath = os.path.join(save_folder, f"product_{product_id}.jpg")
            with open(filepath, "wb") as file:
                file.write(result[0])
            messagebox.showinfo("Success", f"Image saved to {filepath}.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to retrieve image: {e}")
        finally:
            conn.close()
