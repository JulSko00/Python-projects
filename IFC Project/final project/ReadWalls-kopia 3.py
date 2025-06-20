import ifcopenshell
import tkinter as tk
from tkinter import filedialog

# Model
class IfcModel:
    def __init__(self):
        self.file_path = None
        self.ifc_file = None

    def set_file_path(self, file_path):
        """Set the IFC file path."""
        self.file_path = file_path
        self.ifc_file = None  # Reset ifc_file when path changes

    def open_ifc_file(self):
        """Open the IFC file and return it, or None if it fails."""
        if not self.file_path:
            print("No path to the IFC file")
            return None
        print(f"Attempting to open the file: {self.file_path}")
        try:
            self.ifc_file = ifcopenshell.open(self.file_path)
            print("IFC file opened successfully")
            return self.ifc_file
        except FileNotFoundError:
            print("IFC file not found")
            return None
        except Exception as e:
            print(f"An error occurred while opening the file: {str(e)}")
            return None

    def get_walls(self):
        """Retrieve walls from the IFC file and return them."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        walls = ifc_file.by_type("IfcWall")
        print(f"Number of walls: {len(walls)}")
        return walls

    def get_schema(self):
        """Retrieve the schema version from the IFC file."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        return ifc_file.schema

    def get_doors(self):
        """Retrieve doors from the IFC file and return them."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        doors = ifc_file.by_type("IfcDoor")
        print(f"Number of doors: {len(doors)}")
        door_data = []
        for door in doors:
            door_info = {
                "id": door.id(),
                "global_id": door.GlobalId,
                "name": door.Name if door.Name else "Unnamed",
                "width": door.OverallWidth if hasattr(door, "OverallWidth") else "N/A",
                "height": door.OverallHeight if hasattr(door, "OverallHeight") else "N/A"
            }
            print(f"Doors: {door_info}")
            door_data.append(door_info)
        return door_data

    def get_windows(self):
        """Retrieve windows from the IFC file and return them."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        windows = ifc_file.by_type("IfcWindow")
        print(f"Number of windows: {len(windows)}")
        window_data = []
        for window in windows:
            window_info = {
                "id": window.id(),
                "global_id": window.GlobalId,
                "name": window.Name if window.Name else "Unnamed",
                "width": window.OverallWidth if hasattr(window, "OverallWidth") else "N/A",
                "height": window.OverallHeight if hasattr(window, "OverallHeight") else "N/A"
            }
            print(f"Window: {window_info}")
            window_data.append(window_info)
        return window_data
    
    def get_space_areas(self):
        """Retrieve spaces from the IFC file and return their area data."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        spaces = ifc_file.by_type("IfcSpace")
        print(f"Number of spaces: {len(spaces)}")
        space_data = []
        total_area = 0.0
        for space in spaces:
            area = "N/A"
            for rel in space.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    prop_def = rel.RelatingPropertyDefinition
                    if prop_def.is_a("IfcElementQuantity"):
                        for quantity in prop_def.Quantities:
                            if quantity.is_a("IfcQuantityArea") and quantity.Name == "NetFloorArea":
                                area = quantity.AreaValue
                                print(f"Found area for space {space.id()}: {area}")
                                if isinstance(area, (int, float)):
                                    total_area += area
            space_info = {
                "id": space.id(),
                "global_id": space.GlobalId,
                "name": space.Name if space.Name else "Unnamed",
                "area": area
            }
            print(f"Space Area: {space_info}")
            space_data.append(space_info)
        return {"spaces": space_data, "total_area": total_area}

    def get_space_volumes(self):
        """Retrieve spaces from the IFC file and return their volume data."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        spaces = ifc_file.by_type("IfcSpace")
        print(f"Number of spaces: {len(spaces)}")
        space_data = []
        total_volume = 0.0
        for space in spaces:
            volume = "N/A"
            for rel in space.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    prop_def = rel.RelatingPropertyDefinition
                    if prop_def.is_a("IfcElementQuantity"):
                        for quantity in prop_def.Quantities:
                            if quantity.is_a("IfcQuantityVolume") and quantity.Name == "NetVolume":
                                volume = quantity.VolumeValue
                                print(f"Found volume for space {space.id()}: {volume}")
                                if isinstance(volume, (int, float)):
                                    total_volume += volume
            space_info = {
                "id": space.id(),
                "global_id": space.GlobalId,
                "name": space.Name if space.Name else "Unnamed",
                "volume": volume
            }
            print(f"Space Volume: {space_info}")
            space_data.append(space_info)
        return {"spaces": space_data, "total_volume": total_volume}

    def calculate_total_window_area(self):
        """Calculate total window glass area based on 'Steklena površina'."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return 0.0
        total_area = 0.0
        for window in ifc_file.by_type("IfcWindow"):
            for rel in window.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    prop_def = rel.RelatingPropertyDefinition
                    if prop_def.is_a("IfcPropertySet"):
                        for prop in prop_def.HasProperties:
                            if prop.Name == "Steklena površina" and hasattr(prop, "NominalValue"):
                                value = prop.NominalValue.wrappedValue
                                if isinstance(value, (int, float)):
                                    total_area += value
        return total_area

# View
class IfcView:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("IFC Wall Reader")
        self.controller = controller
        
        # Main container frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Top frame for file selection
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X)
        
        # Open button
        self.open_button = tk.Button(
            self.top_frame,
            text="Open BIM IFC model",
            command=self.controller.on_open_button_click,
            width=20
        )
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        # File path entry
        self.file_path_entry = tk.Entry(self.top_frame, width=50)
        self.file_path_entry.pack(side=tk.LEFT, padx=5)
        
        # Frame for buttons and results
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.BOTH, pady=10)
        
        # Dictionary to store result labels for each button
        self.result_labels = {}
        
        # List of buttons and their commands
        button_configs = [
            ("Find Walls", self.controller.on_find_walls_click),
            ("Find Doors", self.controller.on_find_doors_click),
            ("Find Windows", self.controller.on_find_windows_click),
            ("Find Space Areas", self.controller.on_find_space_areas_click),
            ("Find Space Volumes", self.controller.on_find_space_volumes_click),
            ("Calculate Solar Gain", self.controller.on_calc_solar_gain_click)
        ]
        
        # Create button and result label pairs
        for button_text, command in button_configs:
            # Frame for each button-label pair
            frame = tk.Frame(self.buttons_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # Button
            button = tk.Button(
                frame,
                text=button_text,
                command=command,
                state="disabled",
                width=20,
                anchor="center"  # Center the button text
            )
            button.pack(side=tk.LEFT, padx=5)
            
            # Result label
            result_label = tk.Label(
                frame,
                text="",
                font=("Arial", 12),
                anchor="w",
                width=40
            )
            result_label.pack(side=tk.LEFT, padx=5)
            
            # Store button and label for enabling/disabling and updating
            self.result_labels[button_text] = {
                "button": button,
                "label": result_label
            }
    
    def set_file_path(self, file_path):
        """Update the file path in the text field."""
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
    
    def enable_find_walls_button(self, enable=True):
        """Enable or disable the Find Walls button."""
        state = "normal" if enable else "disabled"
        self.result_labels["Find Walls"]["button"].config(state=state)
    
    def enable_find_doors_button(self, enable=True):
        """Enable or disable the Find Doors button."""
        state = "normal" if enable else "disabled"
        self.result_labels["Find Doors"]["button"].config(state=state)
    
    def enable_find_windows_button(self, enable=True):
        """Enable or disable the Find Windows button."""
        state = "normal" if enable else "disabled"
        self.result_labels["Find Windows"]["button"].config(state=state)
    
    def enable_find_space_areas_button(self, enable=True):
        """Enable or disable the Find Space Areas button."""
        state = "normal" if enable else "disabled"
        self.result_labels["Find Space Areas"]["button"].config(state=state)
    
    def enable_find_space_volumes_button(self, enable=True):
        """Enable or disable the Find Space Volumes button."""
        state = "normal" if enable else "disabled"
        self.result_labels["Find Space Volumes"]["button"].config(state=state)

    def enable_calc_solar_gain_button(self, enable=True):
        """Enable or disable the Calculate Solar Gain button."""
        state = "normal" if enable else "disabled"
        self.result_labels["Calculate Solar Gain"]["button"].config(state=state)
    
    def display_walls(self, walls, schema):
        """Prepare and display wall data in the console and update the result label."""
        label = self.result_labels["Find Walls"]["label"]
        if walls is None or schema is None:
            print("No file selected or file could not be opened.")
            label.config(text="No file selected or file could not be opened.")
            return
        
        output = [f"Successfully opened IFC file: {self.file_path_entry.get()}",
                  f"IFC Schema Version: {schema}\n"]
        
        if not walls:
            output.append("No walls found in the IFC file.")
            print("\n".join(output))
            label.config(text="No walls found in the IFC file.")
            return
        
        wall_count = len(walls)
        output.append(f"Total number of walls found: {wall_count}\n")
        
        for wall in walls:
            output.append(f"Wall ID: {wall.id()}")
            output.append(f"Global ID: {wall.GlobalId}")
            output.append(f"Name: {wall.Name if wall.Name else 'Unnamed'}")
            output.append(f"Type: {wall.is_a()}")
            
            if hasattr(wall, "Description") and wall.Description:
                output.append(f"Description: {wall.Description}")
            
            if wall.ObjectPlacement:
                placement = wall.ObjectPlacement.RelativePlacement
                if placement and hasattr(placement, "Location"):
                    coords = placement.Location.Coordinates
                    output.append(f"Location: X={coords[0]}, Y={coords[1]}, Z={coords[2]}")
            
            output.append("-" * 50)
        
        output.append(f"\nTotal number of walls: {wall_count}")
        print("\n".join(output))
        label.config(text=f"Total number of walls: {len(walls)}")
    
    def display_doors(self, doors):
        """Display number of doors in the corresponding result label."""
        label = self.result_labels["Find Doors"]["label"]
        if doors is None:
            label.config(text="No file selected or file could not be opened.")
            return
        label.config(text=f"Total number of doors: {len(doors)}")
    
    def display_windows(self, windows):
        """Display number of windows in the corresponding result label."""
        label = self.result_labels["Find Windows"]["label"]
        if windows is None:
            label.config(text="No file selected or file could not be opened.")
            return
        label.config(text=f"Total number of windows: {len(windows)}")

    def display_space_areas(self, data):
        """Display number of spaces with areas in the corresponding result label and console."""
        label = self.result_labels["Find Space Areas"]["label"]
        if data is None or "spaces" not in data:
            label.config(text="No file selected or file could not be opened.")
            return
        spaces = data["spaces"]
        total_area = data["total_area"]
        output = [f"Total number of spaces with areas: {len(spaces)}\n"]
        for space in spaces:
            output.append(f"Space ID: {space['id']}")
            output.append(f"Global ID: {space['global_id']}")
            output.append(f"Name: {space['name']}")
            output.append(f"Area: {space['area']} m²")
            output.append("-" * 50)
        output.append(f"\nTotal number of spaces with areas: {len(spaces)}")
        output.append(f"Total area of spaces: {total_area:.2f} m²")
        print("\n".join(output))
        label.config(text=f"Total area of spaces: {total_area:.2f} m²")
    
    def display_space_volumes(self, data):
        """Display number of spaces with volumes in the corresponding result label and console."""
        label = self.result_labels["Find Space Volumes"]["label"]
        if data is None or "spaces" not in data:
            label.config(text="No file selected or file could not be opened.")
            return
        spaces = data["spaces"]
        total_volume = data["total_volume"]
        output = [f"Total number of spaces with volumes: {len(spaces)}\n"]
        for space in spaces:
            output.append(f"Space ID: {space['id']}")
            output.append(f"Global ID: {space['global_id']}")
            output.append(f"Name: {space['name']}")
            output.append(f"Volume: {space['volume']} m³")
            output.append("-" * 50)
        output.append(f"\nTotal number of spaces with volumes: {len(spaces)}")
        output.append(f"Total volume of spaces: {total_volume:.2f} m³")
        print("\n".join(output))
        label.config(text=f"Total volume of spaces: {total_volume:.2f} m³")

    def display_solar_gain(self, solar_gain):
        """Display solar gain in the corresponding result label."""
        label = self.result_labels["Calculate Solar Gain"]["label"]
        label.config(text=f"Daily solar heat gain: {solar_gain:.2f} Wh")

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
                self.view.display_solar_gain(0)  # Display error via label
                self.view.result_labels["Calculate Solar Gain"]["label"].config(text="Solar gain coefficient must be between 0 and 1.")
                return
            ext_temp = float(simpledialog.askstring("Input", "Enter external temperature (°C):"))
            int_temp = float(simpledialog.askstring("Input", "Enter internal temperature (°C):"))
            sun_hours = float(simpledialog.askstring("Input", "Enter daily sun exposure (hours):"))
        except Exception:
            self.view.display_solar_gain(0)  # Display error via label
            self.view.result_labels["Calculate Solar Gain"]["label"].config(text="Invalid input.")
            return

        total_window_area = self.model.calculate_total_window_area()
        solar_gain = total_window_area * g_factor * (int_temp - ext_temp) * sun_hours
        self.view.display_solar_gain(solar_gain)
        
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