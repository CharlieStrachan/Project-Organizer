from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QInputDialog, QCheckBox, QLineEdit, QTextEdit, QLabel,QMessageBox # type: ignore
from PySide6.QtGui import Qt, QIcon # type: ignore

from dataclasses import dataclass, field

import json

@dataclass
class Project:
    name: str
    description: str = "No description provided."
    tasks: list = field(default_factory=list)

def load_projects() -> list[Project]:
    try:
        with open("projects.json", "r") as file:
            data = json.load(file)
            return [Project(**project) for project in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON. Returning empty project list.")
        return []
def save_projects(projects: list[Project]):
    with open("projects.json", "w") as file:
        json.dump([project.__dict__ for project in projects], file, indent=4)

projects: list[Project] = load_projects()

def style_sheet(style: int):
    if style == 1:
        return """
        QMainWindow {
            background-color: #212528;
            color: #ffffff
        }

        QPushButton {
            border-radius: 5px;
            background-color: #343A40;
        }
        
        QPushButton:hover {
            background-color: #495057;
        }
        """
    elif style == 2:
        return """
        QPushButton {
            height: 50px;
        }
        """
    return

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Manager")
        self.icon = QIcon("icon.png")
        self.setWindowIcon(self.icon)
        self.setStyleSheet(style_sheet(1))
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        add_project_button = QPushButton("Add new project")
        add_project_button.setStyleSheet(style_sheet(2))
        add_project_button.clicked.connect(self.add_project)
        layout.addWidget(add_project_button)

        for project in projects:
            project_layout = QHBoxLayout()

            manage_project_button = QPushButton(project.name)
            manage_project_button.setStyleSheet(style_sheet(2))
            manage_project_button.clicked.connect(lambda _, p=project: self.manage_project(p))
            project_layout.addWidget(manage_project_button)

            edit_project_details_button = QPushButton("Edit details")
            edit_project_details_button.setStyleSheet(style_sheet(2))
            edit_project_details_button.clicked.connect(lambda _, p=project: self.edit_project_details(p))
            project_layout.addWidget(edit_project_details_button)

            remove_project_button = QPushButton("Remove project")
            remove_project_button.setStyleSheet(style_sheet(2))
            remove_project_button.clicked.connect(lambda _, p=project: self.remove_project(p))
            project_layout.addWidget(remove_project_button)

            layout.addLayout(project_layout)
        
    def add_project(self):
        self.edit_project_details(Project(name="", description="",), title="Add New Project")

    def edit_project_details(self, project: Project, title: str = "Edit Project Details"):
        dialog = QWidget()
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(self.icon)
        dialog.setStyleSheet(style_sheet(1))
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        project_name_label = QLabel("Project Name")
        project_description_label = QLabel("Project Description")
        layout.addWidget(project_name_label)
        name_edit = QLineEdit(project.name)
        name_edit.setPlaceholderText("Enter project name here...")
        layout.addWidget(name_edit)
        
        layout.addWidget(project_description_label)
        desc_edit = QTextEdit()
        desc_edit.setPlainText(project.description)
        desc_edit.setPlaceholderText("Enter project description here...")
        layout.addWidget(desc_edit)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def save_changes():
            new_name = name_edit.text().strip()
            new_desc = desc_edit.toPlainText().strip()
            if not new_name:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText(f"An error occurred:\nProject name cannot be empty.")
                error_popup.setIcon(QMessageBox.Critical)
                error_popup.exec()
                return
            if new_name != project.name and any(p.name == new_name for p in projects):
                print("Project with this name already exists.")
                return
            project.name = new_name
            project.description = new_desc
            save_projects(projects)
            self.setup_ui()
            dialog.close()

        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(dialog.close)

        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.show()
        

    def manage_project(self, project: Project):
        self.project_window = ManageProjects(project)
        self.project_window.show()

    def remove_project(self, project: Project):
        if not project:
            return
        if not any(p.name == project.name for p in projects):
            print("Project not found.")
            return
        if len(projects) == 1:
            print("Cannot remove the last project.")
            return
            
        confirmation = QInputDialog.getItem(self, "Remove Project", "Are you sure you want to remove this project?", ["Yes", "No"], 0, False)
        if confirmation[0] != "Yes":
            return
        
        projects.remove(project)
        save_projects(projects)
        self.setup_ui()

class ManageProjects(QMainWindow):
    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self.setWindowTitle(f"Project tasks for {project.name}")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet(style_sheet(1))

        self.setup_ui()
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        back_button = QPushButton("Back")
        back_button.setStyleSheet(style_sheet(2))
        back_button.clicked.connect(self.close)
        layout.addWidget(back_button)

        add_task_button = QPushButton("Add new task")
        add_task_button.setStyleSheet(style_sheet(2))
        add_task_button.clicked.connect(self.add_task)
        layout.addWidget(add_task_button)

        for task in self.project.tasks:
            task_layout = QHBoxLayout()

            task_label = QLabel(task)
            task_label.setStyleSheet("font-weight: bold;")
            task_layout.addWidget(task_label)

            remove_task_button = QPushButton("Remove Task")
            remove_task_button.setStyleSheet(style_sheet(2))
            remove_task_button.clicked.connect(lambda _, t=task: self.remove_task(t))
            task_layout.addWidget(remove_task_button)

            layout.addLayout(task_layout)

    def add_task(self):
        task_name, ok = QInputDialog.getText(self, "Add Task", "Enter the task you would like to add:")
        if not ok or not task_name:
            return
        self.project.tasks.append(task_name)
        save_projects(projects)
        self.setup_ui()

    def remove_task(self, task: str):
        if not task:
            return
        if task not in self.project.tasks:
            print("Task not found.")
            return
        
        self.project.tasks.remove(task)
        save_projects(projects)
        self.setup_ui()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()