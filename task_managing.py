from PySide6.QtWidgets import (
    QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt
import json

from models import Project, Task

class TaskManager:
    """
    Class for managing tasks within a project.
    This class handles all task-related operations including adding, removing,
    and modifying tasks within a project.
    Attributes:
        projects (list[Project]): List of all projects.
        save_callback (callable): Function to call when saving projects.
    Methods:
        clear_tasks(project, parent_widget): Clears all tasks for the specified project after user confirmation.
        add_task(project, parent_widget): Adds a new task to the specified project after user input.
        remove_task(task, project): Removes a task from the specified project.
        toggle_task_completion(task, state): Toggles the completion state of a task.
        change_task_priority(task, project, parent_widget, mode="edit"): Changes the priority of a task within the specified project.
    This class provides methods to manage tasks in a project, including adding new tasks,
    removing tasks, toggling task completion, and changing task priorities.
    """
    
    def __init__(self, projects: list[Project], save_callback) -> None:
        """
        Initializes the TaskManager.
        Args:
            projects (list[Project]): List of all projects.
            save_callback (callable): Function to call when saving projects.
        """
        self.projects = projects
        self.save_callback = save_callback
    
    def clear_tasks(self, project: Project, parent_widget) -> bool:
        """
        Clears all tasks for the specified project after user confirmation.
        Args:
            project (Project): The project for which to clear tasks.
            parent_widget: The parent widget for the confirmation dialog.
        Returns:
            bool: True if tasks were cleared successfully, False otherwise.
        This method prompts the user with a confirmation dialog before clearing the tasks.
        If the user confirms, it clears the tasks list for the project, saves the updated project list to the JSON file,
        and refreshes the UI.
        """
        item, ok = QInputDialog.getItem(parent_widget, "Clear Tasks", f"Are you sure you want to clear all tasks for '{project.name}'?", ["Yes", "No"])
        if ok and item == "Yes":
            project.tasks.clear()
            self.save_callback(self.projects)
            return True
        return False
    
    def add_task(self, project: Project, parent_widget) -> bool:
        """
        Adds a new task to the specified project after user input.
        Args:
            project (Project): The project to which the new task will be added.
            parent_widget: The parent widget for the input dialog.
        Returns:
            bool: True if task was added successfully, False otherwise.
        This method prompts the user to enter a task name. If the name is valid and does not already exist in the project,
        it creates a new Task object with the specified name and a priority based on the current number of tasks.
        If the task name already exists, it shows a warning message.
        If the user cancels the input dialog, it simply returns without making any changes.
        """
        task_name, ok = QInputDialog.getText(parent_widget, "Add Task", "Enter task name:")
        if not ok or not task_name.strip():
            return False
            
        if task_name in [t.name for t in project.tasks]:
            QMessageBox.warning(parent_widget, "Warning", "Task name already exists.")
            return False

        new_priority = len(project.tasks) + 1
        new_task = Task(name=task_name, priority=new_priority)
        project.tasks.append(new_task)
        self.save_callback(self.projects)
        
        self.change_task_priority(new_task, project, parent_widget, mode="add")
        return True
        
    def remove_task(self, task: Task, project: Project) -> None:
        """
        Removes a task from the specified project.
        Args:
            task (Task): The task to remove from the project.
            project (Project): The project from which to remove the task.
        This method removes the specified task from the project's task list,
        saves the updated project list to the JSON file.
        """
        if project and task in project.tasks:
            project.tasks.remove(task)
            self.save_callback(self.projects)
    
    def toggle_task_completion(self, task: Task, state) -> None:
        """
        Toggles the completion state of a task.
        Args:
            task (Task): The task whose completion state is to be toggled.
            state (Qt.CheckState): The new state of the task's completion checkbox.
        This method updates the task's completed attribute based on the checkbox state,
        and saves the updated project list to the JSON file.
        """
        task.completed = (state == Qt.CheckState.Checked.value)
        self.save_callback(self.projects)

    def change_task_priority(self, task: Task, project: Project, parent_widget, mode="edit") -> None:
        """
        Changes the priority of a task within the specified project.
        Args:
            task (Task): The task whose priority is to be changed.
            project (Project): The project containing the task.
            parent_widget: The parent widget for the input dialog.
            mode (str): The mode for changing the priority. "edit" for editing an existing task, "add" for adding a new task.
        This method prompts the user to select a new priority for the task. The priority is represented as a number,
        where a lower number indicates a higher priority.
        If the mode is "add", it allows the user to select a priority for the new task.
        If the mode is "edit", it allows the user to change the priority of an existing task.
        If the new priority is different from the old priority, it adjusts the priorities of other tasks accordingly,
        ensuring that no two tasks have the same priority.
        """
        if not project:
            return
            
        prompt_title = "Change Task Priority"
        prompt = "Select new priority (lower number = higher priority)"
        
        if mode == "add":
            if len(project.tasks) == 1:
                return
            prompt_title = "Task Priority"
            prompt = "Select priority for task (lower number = higher priority)"

        num_tasks = len(project.tasks)
        
        priority_options = [str(i) for i in range(1, num_tasks + 1)]
        
        priority, ok = QInputDialog.getItem(
            parent_widget,
            prompt_title,
            prompt,
            priority_options,
            min(task.priority - 1, num_tasks - 1)
        )
        
        if ok and priority:
            new_priority = int(priority)
            old_priority = task.priority
            
            if new_priority != old_priority:
                if new_priority < old_priority:
                    for t in project.tasks:
                        if t != task and new_priority <= t.priority < old_priority:
                            t.priority += 1
                else:
                    for t in project.tasks:
                        if t != task and old_priority < t.priority <= new_priority:
                            t.priority -= 1
            
                task.priority = new_priority
                
                self.save_callback(self.projects)
