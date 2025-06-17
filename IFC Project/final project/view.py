import tkinter as tk

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

        # Solar Gain Calculation Button
        self.calc_solar_gain_button = tk.Button(
            self.root,
            text="Calculate daily solar heat gain",
            command=self.controller.on_calc_solar_gain_click,
            state="disabled"
        )
        self.calc_solar_gain_button.pack(pady=5)
        
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

    def enable_calc_solar_gain_button(self, enable=True):
        """Enable or disable the Solar Gain Calculation button."""
        state = "normal" if enable else "disabled"
        self.calc_solar_gain_button.config(state=state)
    
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

    def display_space_areas(self, data):
        """Display number of spaces with areas in the main window and console."""
        if data is None or "spaces" not in data:
            self.result_label.config(text="No file selected or file could not be opened.")
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
        self.result_label.config(text=f"Total area of spaces: {total_area:.2f} m²")
    
    def display_space_volumes(self, data):
        """Display number of spaces with volumes in the main window and console."""
        if data is None or "spaces" not in data:
            self.result_label.config(text="No file selected or file could not be opened.")
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
        self.result_label.config(text=f"Total volume of spaces: {total_volume:.2f} m³")
