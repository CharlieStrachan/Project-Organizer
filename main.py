# Import necessary PySide6 modules
from PySide6.QtWidgets import ( # type: ignore
    QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit,
    QTextEdit, QInputDialog, QWidget, QLabel, QCheckBox, QDialog, QMessageBox,
    QStackedWidget
) # type: ignore
from PySide6.QtCore import Qt, QTimer # type: ignore
from PySide6.QtGui import QIcon # type: ignore

# Import necessary Python modules
from dataclasses import dataclass, field

# Import necessary modules for file handling and JSON
import sys
import json

# Define data classes for Task and Project
@dataclass
class Task:
    name: str
    completed: bool = False
    priority: int = 1

@dataclass
class Project:
    name: str
    description: str = "No description provided."
    tasks: list[Task] = field(default_factory=list)

# Load projects from a JSON file
def load_projects(filename="projects.json"):
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

# Save projects to a JSON file
def save_projects(projects, filename="projects.json"):
    try:
        def project_to_dict(proj):
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

# Class for styling the application
class Style:
    def __init__(self, mode):
        # Define color constants for the application
        if mode == 0:
            # Dark mode colors
            self.BACKGROUND_COLOR, self.FOREGROUND_COLOR, self.ITEMS_COLOR, self.ITEMS_HOVER_COLOR = "#212529", "#FFFFFF", "#343A40", "#495057"
        elif mode == 1:
            # Light mode colors
            self.BACKGROUND_COLOR, self.FOREGROUND_COLOR, self.ITEMS_COLOR, self.ITEMS_HOVER_COLOR = "#F8F9FA", "#212529", "#E9ECEF", "#CED4DA"

    # Style sheet
    def style_sheet(self, sheet):
        if sheet == 1:
            # General style
            return f"""
            QMainWindow {{
                background-color: {self.BACKGROUND_COLOR};
                color: {self.FOREGROUND_COLOR};
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
                
            QWidget {{
                background-color: {self.BACKGROUND_COLOR};
                color: {self.FOREGROUND_COLOR};
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {self.ITEMS_COLOR};
                border-radius: 5px;
                padding: 5px;
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
            
            QPushButton {{
                background-color: {self.ITEMS_COLOR};
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
            
            QPushButton:hover{{
                background-color: {self.ITEMS_HOVER_COLOR};
            }}
            
            QCheckBox {{
                background-color: {self.ITEMS_COLOR};
                border-radius: 5px;
                padding: 5px;
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
            
            QLabel {{
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}

            QToolTip {{
                background-color: {self.ITEMS_COLOR};
                border: 1px solid {self.ITEMS_HOVER_COLOR};
                border-radius: 5px;
                color: {self.FOREGROUND_COLOR};
                padding: 5px;
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
            """
        elif sheet == 2:
            # Larger buttons style
            return """
            QPushButton {
                height: 50px;
            }
            """
        elif sheet == 3:
            # Style for checkboxes and buttons inside the manage project window
            return f"""
            QCheckBox {{
                background-color: {self.ITEMS_COLOR};
                border-radius: 5px;
                padding: 5px;
            }}
            
            QPushButton {{
                background-color: {self.ITEMS_COLOR};
                border-radius: 5px;
                padding: 5px;
            }}
            
            QPushButton:hover {{
                background-color: {self.ITEMS_HOVER_COLOR};
            }}
            
            QCheckBox:hover {{
                background-color: {self.ITEMS_HOVER_COLOR};
            }}
            """
        else:
            return """"""

