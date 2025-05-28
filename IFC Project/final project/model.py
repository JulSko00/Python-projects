import ifcopenshell

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
            print("Brak ścieżki do pliku IFC")
            return None
        print(f"Próba otwarcia pliku: {self.file_path}")
        try:
            self.ifc_file = ifcopenshell.open(self.file_path)
            print("Plik IFC otwarty pomyślnie")
            return self.ifc_file
        except FileNotFoundError:
            print("Plik IFC nie znaleziony")
            return None
        except Exception as e:
            print(f"Wystąpił błąd podczas otwierania pliku: {str(e)}")
            return None

    def get_walls(self):
        """Retrieve walls from the IFC file and return them."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        walls = ifc_file.by_type("IfcWall")
        print(f"Liczba ścian: {len(walls)}")
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
        print(f"Liczba drzwi: {len(doors)}")
        door_data = []
        for door in doors:
            door_info = {
                "id": door.id(),
                "global_id": door.GlobalId,
                "name": door.Name if door.Name else "Unnamed",
                "width": door.OverallWidth if hasattr(door, "OverallWidth") else "N/A",
                "height": door.OverallHeight if hasattr(door, "OverallHeight") else "N/A"
            }
            print(f"Drzwi: {door_info}")
            door_data.append(door_info)
        return door_data

    def get_windows(self):
        """Retrieve windows from the IFC file and return them."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            return None
        windows = ifc_file.by_type("IfcWindow")
        print(f"Liczba okien: {len(windows)}")
        window_data = []
        for window in windows:
            window_info = {
                "id": window.id(),
                "global_id": window.GlobalId,
                "name": window.Name if window.Name else "Unnamed",
                "width": window.OverallWidth if hasattr(window, "OverallWidth") else "N/A",
                "height": window.OverallHeight if hasattr(window, "OverallHeight") else "N/A"
            }
            print(f"Okno: {window_info}")
            window_data.append(window_info)
        return window_data

    def get_spaces(self):
        """Retrieve spaces and calculate net floor area (floor area minus wall footprint)."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            print("Nie można otworzyć pliku IFC.")
            return None
        spaces = ifc_file.by_type("IfcSpace")
        print(f"Liczba pomieszczeń: {len(spaces)}")
        space_data = []

        for space in spaces:
            # Get floor area from properties
            floor_area = None
            for rel in getattr(space, "IsDefinedBy", []):
                if rel.is_a("IfcRelDefinesByProperties"):
                    property_set = rel.RelatingPropertyDefinition
                    if hasattr(property_set, "HasProperties"):
                        for prop in property_set.HasProperties:
                            if prop.Name in ["NetFloorArea", "GrossFloorArea", "Area"]:
                                if hasattr(prop, "NominalValue") and prop.NominalValue:
                                    floor_area = prop.NominalValue.wrappedValue
                                    print(f"Pomieszczenie {space.id()}: Znaleziono powierzchnię {prop.Name} = {floor_area}")
                                    break
                        if floor_area is not None:
                            break

            # Backup: estimate floor area from geometry
            if floor_area is None and space.Representation:
                for rep in space.Representation.Representations:
                    if rep.RepresentationType in ["SweptSolid", "Polygon"]:
                        for item in rep.Items:
                            if item.is_a("IfcExtrudedAreaSolid"):
                                profile = item.SweptArea
                                if profile.is_a("IfcRectangleProfileDef"):
                                    floor_area = profile.XDim * profile.YDim
                                    print(f"Pomieszczenie {space.id()}: Powierzchnia z geometrii = {floor_area}")
                                    break
                        if floor_area is not None:
                            break

            # Get walls intersecting the space via IfcRelSpaceBoundary
            wall_area = 0.0
            for rel in getattr(space, "BoundedBy", []):
                if rel.is_a("IfcRelSpaceBoundary") and rel.RelatedBuildingElement and rel.RelatedBuildingElement.is_a("IfcWall"):
                    wall = rel.RelatedBuildingElement
                    if wall.Representation:
                        for rep in wall.Representation.Representations:
                            if rep.RepresentationType == "SweptSolid":
                                for item in rep.Items:
                                    if item.is_a("IfcExtrudedAreaSolid"):
                                        profile = item.SweptArea
                                        if profile.is_a("IfcRectangleProfileDef"):
                                            length = profile.XDim
                                            thickness = profile.YDim
                                            wall_area += length * thickness
                                            print(f"Ściana w pomieszczeniu {space.id()}: długość={length}, grubość={thickness}, pole={length*thickness}")

            # Convert units if necessary (assuming IFC file uses meters; adjust if needed)
            if floor_area is not None:
                # Example: convert mm² to m² if file uses millimeters
                if floor_area > 1000:  # Heuristic to detect if area is in mm²
                    floor_area /= 1_000_000
                    print(f"Pomieszczenie {space.id()}: Powierzchnia skonwertowana na m²: {floor_area}")
                if wall_area > 1000:  # Heuristic to detect if wall area is in mm²
                    wall_area /= 1_000_000
                    print(f"Pomieszczenie {space.id()}: Powierzchnia ścian skonwertowana na m²: {wall_area}")

            # Calculate net floor area
            net_area = floor_area - wall_area if floor_area is not None and wall_area is not None else None
            if isinstance(net_area, float) and net_area < 0:
                net_area = 0.0  # Prevent negative area
                print(f"Pomieszczenie {space.id()}: Powierzchnia netto ustawiona na 0 (była ujemna)")

            space_data.append({
                "id": space.id(),
                "name": space.Name if space.Name else "Unnamed",
                "net_area": net_area if net_area is not None else "N/A"
            })
            print(f"Pomieszczenie {space.id()}: Powierzchnia netto = {net_area}")

        return space_data

    def get_space_volumes(self):
        """Calculate volume as net floor area times ceiling height."""
        ifc_file = self.open_ifc_file()
        if ifc_file is None:
            print("Nie można otworzyć pliku IFC.")
            return None
        spaces = ifc_file.by_type("IfcSpace")
        print(f"Liczba pomieszczeń (dla objętości): {len(spaces)}")
        volume_data = []

        for space in spaces:
            # Get net floor area
            net_area = None
            for rel in getattr(space, "IsDefinedBy", []):
                if rel.is_a("IfcRelDefinesByProperties"):
                    property_set = rel.RelatingPropertyDefinition
                    if hasattr(property_set, "HasProperties"):
                        for prop in property_set.HasProperties:
                            if prop.Name in ["NetFloorArea", "GrossFloorArea", "Area"]:
                                if hasattr(prop, "NominalValue") and prop.NominalValue:
                                    net_area = prop.NominalValue.wrappedValue
                                    print(f"Pomieszczenie {space.id()}: Powierzchnia netto = {net_area}")
                                    break
                        if net_area is not None:
                            break

            wall_area = 0.0
            for rel in getattr(space, "BoundedBy", []):
                if rel.is_a("IfcRelSpaceBoundary") and rel.RelatedBuildingElement and rel.RelatedBuildingElement.is_a("IfcWall"):
                    wall = rel.RelatedBuildingElement
                    if wall.Representation:
                        for rep in wall.Representation.Representations:
                            if rep.RepresentationType == "SweptSolid":
                                for item in rep.Items:
                                    if item.is_a("IfcExtrudedAreaSolid"):
                                        profile = item.SweptArea
                                        if profile.is_a("IfcRectangleProfileDef"):
                                            length = profile.XDim
                                            thickness = profile.YDim
                                            wall_area += length * thickness
                                            print(f"Ściana w pomieszczeniu {space.id()}: długość={length}, grubość={thickness}, pole={length*thickness}")

            if net_area is not None:
                if net_area > 1000:  # Convert mm² to m² if necessary
                    net_area /= 1_000_000
                    print(f"Pomieszczenie {space.id()}: Powierzchnia netto skonwertowana na m²: {net_area}")
                if wall_area > 1000:  # Convert mm² to m² if necessary
                    wall_area /= 1_000_000
                    print(f"Pomieszczenie {space.id()}: Powierzchnia ścian skonwertowana na m²: {wall_area}")
                net_area = net_area - wall_area if wall_area is not None else net_area
                if net_area < 0:
                    net_area = 0.0
                    print(f"Pomieszczenie {space.id()}: Powierzchnia netto ustawiona na 0 (była ujemna)")

            # Get ceiling height
            height = None
            for rel in getattr(space, "IsDefinedBy", []):
                if rel.is_a("IfcRelDefinesByProperties"):
                    property_set = rel.RelatingPropertyDefinition
                    if hasattr(property_set, "HasProperties"):
                        for prop in property_set.HasProperties:
                            if prop.Name in ["NetCeilingHeight", "Height", "GrossCeilingHeight"]:
                                if hasattr(prop, "NominalValue") and prop.NominalValue:
                                    height = prop.NominalValue.wrappedValue
                                    print(f"Pomieszczenie {space.id()}: Wysokość = {height}")
                                    break
                        if height is not None:
                            break

            # Backup: estimate height from geometry
            if height is None and space.Representation:
                for rep in space.Representation.Representations:
                    if rep.RepresentationType in ["SweptSolid", "Polygon"]:
                        for item in rep.Items:
                            if item.is_a("IfcExtrudedAreaSolid"):
                                height = item.Depth
                                print(f"Pomieszczenie {space.id()}: Wysokość z geometrii = {height}")
                                break
                        if height is not None:
                            break

            # Convert height if necessary (e.g., mm to m)
            if height is not None and height > 100:  # Heuristic to detect if height is in mm
                height /= 1000
                print(f"Pomieszczenie {space.id()}: Wysokość skonwertowana na m: {height}")

            # Calculate volume
            volume = net_area * height if net_area is not None and height is not None else "N/A"
            print(f"Pomieszczenie {space.id()}: net_area={net_area}, height={height}, volume={volume}")

            volume_data.append({
                "id": space.id(),
                "name": space.Name if space.Name else "Unnamed",
                "volume": volume
            })

        return volume_data