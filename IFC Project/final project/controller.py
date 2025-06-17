import tkinter.simpledialog as simpledialog
from tkinter import filedialog

class IfcController:

    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def on_open_button_click(self):
        """Handle the Open BIM IFC model button click."""
        file_path = filedialog.askopenfilename(
            title="Select an IFC File",
            filetypes=[("IFC Files", "*.ifc"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.model.set_file_path(file_path)
            self.view.set_file_path(file_path)
            self.view.enable_find_walls_button(True)
            self.view.enable_find_doors_button(True)
            self.view.enable_find_windows_button(True)
            self.view.enable_find_space_areas_button(True)
            self.view.enable_find_space_volumes_button(True)
            self.view.enable_calc_solar_gain_button(True)
        else:
            self.view.enable_find_walls_button(False)
            self.view.enable_find_doors_button(False)
            self.view.enable_find_windows_button(False)
            self.view.enable_find_space_areas_button(False)
            self.view.enable_find_space_volumes_button(False)
    
    def on_find_walls_click(self):
        """Handle the Find Walls button click."""
        walls = self.model.get_walls()
        schema = self.model.get_schema()
        self.view.display_walls(walls, schema)
    
    def on_find_doors_click(self):
        """Handle the Find Doors button click."""
        doors = self.model.get_doors()
        self.view.display_doors(doors)
    
    def on_find_windows_click(self):
        """Handle the Find Windows button click."""
        windows = self.model.get_windows()
        self.view.display_windows(windows)
    
    def on_find_space_areas_click(self):
        """Handle the Find Space Areas button click."""
        spaces = self.model.get_space_areas()
        self.view.display_space_areas(spaces)
    
    def on_find_space_volumes_click(self):
        """Handle the Find Space Volumes button click."""
        spaces = self.model.get_space_volumes()
        self.view.display_space_volumes(spaces)

    def on_calc_solar_gain_click(self):
        """Calculate solar heat gain based on window areas and user input."""
        import tkinter.simpledialog as simpledialog
        try:
            g_factor = float(simpledialog.askstring("Input", "Enter solar heat gain coefficient (0 to 1):"))
            if not (0 <= g_factor <= 1):
                self.view.result_label.config(text="Solar gain coefficient must be between 0 and 1.")
                return
            ext_temp = float(simpledialog.askstring("Input", "Enter external temperature (°C):"))
            int_temp = float(simpledialog.askstring("Input", "Enter internal temperature (°C):"))
            sun_hours = float(simpledialog.askstring("Input", "Enter daily sun exposure (hours):"))
        except Exception:
            self.view.result_label.config(text="Invalid input.")
            return

        total_window_area = self.model.calculate_total_window_area()
        solar_gain = total_window_area * g_factor * (int_temp - ext_temp) * sun_hours
        self.view.result_label.config(text=f"Daily solar heat gain: {solar_gain:.2f} Wh")
