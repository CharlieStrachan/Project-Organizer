import json

from models import Project, Task

def load_projects(filename="projects.json") -> list[Project]:
    """
    Load projects from a JSON file.
    Args:
        filename (str): The name of the JSON file to load projects from. Defaults to "projects.json".
    Returns:
        list[Project]: A list of Project objects loaded from the file. If the file does not exist or is empty, returns an empty list.
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            projects = []
            for proj in data:
                tasks = [Task(**t) for t in proj.get("tasks", [])]
                projects.append(Project(
                    name=proj["name"],
                    description=proj.get("description", "No description provided."),
                    tasks=tasks
                ))
            return projects
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON. Starting with an empty project list.")
        return []

def save_projects(projects, filename="projects.json") -> bool:
    """
    Save projects to a JSON file.
    Args:
        projects (list[Project]): A list of Project objects to save.
        filename (str): The name of the JSON file to save projects to. Defaults to "projects.json".
    Returns:
        bool: True if the projects were saved successfully, False otherwise.
    Raises:
        IOError: If there is an error writing to the file.
        OSError: If there is an error with the file system.
    This function serializes the list of Project objects to JSON format and writes it to the specified file.
    """
    try:
        def project_to_dict(proj) -> dict:
            """
            Convert a Project object to a dictionary for JSON serialization.
            Args:
                proj (Project): The Project object to convert.
            Returns:
                dict: A dictionary representation of the Project object.
            This function is used to ensure that the Project and Task objects can be serialized to JSON.
            """
            return {
                "name": proj.name,
                "description": proj.description,
                "tasks": [task.__dict__ for task in proj.tasks]
            }
        with open(filename, "w") as file:
            json.dump([project_to_dict(proj) for proj in projects], file, indent=4)
    except (IOError, OSError) as e:
        print(f"Error saving projects: {e}")
        return False
    return True
