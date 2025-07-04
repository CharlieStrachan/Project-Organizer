from PySide6.QtWidgets import (
    QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit,
    QTextEdit, QInputDialog, QWidget, QLabel, QCheckBox, QDialog, QMessageBox,
    QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from dataclasses import dataclass, field

import sys
import json

from style import Style
from data import load_projects, save_projects
from models import Project, Task
from task_managing import TaskManager

class MainWindow(QMainWindow):
    """
    Main window class for the Project Manager application.
    This class initializes the main window, sets up the UI, and handles user interactions.
    Attributes:
        projects (list[Project]): A list of Project objects loaded from the JSON file.
        mode (int): The current mode of the application (0 for dark mode, 1 for light mode).
        current_project (Project): The currently selected project.
        main_view_initialized (bool): Flag to check if the main view has been initialized.
        project_view_initialized (bool): Flag to check if the project view has been initialized.
        task_manager (TaskManager): Instance for managing tasks.
    Methods:
        __init__(): Initializes the main window and sets up the UI.
        setup_main_view(): Sets up the main view of the application.
        setup_project_view(): Sets up the project view for managing tasks.
        toggle_mode(): Toggles between light and dark mode.
        clear_projects(): Clears all projects after user confirmation.
        edit_project_details(project, mode="edit"): Opens a dialog to edit project details.
        refresh_ui(): Refreshes the UI based on the current view.
        delete_project(project): Deletes a project after user confirmation.
        clear_layout(layout): Clears all widgets from a layout.
        show_project_view(project): Displays the project view for the selected project.
        show_main_view(): Displays the main view of the application.
    """
    def __init__(self) -> None:
        """
        Initializes the main window and sets up the UI.
        Loads projects from the JSON file and sets the initial mode to light mode.
        """
        super().__init__()
        self.projects = load_projects()

        self.mode = 1

        self.current_project = None
        
        self.main_view_initialized = False
        self.project_view_initialized = False
        
        self.task_manager = TaskManager(self.projects, save_projects)

        self.setWindowTitle("Project Manager")
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(Style(self.mode).style_sheet(1))
        self.setGeometry(100, 100, 800, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.main_view = QWidget()
        self.project_view = QWidget()
        
        self.stacked_widget.addWidget(self.main_view)
        self.stacked_widget.addWidget(self.project_view)
        
        self.setup_main_view()
        
        self.stacked_widget.setCurrentWidget(self.main_view)

    def setup_main_view(self) -> None:
        """
        Sets up the main view of the application.
        This method initializes the layout, adds buttons for adding projects, and displays the list of current projects.
        If there are no projects, it displays a message indicating that there are no current projects.
        """
        if not self.main_view_initialized:
            layout = QVBoxLayout()
            self.main_view.setLayout(layout)
            self.main_view_initialized = True
        else:
            current_layout = self.main_view.layout()
            self.clear_layout_content(current_layout)
        
        layout = self.main_view.layout()
        assert isinstance(layout, QVBoxLayout)

        horizontal_layout = QHBoxLayout()
        
        add_project_button = QPushButton("Add Project")
        add_project_button.clicked.connect(lambda: self.edit_project_details(Project(name="", description=""), mode="add"))
        add_project_button.setStyleSheet(Style(self.mode).style_sheet(2))
        horizontal_layout.addWidget(add_project_button, alignment=Qt.AlignmentFlag.AlignTop)

        add_project_button.setShortcut("Ctrl+N")
        add_project_button.setToolTip("Add a new project (Ctrl+N)")

        layout.addLayout(horizontal_layout)

        if not self.projects:
            no_projects_label = QLabel("No current projects.")
            no_projects_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addStretch(1)
            layout.addWidget(no_projects_label)
            no_projects_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addStretch(1)
            
            layout.addStretch(2)
            
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            
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
                clear_projects_button = QPushButton("Clear Projects")
                clear_projects_button.clicked.connect(lambda: self.clear_projects())
                clear_projects_button.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(clear_projects_button, alignment=Qt.AlignmentFlag.AlignTop)
                
                clear_projects_button.setShortcut("Ctrl+C")
                clear_projects_button.setToolTip("Clear all projects (Ctrl+C)")

            for project in self.projects:

                horizontal_layout = QHBoxLayout()
                
                project_label = QPushButton(project.name)
                project_label.clicked.connect(lambda _, p=project: self.show_project_view(p))
                project_label.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(project_label)

                edit_details_button = QPushButton("Edit Details")
                edit_details_button.clicked.connect(lambda _, p=project: self.edit_project_details(p))
                edit_details_button.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(edit_details_button)

                delete_project_button = QPushButton("Delete")
                delete_project_button.clicked.connect(lambda _, p=project: self.delete_project(p))
                delete_project_button.setStyleSheet(Style(self.mode).style_sheet(2))
                horizontal_layout.addWidget(delete_project_button)

                layout.addLayout(horizontal_layout)

            layout.addStretch()
            
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            
            toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
            toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
            toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
            toggle_mode_button.setFixedWidth(120)
            toggle_mode_button.setShortcut("Ctrl+T")
            toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
            toggle_layout.addWidget(toggle_mode_button)
            
            layout.addLayout(toggle_layout)

    def toggle_mode(self) -> None:
        """
        Toggles the application mode between light and dark.
        This method changes the mode attribute and updates the style sheet accordingly.
        It also refreshes the UI to apply the new style.
        """
        self.mode = 0 if self.mode == 1 else 1

        self.setStyleSheet(Style(self.mode).style_sheet(1))

        self.refresh_ui()

    def clear_projects(self) -> None:
        """
        Clears all projects after user confirmation.
        This method prompts the user with a confirmation dialog and, if confirmed, clears the projects list,
        saves the empty list to the JSON file, and refreshes the UI.
        """
        item, ok = QInputDialog.getItem(self, "Clear Projects", "Are you sure you want to clear all projects?", ["Yes", "No"])
        if ok and item == "Yes":
            self.projects = []
            save_projects(self.projects)
            self.refresh_ui()
    
    def edit_project_details(self, project: Project, mode="edit") -> None:
        """
        Opens a dialog to edit project details.
        Args:
            project (Project): The project to edit. If mode is "add", a new project will be created.
            mode (str): The mode for editing the project. "edit" for editing an existing project, "add" for creating a new one.
        This method creates a dialog with fields for the project name and description.
        If the mode is "add", it allows the user to enter a new project name and description.
        If the mode is "edit", it pre-fills the fields with the existing project details.
        It validates the input and updates the project list accordingly.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Project Details")
        dialog.setWindowIcon(QIcon("icon.png"))
        dialog.setStyleSheet(Style(self.mode).style_sheet(1))
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        name_edit = QLineEdit(project.name)
        name_edit.setPlaceholderText("Enter project name here...")
        layout.addWidget(name_edit)

        desc_edit = QTextEdit()
        desc_edit.setPlainText(project.description)
        desc_edit.setPlaceholderText("Enter project description here...")
        layout.addWidget(desc_edit)

        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(cancel_button)

        done_button = QPushButton("Done")
        button_layout.addWidget(done_button)

        layout.addLayout(button_layout)

        cancel_button.clicked.connect(dialog.close)

        def on_done() -> None:
            """
            Handles the "Done" button click event.
            Validates the input fields and updates the project list.
            If the project name is empty or already exists, it shows a warning message.
            If the mode is "edit", it updates the existing project; if "add", it creates a new project.
            """
            name = name_edit.text().strip()
            desc = desc_edit.toPlainText().strip()
            
            if not name and mode == "add":
                QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
                return
            if project.name in [p.name for p in self.projects if p != project] and mode == "add":
                QMessageBox.warning(self, "Warning", "Project name already exists.")
                return
            if mode == "edit":
                project.name = name
                if not project.name:
                    QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
                    return
                if project.name in [p.name for p in self.projects if p != project]:
                    QMessageBox.warning(self, "Warning", "Project name already exists.")
                    return
                project.description = desc
            else:
                self.projects.append(Project(name=name, description=desc))
            save_projects(self.projects)
            dialog.accept()
            self.refresh_ui()

        done_button.clicked.connect(on_done)

        dialog.exec()

    def refresh_ui(self) -> None:
        """
        Refreshes the UI based on the current view.
        This method checks which view is currently active (main view or project view)
        and calls the appropriate setup method to update the UI.
        """
        if self.stacked_widget.currentWidget() == self.main_view:
            self.setup_main_view()
        elif self.stacked_widget.currentWidget() == self.project_view:
            self.setup_project_view()

    def delete_project(self, project: Project) -> None:
        """
        Deletes a project after user confirmation.
        Args:
            project (Project): The project to delete.
        This method prompts the user with a confirmation dialog before deleting the project.
        If the user confirms, it removes the project from the projects list, saves the updated list to the JSON file,
        and refreshes the UI.
        """
        item, ok = QInputDialog.getItem(self, "Delete Project", f"Are you sure you want to delete the project '{project.name}'?", ["Yes", "No"])
        if ok and item == "Yes":
            self.projects.remove(project)
            save_projects(self.projects)
            self.refresh_ui()

    def clear_layout(self, layout) -> None:
        """
        Clears all widgets from a layout.
        Args:
            layout (QLayout): The layout to clear.
        This method iterates through all items in the layout and removes them,
        setting their parent to None and deleting them to free up resources.
        """
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

    def clear_layout_content(self, layout) -> None:
        """
        Clears all widgets from a layout without deleting the layout itself.
        Args:
            layout (QLayout): The layout to clear.
        This method iterates through all items in the layout and removes them,
        setting their parent to None and deleting them to free up resources.
        """
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

    def show_project_view(self, project: Project) -> None:
        """
        Displays the project view for the selected project.
        Args:
            project (Project): The project to display in the project view.
        This method sets the current project to the selected project, updates the window title,
        and calls the setup method to initialize the project view.
        """
        self.current_project = project
        self.setWindowTitle(f"Project Manager - Managing {project.name}")
        self.setup_project_view()
        self.stacked_widget.setCurrentWidget(self.project_view)

    def show_main_view(self) -> None:
        """
        Displays the main view of the application.
        This method resets the current project to None, updates the window title,
        and calls the setup method to initialize the main view.
        """
        self.current_project = None
        self.setWindowTitle("Project Manager")
        self.setup_main_view()
        self.stacked_widget.setCurrentWidget(self.main_view)

    def setup_project_view(self) -> None:
        """
        Sets up the project view for managing tasks.
        This method initializes the layout, adds buttons for adding tasks, clearing tasks,
        and displays the list of tasks for the current project.
        If there are no tasks, it displays a message indicating that there are no tasks for the project.
        """
        if not self.current_project:
            return
            
        if not self.project_view_initialized:
            main_layout = QVBoxLayout()
            self.project_view.setLayout(main_layout)
            self.project_view_initialized = True
        else:
            current_layout = self.project_view.layout()
            self.clear_layout_content(current_layout)
        
        main_layout = self.project_view.layout()
        assert isinstance(main_layout, QVBoxLayout)

        horizontal_layout = QHBoxLayout()

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_view)
        back_button.setStyleSheet(Style(self.mode).style_sheet(2))
        horizontal_layout.addWidget(back_button)

        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(lambda: self.add_task_and_refresh())
        add_task_button.setStyleSheet(Style(self.mode).style_sheet(2))
        horizontal_layout.addWidget(add_task_button)

        add_task_button.setShortcut("Ctrl+N")
        add_task_button.setToolTip("Add a new task to the project (Ctrl+N)")
        back_button.setShortcut("Esc")
        back_button.setToolTip("Go back to the main view (Esc)")

        if len(self.current_project.tasks) > 1:
            clear_tasks_button = QPushButton("Clear Tasks")
            clear_tasks_button.clicked.connect(lambda: self.clear_tasks_and_refresh())
            clear_tasks_button.setStyleSheet(Style(self.mode).style_sheet(2))
            horizontal_layout.addWidget(clear_tasks_button)
            clear_tasks_button.setShortcut("Ctrl+C")
            clear_tasks_button.setToolTip("Clear all tasks in the project (Ctrl+C)")

        main_layout.addLayout(horizontal_layout)

        if not self.current_project.tasks:
            no_tasks_label = QLabel(f"No tasks for {self.current_project.name}.")
            no_tasks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(no_tasks_label)
            
            main_layout.addStretch()
            
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            
            toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
            toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
            toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
            toggle_mode_button.setFixedWidth(120)
            toggle_mode_button.setShortcut("Ctrl+T")
            toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
            toggle_layout.addWidget(toggle_mode_button)
            
            main_layout.addLayout(toggle_layout)
            return
        
        self.current_project.tasks.sort(key=lambda t: t.priority)
        
        for task in self.current_project.tasks:
            task_layout = QHBoxLayout()
            
            priority_button = QPushButton(f"#{task.priority}")
            priority_button.clicked.connect(lambda _, t=task: self.change_priority_and_refresh(t))
            priority_button.setStyleSheet(Style(self.mode).style_sheet(3))
            priority_button.setFixedWidth(50)
            priority_button.setFixedHeight(30)
            task_layout.addWidget(priority_button)
            
            task_checkbox = QCheckBox(task.name)
            task_checkbox.setChecked(task.completed)
            task_checkbox.stateChanged.connect(lambda state, t=task: self.task_manager.toggle_task_completion(t, state))
            task_checkbox.setStyleSheet(Style(self.mode).style_sheet(3))
            task_checkbox.setFixedHeight(30)
            task_layout.addWidget(task_checkbox)
            
            delete_task_button = QPushButton("Remove Task")
            delete_task_button.clicked.connect(lambda _, t=task: self.remove_task_and_refresh(t))
            delete_task_button.setStyleSheet(Style(self.mode).style_sheet(3))
            delete_task_button.setFixedHeight(30)
            task_layout.addWidget(delete_task_button)
            
            main_layout.addLayout(task_layout)
        
        main_layout.addStretch()
        
        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()
        
        toggle_mode_button = QPushButton("🌙" if self.mode == 0 else "☀️")
        toggle_mode_button.setStyleSheet(Style(self.mode).style_sheet(2))
        toggle_mode_button.clicked.connect(lambda: self.toggle_mode())
        toggle_mode_button.setFixedWidth(120)
        toggle_mode_button.setShortcut("Ctrl+T")
        toggle_mode_button.setToolTip("Toggle light/dark mode (Ctrl+T)")
        toggle_layout.addWidget(toggle_mode_button)
        
        main_layout.addLayout(toggle_layout)

    def add_task_and_refresh(self) -> None:
        """Helper method to add a task and refresh the UI."""
        if self.current_project:
            if self.task_manager.add_task(self.current_project, self):
                self.refresh_ui()

    def clear_tasks_and_refresh(self) -> None:
        """Helper method to clear tasks and refresh the UI."""
        if self.current_project:
            if self.task_manager.clear_tasks(self.current_project, self):
                self.refresh_ui()

    def remove_task_and_refresh(self, task: Task) -> None:
        """Helper method to remove a task and refresh the UI."""
        if self.current_project:
            self.task_manager.remove_task(task, self.current_project)
            self.refresh_ui()

    def change_priority_and_refresh(self, task: Task) -> None:
        """Helper method to change task priority and refresh the UI."""
        if self.current_project:
            self.task_manager.change_task_priority(task, self.current_project, self)
            self.refresh_ui()

if __name__ == "__main__":
    """
    Main entry point for the Project Manager application.
    """
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())
