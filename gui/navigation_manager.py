class NavigationManager:
    def __init__(self):
        self.stack = []

    def navigate(self, from_window, to_window_class, *args, **kwargs):
        self.stack.append(from_window)
        from_window.withdraw()
        new_window = to_window_class(*args, **kwargs)
        return new_window

    def back(self, current_window):
        if self.stack:
            previous_window = self.stack.pop()
            current_window.destroy()
            previous_window.deiconify()
