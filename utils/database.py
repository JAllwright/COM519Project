import sqlite3
import os

from utils.encryption import hash_password, verify_password


class Database:
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/autodatabase.db"))

    @staticmethod
    def connect():
        conn = sqlite3.connect(Database.DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def fetch_all_staff():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT EmployeeID, FirstName, Surname, ContactNumber, BranchID, JobRoleID FROM Employees")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def add_staff(first_name, surname, contact_number, branch_id, job_role_id, hashed_password):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM Branches WHERE BranchID = ?", (branch_id,))
            if not cursor.fetchone():
                raise ValueError(f"BranchID {branch_id} does not exist.")

            cursor.execute("SELECT 1 FROM JobRoles WHERE JobRoleID = ?", (job_role_id,))
            if not cursor.fetchone():
                raise ValueError(f"JobRoleID {job_role_id} does not exist.")

            cursor.execute("""
                INSERT INTO Employees (FirstName, Surname, ContactNumber, BranchID, JobRoleID, Password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (first_name, surname, contact_number, branch_id, job_role_id, hashed_password))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_staff(employee_id, contact_number, branch_id, job_role_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Employees
                SET ContactNumber = ?, BranchID = ?, JobRoleID = ?
                WHERE EmployeeID = ?
            """, (contact_number, branch_id, job_role_id, employee_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_order(order_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM CustomerOrders WHERE OrderID = ?", (order_id,))
            cursor.execute("DELETE FROM Orders WHERE OrderID = ?", (order_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_staff(employee_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Employees WHERE EmployeeID = ?", (employee_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_all_customers():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CustomerID, FirstName, Surname, ContactNumber, MembershipLevelID FROM Customers")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def update_customer(customer_id, contact_number, membership_level_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Customers
                SET ContactNumber = ?, MembershipLevelID = ?
                WHERE CustomerID = ?
            """, (contact_number, membership_level_id, customer_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_customer(customer_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Customers WHERE CustomerID = ?", (customer_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_all_products():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ProductID, ProductName, CategoryID, Price FROM Products")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def fetch_supplier_products(supplier_id, search=None, category_id=None, min_price=None, max_price=None):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            query = """
                SELECT 
                    p.ProductID, 
                    p.ProductName, 
                    p.Price, 
                    p.CategoryID, 
                    p.ProductImage
                FROM Products p
                JOIN SupplierProducts sp ON p.ProductID = sp.ProductID
                WHERE sp.SupplierID = ?
            """
            params = [supplier_id]

            if search:
                query += " AND p.ProductName LIKE ?"
                params.append(f"%{search}%")

            if category_id:
                query += " AND p.CategoryID = ?"
                params.append(category_id)

            if min_price is not None:
                query += " AND p.Price >= ?"
                params.append(min_price)

            if max_price is not None:
                query += " AND p.Price <= ?"
                params.append(max_price)

            cursor.execute(query, params)
            results = cursor.fetchall()

            processed_results = []
            for result in results:
                product_id, product_name, price, category_id, product_image = result
                processed_results.append((product_id, product_name, price, category_id, product_image))
            return processed_results
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
        finally:
            conn.close()

    @staticmethod
    def fetch_all_suppliers():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SupplierID, SupplierName FROM Suppliers")
            return [(row[0], row[1]) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
        finally:
            conn.close()

    @staticmethod
    def place_order(branch_id, supplier_id, product_id, quantity):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO BranchOrders (BranchID, SupplierID, ProductID, OrderQuantity, OrderDate)
                VALUES (?, ?, ?, ?, DATE('now'))
                """,
                (branch_id, supplier_id, product_id, quantity),
            )
            print(
                f"DEBUG: Order placed for BranchID={branch_id}, SupplierID={supplier_id}, ProductID={product_id}, Quantity={quantity}"
            )

            cursor.execute("SELECT 1 FROM Branches WHERE BranchID = ?", (branch_id,))
            if not cursor.fetchone():
                raise ValueError(f"Invalid BranchID: {branch_id}")

            cursor.execute("SELECT 1 FROM Products WHERE ProductID = ?", (product_id,))
            if not cursor.fetchone():
                raise ValueError(f"Invalid ProductID: {product_id}")

            print(
                f"DEBUG: Preparing to update BranchStock with BranchID={branch_id}, ProductID={product_id}, StockQuantity={quantity}"
            )
            cursor.execute(
                """
                INSERT INTO BranchStock (BranchID, ProductID, StockQuantity)
                VALUES (?, ?, ?)
                ON CONFLICT(BranchID, ProductID) DO UPDATE SET StockQuantity = StockQuantity + ?
                """,
                (branch_id, product_id, quantity, quantity),
            )
            print("DEBUG: BranchStock update successful.")
            conn.commit()
        except sqlite3.Error as e:
            print(f"ERROR: {e}")
            raise ValueError(f"Database error: {e}")
        finally:
            conn.close()
    @staticmethod
    def add_product(product_name, category_id, price, product_image=None):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Products (ProductName, CategoryID, Price, ProductImage)
                VALUES (?, ?, ?, ?)
            """, (product_name, category_id, price, product_image))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_product(product_id, category_id, price):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Products
                SET CategoryID = ?, Price = ?
                WHERE ProductID = ?
            """, (category_id, price, product_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_product(product_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_inventory(branch_id=None, product_id=None):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            query = "SELECT BranchID, ProductID, StockQuantity FROM BranchStock WHERE 1=1"
            params = []

            if branch_id is not None:
                query += " AND BranchID = ?"
                params.append(branch_id)

            if product_id is not None:
                query += " AND ProductID = ?"
                params.append(product_id)

            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    from utils.encryption import hash_password

    @staticmethod
    def signup_customer(first_name, surname, contact_number, membership_level_id, email, password, branch_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            cursor.execute("""
                INSERT INTO Customers (FirstName, Surname, ContactNumber, MembershipLevelID, Email, Password, BranchID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (first_name, surname, contact_number, membership_level_id, email, hashed_password, branch_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    from utils.encryption import verify_password

    @staticmethod
    def authenticate_customer(email, entered_password):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT CustomerID, FirstName, Surname, MembershipLevelID, Password, BranchID
                FROM Customers
                WHERE Email = ?
            """, (email,))
            result = cursor.fetchone()
            if result:
                customer_id, first_name, surname, membership_level_id, stored_password, branch_id = result
                if verify_password(stored_password, entered_password):
                    return {
                        "CustomerID": customer_id,
                        "FirstName": first_name,
                        "Surname": surname,
                        "MembershipLevelID": membership_level_id,
                        "BranchID": branch_id,
                    }
                else:
                    return None
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_all_supplier_orders():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT OrderID, BranchID, SupplierID, ProductID, OrderQuantity, OrderDate, DeliveryDate
                FROM BranchOrders
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def add_supplier_order(branch_id, supplier_id, product_id, order_quantity, order_date):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO BranchOrders (BranchID, SupplierID, ProductID, OrderQuantity, OrderDate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (branch_id, supplier_id, product_id, order_quantity, order_date))

            cursor.execute("""
                INSERT INTO BranchStock (BranchID, ProductID, StockQuantity)
                VALUES (?, ?, ?)
                ON CONFLICT(BranchID, ProductID) DO UPDATE SET StockQuantity = StockQuantity + ?
            """, (branch_id, product_id, order_quantity, order_quantity))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_supplier_order(order_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT BranchID, ProductID, OrderQuantity FROM BranchOrders WHERE OrderID = ?
            """, (order_id,))
            order = cursor.fetchone()

            if order:
                branch_id, product_id, order_quantity = order

                cursor.execute("""
                    UPDATE BranchStock
                    SET StockQuantity = StockQuantity - ?
                    WHERE BranchID = ? AND ProductID = ?
                """, (order_quantity, branch_id, product_id))

            cursor.execute("DELETE FROM BranchOrders WHERE OrderID = ?", (order_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_order_details(order_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.ProductName, co.OrderQuantity, (co.OrderQuantity * p.Price) AS TotalPrice
                FROM CustomerOrders co
                JOIN Products p ON co.ProductID = p.ProductID
                WHERE co.OrderID = ?
            """, (order_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_past_orders(customer_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT o.OrderID, p.ProductName, co.OrderQuantity, 
                       (co.OrderQuantity * p.Price) AS TotalPrice, o.OrderDate
                FROM Orders o
                JOIN CustomerOrders co ON o.OrderID = co.OrderID
                JOIN Products p ON co.ProductID = p.ProductID
                WHERE o.CustomerID = ?
                ORDER BY o.OrderDate DESC
            """, (customer_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_all_categories():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CategoryID, CategoryName FROM Categories")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_basket(customer_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT b.BasketID, p.ProductName, b.Quantity, (b.Quantity * p.Price) AS TotalPrice
                FROM Basket b
                JOIN Products p ON b.ProductID = p.ProductID
                WHERE b.CustomerID = ?
            """, (customer_id,))
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_available_products(branch_id, search=None, category_id=None, min_price=None, max_price=None):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            query = """
                SELECT p.ProductID, p.ProductName, bs.StockQuantity, p.Price, p.CategoryID, p.ProductImage
                FROM Products p
                JOIN BranchStock bs ON p.ProductID = bs.ProductID
                WHERE bs.BranchID = ? AND bs.StockQuantity > 0
            """
            params = [branch_id]

            if search:
                query += " AND p.ProductName LIKE ?"
                params.append(f"%{search}%")
            if category_id:
                query += " AND p.CategoryID = ?"
                params.append(category_id)
            if min_price is not None:
                query += " AND p.Price >= ?"
                params.append(min_price)
            if max_price is not None:
                query += " AND p.Price <= ?"
                params.append(max_price)

            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
        finally:
            conn.close()

    @staticmethod
    def add_to_basket(customer_id, product_id, quantity, branch_id, delivery_option):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT StockQuantity FROM BranchStock
                WHERE ProductID = ? AND BranchID = ?
            """, (product_id, branch_id))
            stock = cursor.fetchone()
            if not stock or stock[0] < quantity:
                raise ValueError("Insufficient stock.")

            cursor.execute("""
                INSERT INTO Basket (CustomerID, ProductID, Quantity, BranchID, DeliveryOption)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(CustomerID, ProductID) DO UPDATE SET Quantity = Quantity + ?
            """, (customer_id, product_id, quantity, branch_id, delivery_option, quantity))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def checkout_basket(customer_id, basket):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            if not basket:
                raise ValueError("Basket is empty.")

            for product_id, item in basket.items():
                quantity = item['quantity']
                print(
                    f"Adding to CustomerOrders: CustomerID={customer_id}, ProductID={product_id}, Quantity={quantity}")

                cursor.execute("""
                    INSERT INTO CustomerOrders (CustomerID, ProductID, OrderDate, OrderQuantity)
                    VALUES (?, ?, DATE('now'), ?)
                """, (customer_id, product_id, quantity))

            conn.commit()

            basket.clear()
            print("Basket cleared after successful checkout.")

        except sqlite3.Error as e:
            print(f"Database error during checkout: {e}")
            raise e
        except ValueError as ve:
            print(f"Validation error: {ve}")
            raise ve
        finally:
            conn.close()

    @staticmethod
    def add_customer_order(customer_id, basket):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Orders (CustomerID, OrderDate)
                VALUES (?, DATE('now'))
            """, (customer_id,))
            order_id = cursor.lastrowid

            for product_id, item in basket.items():
                quantity = item['quantity']
                cursor.execute("""
                    INSERT INTO CustomerOrders (OrderID, ProductID, OrderQuantity)
                    VALUES (?, ?, ?)
                """, (order_id, product_id, quantity))

            conn.commit()
            return order_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_all_branches():
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT BranchID, Location FROM Branches
            """)
            branches = cursor.fetchall()
            return [f"{branch[0]} - {branch[1]}" for branch in branches]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_product_image(product_id, product_image):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Products
                SET ProductImage = ?
                WHERE ProductID = ?
            """, (product_image, product_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def adjust_stock_quantity(branch_id, product_id, quantity_change):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE BranchStock
                SET StockQuantity = StockQuantity + ?
                WHERE BranchID = ? AND ProductID = ?
            """, (quantity_change, branch_id, product_id))
            print(
                f"DEBUG: Adjusted stock for BranchID={branch_id}, ProductID={product_id}, QuantityChange={quantity_change}")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error during stock adjustment: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_branch_stock_id(branch_id, product_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT ROWID FROM BranchStock
                WHERE BranchID = ? AND ProductID = ?
            """, (branch_id, product_id))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_stock_quantity(branch_id, product_id):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT StockQuantity 
                FROM BranchStock 
                WHERE BranchID = ? AND ProductID = ?
            """, (branch_id, product_id))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def fetch_branch_id(branch_location):
        conn = Database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT BranchID FROM Branches WHERE Location = ?", (branch_location,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error while fetching BranchID: {e}")
            raise e
        finally:
            conn.close()

