from tkinter import filedialog

# Controller
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
            self.view.enable_area_report_button(True)
            self.view.enable_volumes_button(True)
        else:
            self.view.enable_find_walls_button(False)
            self.view.enable_find_doors_button(False)
            self.view.enable_find_windows_button(False)
            self.view.enable_area_report_button(False)
            self.view.enable_volumes_button(False)
    
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
    
    def on_generate_area_report_click(self):
        """Handle the Calculate Net Floor Area button click."""
        spaces = self.model.get_spaces()
        self.view.display_area_report(spaces)
    
    def on_calculate_volumes_click(self):
        """Handle the Calculate Volume button click."""
        volumes = self.model.get_space_volumes()
        self.view.display_volumes(volumes)