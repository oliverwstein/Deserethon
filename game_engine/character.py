import yaml # We'll need this for the loading method

class Character:
    def __init__(self,
                 char_id: str,
                 name: str,
                 age: int,
                 gender: str,
                 bio: str,
                 is_player: bool = False,
                 relationships_data: dict = None, # Raw relationship IDs from YAML
                 assets: list = None, # Added
                 skills: list = None, # Added
                 traits: list = None, # As per your request
                 # --- Dynamic attributes, initialized later ---
                 # These will be populated after all characters are loaded
                 # by the GameState.link_relationships() method.
                 # We initialize them to None or empty collections.
                 spouse_obj: 'Character' = None, # Forward reference using quotes
                 parent_objs: list['Character'] = None,
                 children_objs: list['Character'] = None,
                 sibling_objs: list['Character'] = None
                 ):
        
        self.id: str = char_id
        self.name: str = name
        self.is_player: bool = is_player
        self.age: int = age
        self.gender: str = gender # "M", "F", or perhaps more inclusive options later
        self.bio: str = bio

        # This dictionary stores the *IDs* of related characters as read from YAML.
        # e.g., {"spouse_id": "MARTHA001", "children_ids": ["JULIA001", ...]}
        self.relationships_data: dict = relationships_data if relationships_data is not None else {}

        self.assets: list[str] = assets if assets is not None else []
        self.skills: list[str] = skills if skills is not None else []
        
        # Traits: could be simple strings or more complex objects later
        self.traits: list[str] = traits if traits is not None else []

        # --- Dynamically linked object references ---
        # These will be populated by GameState.link_relationships()
        self.spouse_obj: Character | None = spouse_obj # Direct reference to spouse Character object
        self.parent_objs: list[Character] = parent_objs if parent_objs is not None else []
        self.children_objs: list[Character] = children_objs if children_objs is not None else []
        self.sibling_objs: list[Character] = sibling_objs if sibling_objs is not None else []

    @classmethod
    def load_from_yaml_file(cls, file_path: str) -> 'Character':
        """
        Loads character data from a single YAML file and creates a Character instance.
        Assumes the YAML file contains a single character definition (a dictionary).
        """
        try:
            with open(file_path, 'r') as f:
                char_data = yaml.safe_load(f)
                if not isinstance(char_data, dict):
                    raise ValueError(f"YAML file {file_path} does not contain a valid character dictionary.")
        except FileNotFoundError:
            # Handle error: log it, raise it, or return None
            print(f"ERROR: Character file not found: {file_path}")
            raise # Or return None, depending on desired error handling
        except yaml.YAMLError as e:
            print(f"ERROR: Could not parse YAML file {file_path}: {e}")
            raise # Or return None
        except ValueError as e:
            print(f"ERROR: Invalid data in {file_path}: {e}")
            raise # Or return None

        # Basic validation for required fields (can be expanded)
        required_fields = ['id', 'name', 'age', 'gender', 'bio']
        for field in required_fields:
            if field not in char_data:
                raise ValueError(f"Missing required field '{field}' in character data from {file_path}")
        
        # Map YAML keys to __init__ parameters
        # Handle optional fields gracefully with .get() and defaults
        return cls(
            char_id=char_data['id'],
            name=char_data['name'],
            age=char_data['age'],
            gender=char_data['gender'],
            bio=char_data['bio'],
            is_player=char_data.get('is_player', False),
            relationships_data=char_data.get('relationships'), # 'relationships' in YAML
            assets=char_data.get('assets'),
            skills=char_data.get('skills'),
            traits=char_data.get('traits')
        )

    def __repr__(self) -> str:
        return f"<Character(id='{self.id}', name='{self.name}', age={self.age})>"

    def get_short_description(self) -> str:
        """Returns a short, one-line description."""
        return f"{self.name} ({self.age}{self.gender})"

    def get_full_bio_display(self) -> str:
        """Returns a formatted string for full bio display."""
        lines = [
            f"Name: {self.name}",
            f"ID: {self.id}",
            f"Age: {self.age}",
            f"Gender: {self.gender}",
            "Bio:",
            f"  {self.bio.replace  # Indent bio lines
                ('\n', '\n  ') if self.bio else 'N/A'}",
        ]
        if self.traits:
            lines.append(f"Traits: {', '.join(self.traits)}")
        if self.skills:
            lines.append(f"Notable Skills: {', '.join(self.skills)}")
        if self.assets:
            lines.append(f"Assets: {', '.join(self.assets)}")
        return "\n".join(lines)

    def get_family_info_display(self) -> str:
        """Returns formatted string for family relationships (uses linked objects)."""
        lines = ["Family Information:"]
        if self.spouse_obj:
            lines.append(f"  Spouse: {self.spouse_obj.name} (ID: {self.spouse_obj.id})")
        else:
            lines.append(f"  Spouse: None") # Or based on marital_status

        if self.parent_objs:
            parent_names = [p.name for p in self.parent_objs]
            lines.append(f"  Parents: {', '.join(parent_names)}")
        else:
            lines.append("  Parents: Unknown")

        if self.children_objs:
            child_names = [c.name for c in self.children_objs]
            lines.append(f"  Children: {', '.join(child_names)}")
        else:
            lines.append("  Children: None")

        if self.sibling_objs:
            sibling_names = [s.name for s in self.sibling_objs]
            lines.append(f"  Siblings: {', '.join(sibling_names)}")
        
        return "\n".join(lines)

    # Helper methods to access relationship IDs if needed before objects are linked
    def get_spouse_id(self) -> str | None:
        return self.relationships_data.get("spouse_id")

    def get_parent_ids(self) -> list[str]:
        return self.relationships_data.get("parent_ids", [])

    def get_children_ids(self) -> list[str]:
        return self.relationships_data.get("children_ids", [])

    def get_sibling_ids(self) -> list[str]:
        return self.relationships_data.get("sibling_ids", [])