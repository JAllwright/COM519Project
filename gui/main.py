import tkinter as tk
from gui.customer_portal import CustomerPortal
from gui.navigation_manager import NavigationManager
from gui.staff_portal import StaffPortal
from custom_xml_utils.xml_utils import XMLUtils


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Application")
        self.root.geometry("400x300")
        self.navigation_manager = NavigationManager()
        self.create_widgets()

    def create_widgets(self):
        """Create widgets for the main application."""
        tk.Label(self.root, text="Main Application", font=("Arial", 16)).pack(pady=20)

        tk.Button(self.root, text="Customer Portal", command=self.open_customer_portal, width=20).pack(pady=10)
        tk.Button(self.root, text="Admin Portal", command=self.open_admin_portal, width=20).pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit, width=20).pack(pady=10)

    def open_customer_portal(self):
        """Open the Customer Portal."""
        self.navigation_manager.navigate(
            self.root, lambda: CustomerPortal(self.root, self.navigation_manager)
        )

    def open_admin_portal(self):
        """Open the Admin/Staff Portal."""
        self.navigation_manager.navigate(
            self.root, lambda: StaffPortal(self.root, self.navigation_manager)
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
