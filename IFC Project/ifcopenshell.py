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
        for space in spaces:
            area = "N/A"
            # Look for area in property sets
            if hasattr(space, "IsDefinedBy"):
                for rel in space.IsDefinedBy:
                    if rel.is_a("IfcRelDefinesByProperties"):
                        property_set = rel.RelatingPropertyDefinition
                        if property_set.is_a("IfcPropertySet"):
                            for prop in property_set.HasProperties:
                                if prop.Name == "NetFloorArea" and hasattr(prop, "NominalValue"):
                                    area = prop.NominalValue.wrappedValue if prop.NominalValue else "N/A"
            space_info = {
                "id": space.id(),
                "global_id": space.GlobalId,
                "name": space.Name if space.Name else "Unnamed",
                "area": area
            }
            print(f"Space Area: {space_info}")
            space_data.append(space_info)
        return space_data

    def get_space_volumes(self):
        """Retrieve spaces from the IFC file and return their volume data."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        spaces = ifc_file.by_type("IfcSpace")
        print(f"Number of spaces: {len(spaces)}")
        space_data = []
        for space in spaces:
            area = "N/A"
            height = "N/A"
            volume = "N/A"
            # Look for area and height in property sets
            if hasattr(space, "IsDefinedBy"):
                for rel in space.IsDefinedBy:
                    if rel.is_a("IfcRelDefinesByProperties"):
                        property_set = rel.RelatingPropertyDefinition
                        if property_set.is_a("IfcPropertySet"):
                            for prop in property_set.HasProperties:
                                if prop.Name == "NetFloorArea" and hasattr(prop, "NominalValue"):
                                    area = prop.NominalValue.wrappedValue if prop.NominalValue else "N/A"
                                if prop.Name == "Height" and hasattr(prop, "NominalValue"):
                                    height = prop.NominalValue.wrappedValue if prop.NominalValue else "N/A"
            # Calculate volume if both area and height are available
            if isinstance(area, (int, float)) and isinstance(height, (int, float)):
                volume = area * height
            space_info = {
                "id": space.id(),
                "global_id": space.GlobalId,
                "name": space.Name if space.Name else "Unnamed",
                "area": area,
                "height": height,
                "volume": volume
            }
            print(f"Space Volume: {space_info}")
            space_data.append(space_info)
        return space_data

# View
class IfcView:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("IFC Wall Reader")
        self.controller = controller
        
        # Frame for the top row (button and text field)
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10, padx=10)
        
        # Open button
        self.open_button = tk.Button(
            self.top_frame,
            text="Open BIM IFC model",
            command=self.controller.on_open_button_click
        )
        self.open_button.pack(side=tk.LEFT)
        
        # File path entry
        self.file_path_entry = tk.Entry(self.top_frame, width=50)
        self.file_path_entry.pack(side=tk.LEFT, padx=5)
        
        # Find Walls button
        self.find_walls_button = tk.Button(
            self.root,
            text="Find Walls",
            command=self.controller.on_find_walls_click,
            state="disabled"
        )
        self.find_walls_button.pack(pady=5)
        
        # Find Doors button
        self.find_doors_button = tk.Button(
            self.root,
            text="Find Doors",
            command=self.controller.on_find_doors_click,
            state="disabled"
        )
        self.find_doors_button.pack(pady=5)
        
        # Find Windows button
        self.find_windows_button = tk.Button(
            self.root,
            text="Find Windows",
            command=self.controller.on_find_windows_click,
            state="disabled"
        )
        self.find_windows_button.pack(pady=5)
        
        # Find Space Areas button
        self.find_space_areas_button = tk.Button(
            self.root,
            text="Find Space Areas",
            command=self.controller.on_find_space_areas_click,
            state="disabled"
        )
        self.find_space_areas_button.pack(pady=5)
        
        # Find Space Volumes button
        self.find_space_volumes_button = tk.Button(
            self.root,
            text="Find Space Volumes",
            command=self.controller.on_find_space_volumes_click,
            state="disabled"
        )
        self.find_space_volumes_button.pack(pady=5)
        
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)
    
    def set_file_path(self, file_path):
        """Update the file path in the text field."""
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
    
    def enable_find_walls_button(self, enable=True):
        """Enable or disable the Find Walls button."""
        state = "normal" if enable else "disabled"
        self.find_walls_button.config(state=state)
    
    def enable_find_doors_button(self, enable=True):
        """Enable or disable the Find Doors button."""
        state = "normal" if enable else "disabled"
        self.find_doors_button.config(state=state)
    
    def enable_find_windows_button(self, enable=True):
        """Enable or disable the Find Windows button."""
        state = "normal" if enable else "disabled"
        self.find_windows_button.config(state=state)
    
    def enable_find_space_areas_button(self, enable=True):
        """Enable or disable the Find Space Areas button."""
        state = "normal" if enable else "disabled"
        self.find_space_areas_button.config(state=state)
    
    def enable_find_space_volumes_button(self, enable=True):
        """Enable or disable the Find Space Volumes button."""
        state = "normal" if enable else "disabled"
        self.find_space_volumes_button.config(state=state)
    
    def display_walls(self, walls, schema):
        """Prepare and display wall data in the console."""
        if walls is None or schema is None:
            print("No file selected or file could not be opened.")
            self.result_label.config(text="No file selected or file could not be opened.")
            return
        
        output = [f"Successfully opened IFC file: {self.file_path_entry.get()}",
                  f"IFC Schema Version: {schema}\n"]
        
        if not walls:
            output.append("No walls found in the IFC file.")
            print("\n".join(output))
            self.result_label.config(text="No walls found in the IFC file.")
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
        self.result_label.config(text=f"Total number of walls: {len(walls)}")
    
    def display_doors(self, doors):
        """Display number of doors in the main window."""
        if doors is None:
            self.result_label.config(text="No file selected or file could not be opened.")
            return
        self.result_label.config(text=f"Total number of doors: {len(doors)}")
    
    def display_windows(self, windows):
        """Display number of windows in the main window."""
        if windows is None:
            self.result_label.config(text="No file selected or file could not be opened.")
            return
        self.result_label.config(text=f"Total number of windows: {len(windows)}")
    
    def display_space_areas(self, spaces):
        """Display number of spaces with areas in the main window and console."""
        if spaces is None:
            self.result_label.config(text="No file selected or file could not be opened.")
            return
        output = [f"Total number of spaces with areas: {len(spaces)}\n"]
        for space in spaces:
            output.append(f"Space ID: {space['id']}")
            output.append(f"Global ID: {space['global_id']}")
            output.append(f"Name: {space['name']}")
            output.append(f"Area: {space['area']} m²")
            output.append("-" * 50)
        output.append(f"\nTotal number of spaces with areas: {len(spaces)}")
        print("\n".join(output))
        self.result_label.config(text=f"Total number of spaces with areas: {len(spaces)}")
    
    def display_space_volumes(self, spaces):
        """Display number of spaces with volumes in the main window and console."""
        if spaces is None:
            self.result_label.config(text="No file selected or file could not be opened.")
            return
        output = [f"Total number of spaces with volumes: {len(spaces)}\n"]
        for space in spaces:
            output.append(f"Space ID: {space['id']}")
            output.append(f"Global ID: {space['global_id']}")
            output.append(f"Name: {space['name']}")
            output.append(f"Area: {space['area']} m²")
            output.append(f"Height: {space['height']} m")
            output.append(f"Volume: {space['volume']} m³")
            output.append("-" * 50)
        output.append(f"\nTotal number of spaces with volumes: {len(spaces)}")
        print("\n".join(output))
        self.result_label.config(text=f"Total number of spaces with volumes: {len(spaces)}")

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