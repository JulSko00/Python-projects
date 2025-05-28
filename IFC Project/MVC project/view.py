import tkinter as tk

# View
class IfcView:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Hello in IFC Wall Reader!")
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

    def display_walls(self, walls, schema):
        """Prepare and display wall data in the console."""
        if walls is None or schema is None:
            print("No file selected or file could not be opened.")
            return
        
        # Prepare the output list
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

        # Add the final wall count
        output.append(f"\nTotal number of walls: {wall_count}")
    
        # Print the entire output
        print("\n".join(output))
        self.result_label.config(text=f"Total number of walls: {len(walls) if walls else 0}")