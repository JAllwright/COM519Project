class NavigationManager:
    def __init__(self):
        self.stack = []  # A stack to keep track of navigation

    def navigate(self, from_window, to_window_class, *args, **kwargs):
        """Navigate to a new window."""
        self.stack.append(from_window)
        from_window.withdraw()  # Hide the current window
        new_window = to_window_class(*args, **kwargs)  # Pass arguments to the new window class
        return new_window

    def back(self, current_window):
        """Navigate back to the previous window."""
        if self.stack:
            previous_window = self.stack.pop()
            current_window.destroy()  # Close the current window
            previous_window.deiconify()  # Show the previous window
