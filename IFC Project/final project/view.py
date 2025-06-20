import tkinter as tk

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
