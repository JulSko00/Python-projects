import ifcopenshell

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
