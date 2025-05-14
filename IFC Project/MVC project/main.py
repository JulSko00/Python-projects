import tkinter as tk
from model import IfcModel
from view import IfcView
from controller import IfcController

# Main Application
def main():
    root = tk.Tk()
    root.geometry("600x150")
    model = IfcModel()
    controller = IfcController(model, None)  # Temporarily set view as None
    view = IfcView(root, controller)
    controller.view = view  # Set the view in the controller after creation
    root.mainloop()

if __name__ == "__main__":
    main()
#comment