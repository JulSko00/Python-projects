import tkinter as tk
from model import IfcModel
from view import IfcView
from controller import IfcController

# Main Application
def main():
    root = tk.Tk()
    root.geometry("600x400")
    model = IfcModel()
    controller = IfcController(model, None)
    view = IfcView(root, controller)
    controller.view = view
    root.mainloop()

if __name__ == "__main__":
    main()