# Class for the main window
class MainWindow(QMainWindow):
    # Initialize the main window and set up the user interface
    def __init__(self):
        super().__init__()
        # Load existing projects
        self.projects = load_projects()

        # Default mode to light mode
        self.mode = 1

        # Current project being managed (None means we're on the main view)
        self.current_project = None
        
        # Track if layouts have been set up
        self.main_view_initialized = False
        self.project_view_initialized = False

        # Set the main window title, icon, style, and geometry
        self.setWindowTitle("Project Manager")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(Style(self.mode).style_sheet(1))
        self.setGeometry(100, 100, 800, 600)
        
        # Create the stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create the main view and project management view
        self.main_view = QWidget()
        self.project_view = QWidget()
        
        # Add views to the stacked widget
        self.stacked_widget.addWidget(self.main_view)
        self.stacked_widget.addWidget(self.project_view)
        
        # Setup main view initially
        self.setup_main_view()
        
        # Start with the main view
        self.stacked_widget.setCurrentWidget(self.main_view)

    # Setup the main view (project list)
    def setup_main_view(self):
        # Only initialize layout once
        if not self.main_view_initialized:
            layout = QVBoxLayout()
            self.main_view.setLayout(layout)
            self.main_view_initialized = True
        else:
            # Clear existing content
            current_layout = self.main_view.layout()
            self.clear_layout_content(current_layout)
        
        # Get the layout and cast it properly
        layout = self.main_view.layout()
        assert isinstance(layout, QVBoxLayout)  # Type hint for the linter

        horizontal_layout = QHBoxLayout()
        
        # Add projects button
        add_project_button = QPushButton("Add Project")
        add_project_button.clicked.connect(lambda: self.edit_project_details(Project(name="", description=""), mode="add"))
        add_project_button.setStyleSheet(Style(self.mode).style_sheet(2))
        horizontal_layout.addWidget(add_project_button, alignment=Qt.AlignmentFlag.AlignTop)

        # Set a shortcut (Ctrl+N) aswell as a tooltip for the add project button
        add_project_button.setShortcut("Ctrl+N")
        add_project_button.setToolTip("Add a new project (Ctrl+N)")

        layout.addLayout(horizontal_layout)

        if not self.projects:
            # If there are no projects, display a message
            no_projects_label = QLabel("No current projects.")
            no_projects_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addStretch(1)
            layout.addWidget(no_projects_label)
            no_projects_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addStretch(1)
            
            # Add stretch to push toggle button to bottom
            layout.addStretch(2)
            
            # Add toggle mode button at bottom right even when no projects
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            
            # Light/Dark mode toggle button
            toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
            toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
            toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
            toggle_mode_button.setFixedWidth(120)
            toggle_mode_button.setShortcut("Ctrl+T")
            toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
            toggle_layout.addWidget(toggle_mode_button)
            
            layout.addLayout(toggle_layout)
            return
        else:
            if len(self.projects) > 1:
                # Add three buttons to edit the project details, delete the project, and manage the tasks for each project
                clear_projects_button = QPushButton("Clear Projects")
                clear_projects_button.clicked.connect(lambda: self.clear_projects())
                clear_projects_button.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(clear_projects_button, alignment=Qt.AlignmentFlag.AlignTop)
                
                # Set a shortcut (Ctrl+C) as well as a tooltip for the clear projects button
                clear_projects_button.setShortcut("Ctrl+C")
                clear_projects_button.setToolTip("Clear all projects (Ctrl+C)")

            # Add three buttons to edit the project details, delete the project, and manage the tasks for each project
            for project in self.projects:

                horizontal_layout = QHBoxLayout()
                
                # Create a button for each project that opens the project management view
                project_label = QPushButton(project.name)
                project_label.clicked.connect(lambda _, p=project: self.show_project_view(p))
                project_label.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(project_label)

                # Add a button to edit the projects details
                edit_details_button = QPushButton("Edit Details")
                edit_details_button.clicked.connect(lambda _, p=project: self.edit_project_details(p))
                edit_details_button.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(edit_details_button)

                # Add a button to delete the project
                delete_project_button = QPushButton("Delete")
                delete_project_button.clicked.connect(lambda _, p=project: self.delete_project(p))
                delete_project_button.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(delete_project_button)

                layout.addLayout(horizontal_layout)

            # Add stretch to push toggle button to bottom
            layout.addStretch()
            
            # Add toggle mode button at bottom right
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            
            # Light/Dark mode toggle button
            toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
            toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
            toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
            toggle_mode_button.setFixedWidth(120)
            toggle_mode_button.setShortcut("Ctrl+T")
            toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
            toggle_layout.addWidget(toggle_mode_button)
            
            layout.addLayout(toggle_layout)

    # Function to toggle between light and dark mode
    def toggle_mode(self):
        # Toggle the mode variable
        self.mode = 0 if self.mode == 1 else 1

        # Update the style sheet based on the new mode
        self.setStyleSheet(Style(self.mode).style_sheet(1))

        # Refresh the UI to apply the new style
        self.refresh_ui()

    # Clear projects function
    def clear_projects(self):
        item, ok = QInputDialog.getItem(self, "Clear Projects", "Are you sure you want to clear all projects?", ["Yes", "No"])
        if ok and item == "Yes":
            self.projects = []
            save_projects(self.projects)
            self.refresh_ui()
    
    # Function to edit project details
    def edit_project_details(self, project: Project, mode="edit"):
        # Create a window to edit both project name and description
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Project Details")
        dialog.setWindowIcon(QIcon("icon.png"))
        dialog.setStyleSheet(Style(self.mode).style_sheet(1))
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        # Create a line edit for the project name
        name_edit = QLineEdit(project.name)
        name_edit.setPlaceholderText("Enter project name here...")
        layout.addWidget(name_edit)

        # Create a text edit for the project description
        desc_edit = QTextEdit()
        desc_edit.setPlainText(project.description)
        desc_edit.setPlaceholderText("Enter project description here...")
        layout.addWidget(desc_edit)

        button_layout = QHBoxLayout()

        # Create a cancel button to close the dialog without saving changes
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(cancel_button)

        # Create a done button to save the changes made
        done_button = QPushButton("Done")
        button_layout.addWidget(done_button)

        layout.addLayout(button_layout)

        # If the user clicks the cancel button, close the dialog
        cancel_button.clicked.connect(dialog.close)

        # Function to handle if the user clicks the done button
        def on_done():
            name = name_edit.text().strip()
            desc = desc_edit.toPlainText().strip()
            
            # If the name is empty, show a warning message
            if not name and mode == "add":
                QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
                return
            # If the name already exists, show a warning message
            if project.name in [p.name for p in self.projects if p != project] and mode == "add":
                QMessageBox.warning(self, "Warning", "Project name already exists.")
                return
            if mode == "edit":
                project.name = name
                if not project.name:
                    QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
                    return
                # If the project name already exists, show a warning message
                if project.name in [p.name for p in self.projects if p != project]:
                    QMessageBox.warning(self, "Warning", "Project name already exists.")
                    return
                project.description = desc
            else:
                self.projects.append(Project(name=name, description=desc))
            save_projects(self.projects)
            dialog.accept()
            self.refresh_ui()

        # Run the on_done function if the user clicks the done button
        done_button.clicked.connect(on_done)

        dialog.exec()

    # Refresh the UI after adding, editing, or deleting a project or task
    def refresh_ui(self):
        if self.stacked_widget.currentWidget() == self.main_view:
            self.setup_main_view()
        elif self.stacked_widget.currentWidget() == self.project_view:
            self.setup_project_view()

    # Function to delete a project
    def delete_project(self, project: Project):
        item, ok = QInputDialog.getItem(self, "Delete Project", f"Are you sure you want to delete the project '{project.name}'?", ["Yes", "No"])
        if ok and item == "Yes":
            self.projects.remove(project)
            save_projects(self.projects)
            self.refresh_ui()

    # Helper method to clear a layout
    def clear_layout(self, layout):
        if layout is None:
            return
        
        while layout.count():
            child = layout.takeAt(0)
            if child is not None:
                widget = child.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    child_layout = child.layout()
                    if child_layout is not None:
                        self.clear_layout(child_layout)

    # Helper method to clear layout content without deleting the layout
    def clear_layout_content(self, layout):
        if layout is None:
            return
        
        while layout.count():
            child = layout.takeAt(0)
            if child is not None:
                widget = child.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    child_layout = child.layout()
                    if child_layout is not None:
                        self.clear_layout_content(child_layout)

    # Show the project management view for a specific project
    def show_project_view(self, project: Project):
        self.current_project = project
        self.setWindowTitle(f"Project Manager - Managing {project.name}")
        self.setup_project_view()
        self.stacked_widget.setCurrentWidget(self.project_view)

    # Show the main view (project list)
    def show_main_view(self):
        self.current_project = None
        self.setWindowTitle("Project Manager")
        self.setup_main_view()
        self.stacked_widget.setCurrentWidget(self.main_view)

    # Setup the project management view
    def setup_project_view(self):
        if not self.current_project:
            return
            
        # Only initialize layout once
        if not self.project_view_initialized:
            main_layout = QVBoxLayout()
            self.project_view.setLayout(main_layout)
            self.project_view_initialized = True
        else:
            # Clear existing content
            current_layout = self.project_view.layout()
            self.clear_layout_content(current_layout)
        
        # Get the layout and cast it properly
        main_layout = self.project_view.layout()
        assert isinstance(main_layout, QVBoxLayout)

        horizontal_layout = QHBoxLayout()

        # Back button to return to the main view
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_view)
        back_button.setStyleSheet(Style(self.mode).style_sheet(2))
        horizontal_layout.addWidget(back_button)

        # Add task button to add a new task to the project
        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(lambda: self.add_task(self.current_project) if self.current_project else None)
        add_task_button.setStyleSheet(Style(self.mode).style_sheet(2))
        horizontal_layout.addWidget(add_task_button)

        # Set shortcuts and tooltips
        add_task_button.setShortcut("Ctrl+N")
        add_task_button.setToolTip("Add a new task to the project (Ctrl+N)")
        back_button.setShortcut("Esc")
        back_button.setToolTip("Go back to the main view (Esc)")

        if len(self.current_project.tasks) > 1:
            # Add a button to clear all tasks in the project if there are more than 1 tasks
            clear_tasks_button = QPushButton("Clear Tasks")
            clear_tasks_button.clicked.connect(lambda: self.clear_tasks(self.current_project) if self.current_project else None)
            clear_tasks_button.setStyleSheet(Style(self.mode).style_sheet(2))
            horizontal_layout.addWidget(clear_tasks_button)
            clear_tasks_button.setShortcut("Ctrl+C")
            clear_tasks_button.setToolTip("Clear all tasks in the project (Ctrl+C)")

        main_layout.addLayout(horizontal_layout)

        if not self.current_project.tasks:
            # If there are no tasks, display a message to say so
            no_tasks_label = QLabel(f"No tasks for {self.current_project.name}.")
            no_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(no_tasks_label)
            
            # Add stretch to push toggle button to bottom
            main_layout.addStretch()
            
            # Add toggle mode button at bottom right even when no tasks
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            
            # Light/Dark mode toggle button
            toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
            toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
            toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
            toggle_mode_button.setFixedWidth(120)
            toggle_mode_button.setShortcut("Ctrl+T")
            toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
            toggle_layout.addWidget(toggle_mode_button)
            
            main_layout.addLayout(toggle_layout)
            return
        
        # Sort tasks by priority (lowest number = highest priority)
        self.current_project.tasks.sort(key=lambda t: t.priority)
        
        for task in self.current_project.tasks:
            # For each task, create a horizontal layout with priority, checkbox and buttons
            task_layout = QHBoxLayout()
            
            # Create a priority label/button
            priority_button = QPushButton(f"#{task.priority}")
            priority_button.clicked.connect(lambda _, t=task: self.change_task_priority(t))
            priority_button.setStyleSheet(Style(self.mode).style_sheet(3))
            priority_button.setFixedWidth(50)
            priority_button.setFixedHeight(30)
            task_layout.addWidget(priority_button)
            
            # Create a checkbox for the task
            task_checkbox = QCheckBox(task.name)
            task_checkbox.setChecked(task.completed)
            task_checkbox.stateChanged.connect(lambda state, t=task: self.toggle_task_completion(t, state))
            task_checkbox.setStyleSheet(Style(self.mode).style_sheet(3))
            task_checkbox.setFixedHeight(30)
            task_layout.addWidget(task_checkbox)
            
            # Create a button to remove the task
            delete_task_button = QPushButton("Remove Task")
            delete_task_button.clicked.connect(lambda _, t=task: self.remove_task(t))
            delete_task_button.setStyleSheet(Style(self.mode).style_sheet(3))
            delete_task_button.setFixedHeight(30)
            task_layout.addWidget(delete_task_button)
            
            main_layout.addLayout(task_layout)
        
        # Add stretch to push toggle button to bottom
        main_layout.addStretch()
        
        # Add toggle mode button at bottom right after task list
        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()
        
        # Light/Dark mode toggle button
        toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
        toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
        toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
        toggle_mode_button.setFixedWidth(120)
        toggle_mode_button.setShortcut("Ctrl+T")
        toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
        toggle_layout.addWidget(toggle_mode_button)
        
        main_layout.addLayout(toggle_layout)

    # Function to clear all tasks in the project
    def clear_tasks(self, project: Project):
        item, ok = QInputDialog.getItem(self, "Clear Tasks", f"Are you sure you want to clear all tasks for '{project.name}'?", ["Yes", "No"])
        if ok and item == "Yes":
            project.tasks.clear()
            save_projects(self.projects)
            self.refresh_ui()
    
    # Function to add a new task to the project
    def add_task(self, project: Project):
        task_name, ok = QInputDialog.getText(self, "Add Task", "Enter task name:")
        # Check if the task name already exists
        if task_name in [t.name for t in project.tasks]:
            # If it does, show a warning message and return
            QMessageBox.warning(self, "Warning", "Task name already exists.")
            return
        if ok and task_name:
            # Calculate the priority for the new task (lowest priority by default)
            new_priority = len(project.tasks) + 1
            
            # Create and add the new task
            project.tasks.append(Task(name=task_name, priority=new_priority))
            save_projects(self.projects)
        else:
            # If the user did not enter a task name or cancelled, do not add the task and return
            return
        self.change_task_priority(project.tasks[-1], mode="add")
        self.refresh_ui()
        
    # Function to remove a task from the project    
    def remove_task(self, task: Task):
        if self.current_project:
            self.current_project.tasks.remove(task)
            save_projects(self.projects)
            self.refresh_ui()
    
    # Function to toggle the completion state of a task
    def toggle_task_completion(self, task: Task, state):
        task.completed = (state == Qt.CheckState.Checked.value)
        save_projects(self.projects)

    # Function to change or add the priority of a task depending on the mode (edit or add)
    def change_task_priority(self, task: Task, mode="edit"):
        if not self.current_project:
            return
            
        # Prompt message and title based on the mode
        prompt_title = "Change Task Priority"
        prompt = "Select new priority (lower number = higher priority)"
        
        if mode == "add":
            # If there is no other tasks, dont prompt for priority
            if len(self.current_project.tasks) == 1:
                return
            prompt_title = "Task Priority"
            prompt = "Select priority for task (lower number = higher priority)"

        # Get the current number of tasks
        num_tasks = len(self.current_project.tasks)
        
        # Create a list of priority options from 1 to num_tasks
        priority_options = [str(i) for i in range(1, num_tasks + 1)]
        
        # Show dialog to select priority
        priority, ok = QInputDialog.getItem(
            self,
            prompt_title,
            prompt,
            priority_options,
            min(task.priority - 1, num_tasks - 1)
        )
        
        if ok and priority:
            new_priority = int(priority)
            old_priority = task.priority
            
            # Update priorities of other tasks to maintain consistency
            if new_priority != old_priority:
                # If moving to a higher priority (lower number)
                if new_priority < old_priority:
                    for t in self.current_project.tasks:
                        if t != task and new_priority <= t.priority < old_priority:
                            t.priority += 1
                # If moving to a lower priority (higher number)
                else:
                    for t in self.current_project.tasks:
                        if t != task and old_priority < t.priority <= new_priority:
                            t.priority -= 1
            
                # Set the new priority for this task
                task.priority = new_priority
                
                # Save and refresh
                save_projects(self.projects)
                self.refresh_ui()

# Main function to create and show the main window
def main():
    # Create the application instance 
    app = QApplication(sys.argv)

    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec())
    
# Run the main function when the application is executed
if __name__ == "__main__":
    main()
