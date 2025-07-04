from dataclasses import dataclass, field

@dataclass
class Task:
    """
    Class representing a task in a project.
    Attributes:
        name (str): The name of the task.
        completed (bool): Whether the task is completed. Defaults to False.
        priority (int): The priority of the task, lower number means higher priority. Defaults to 1.
    """
    name: str
    completed: bool = False
    priority: int = 1

@dataclass
class Project:
    """
    Class representing a project containing multiple tasks.
    Attributes:
        name (str): The name of the project.
        description (str): A description of the project. Defaults to "No description provided."
        tasks (list[Task]): A list of tasks associated with the project.
    """
    name: str
    description: str = "No description provided."
    tasks: list[Task] = field(default_factory=list)
