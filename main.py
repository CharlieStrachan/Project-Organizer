from PySide6.QtWidgets import ( # type: ignore
    QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit,
    QTextEdit, QInputDialog, QWidget, QLabel, QCheckBox, QDialog, QMessageBox
) # type: ignore
from PySide6.QtCore import Qt # type: ignore
from PySide6.QtGui import QIcon, QFont # type: ignore

from dataclasses import dataclass, field

import sys
import json

app = QApplication(sys.argv)

@dataclass
class Task:
    name: str
    completed: bool = False

@dataclass
class Project:
    name: str
    description: str = "No description provided."
    tasks: list[Task] = field(default_factory=list)

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

def save_projects(projects, filename="projects.json"):
    def project_to_dict(proj):
        return {
            "name": proj.name,
            "description": proj.description,
            "tasks": [task.__dict__ for task in proj.tasks]
        }
    with open(filename, "w") as file:
        json.dump([project_to_dict(proj) for proj in projects], file, indent=4)

icon = QIcon("icon.png")
font = QFont("Arial", 14)

projects = load_projects()

def style_sheet(sheet):
    if sheet == 1:
        return """
        QMainWindow {
            background-color: #212529;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 15px;
        }
                
        QWidget {
            background-color: #212529;
            color: white;
        }
        
        QLineEdit, QTextEdit {
            background-color: #343A40;
            border-radius: 5px;
            padding: 5px;
        }
        
        QPushButton {
            background-color: #343A40;
            border-radius: 5px;
            font-family: Arial, sans-serif;
        }
        
        QPushButton:hover{
            background-color: #495057;
        }
        
        QCheckBox {
            background-color: #343A40;
            border-radius: 5px;
            padding: 5px;
            font-size: 18px;
        }
        
        """
    elif sheet == 2:
        return """
        QPushButton {
            height: 50px;
            font-size: 18px;
        }
        """
    elif sheet == 3:
        return """
        QCheckBox {
            background-color: #343A40;
            border-radius: 5px;
            padding: 5px;
            font-size: 18px;
        }
        
        QPushButton {
            background-color: #343A40;
            border-radius: 5px;
            padding: 5px;
            font-size: 18px;
        }
        
        QPushButton:hover {
            background-color: #495057;
        }
        
        QCheckBox:hover {
            background-color: #495057;
        }
        """
    else:
        return """"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Manager")
        self.setWindowIcon(icon)
        self.setStyleSheet(style_sheet(1))
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        horizontal_layout = QHBoxLayout()
        add_project_button = QPushButton("Add Project")
        add_project_button.clicked.connect(lambda: self.edit_project_details(Project(name="", description=""), mode="add"))
        add_project_button.setStyleSheet(style_sheet(2))
        horizontal_layout.addWidget(add_project_button, alignment=Qt.AlignTop)
        
        clear_projects_button = QPushButton("Clear Projects")
        clear_projects_button.clicked.connect(lambda: self.clear_projects())
        clear_projects_button.setStyleSheet(style_sheet(2))
        horizontal_layout.addWidget(clear_projects_button, alignment=Qt.AlignTop)

        layout.addLayout(horizontal_layout)
        
        if not projects:
            no_projects_label = QLabel("No current projects.")
            no_projects_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_projects_label)
            layout.addStretch()
            return
        else:
            for project in projects:
                horizontal_layout = QHBoxLayout()
                project_label = QPushButton(project.name)
                project_label.clicked.connect(lambda _, p=project: ManageProject(p).show())
                project_label.setStyleSheet(style_sheet(2))
                horizontal_layout.addWidget(project_label)

                edit_details_button = QPushButton("Edit Details")
                edit_details_button.clicked.connect(lambda _, p=project: self.edit_project_details(p))
                edit_details_button.setStyleSheet(style_sheet(2))
                horizontal_layout.addWidget(edit_details_button)

                delete_project_button = QPushButton("Delete")
                delete_project_button.clicked.connect(lambda _, p=project: self.delete_project(p))
                delete_project_button.setStyleSheet(style_sheet(2))
                horizontal_layout.addWidget(delete_project_button)

                layout.addLayout(horizontal_layout)

            layout.addStretch()

    def clear_projects(self):
        item, ok = QInputDialog.getItem(self, "Clear Projects", "Are you sure you want to clear all projects?", ["Yes", "No"])
        if ok and item == "Yes":
            global projects
            projects = []
            save_projects(projects)
            self.refresh_ui()
            
    def edit_project_details(self, project: Project, mode="edit"):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Project Details")
        dialog.setWindowIcon(icon)
        dialog.setStyleSheet(style_sheet(1))
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        name_edit = QLineEdit(project.name)
        name_edit.setPlaceholderText("Enter project name here...")
        layout.addWidget(name_edit)

        if not name_edit:
            QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
            return

        desc_edit = QTextEdit()
        desc_edit.setPlainText(project.description)
        desc_edit.setPlaceholderText("Enter project description here...")
        layout.addWidget(desc_edit)
        
        if not desc_edit:
            QMessageBox.warning(self, "Warning", "Project description cannot be empty.")
            return

        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(cancel_button)

        done_button = QPushButton("Done")
        button_layout.addWidget(done_button)

        layout.addLayout(button_layout)

        cancel_button.clicked.connect(dialog.close)

        def on_done():
            name = name_edit.text().strip()
            desc = desc_edit.toPlainText().strip()
            if not name:
                return
            if mode == "edit":
                project.name = name
                project.description = desc
            else:
                projects.append(Project(name=name, description=desc))
            save_projects(projects)
            dialog.accept()
            self.refresh_ui()

        done_button.clicked.connect(on_done)

        dialog.exec()

    def refresh_ui(self):
        self.centralWidget().deleteLater()
        self.setup_ui()

    def delete_project(self, project: Project):
        item, ok = QInputDialog.getItem(self, "Delete Project", f"Are you sure you want to delete the project '{project.name}'?", ["Yes", "No"])
        if ok and item == "Yes":
            projects.remove(project)
            save_projects(projects)
            self.refresh_ui()

class ManageProject(QMainWindow):
    def __init__(self, project: Project):
        super().__init__()
        self.project: Project = project
        self.setWindowTitle(f"Managing {project.name}")
        self.setWindowIcon(icon)
        self.setStyleSheet(style_sheet(1))
        self.setGeometry(0, 0, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        horizontal_layout = QHBoxLayout()

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.close)
        back_button.setStyleSheet(style_sheet(2))
        horizontal_layout.addWidget(back_button)

        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(lambda: self.add_task(self.project))
        add_task_button.setStyleSheet(style_sheet(2))
        horizontal_layout.addWidget(add_task_button)

        self.layout.addLayout(horizontal_layout)

        if not self.project.tasks:
            no_tasks_label = QLabel(f"No tasks for {self.project.name}.")
            no_tasks_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(no_tasks_label)
            return
        
        for task in self.project.tasks:
            task_layout = QHBoxLayout()
            
            task_checkbox = QCheckBox(task.name)
            task_checkbox.setChecked(task.completed)
            task_checkbox.stateChanged.connect(lambda state, t=task: self.toggle_task_completion(t, state))
            task_checkbox.setStyleSheet(style_sheet(3))
            task_checkbox.setFixedHeight(30)
            task_layout.addWidget(task_checkbox)
            
            delete_task_button = QPushButton("Remove Task")
            delete_task_button.clicked.connect(lambda _, t=task: self.remove_task(t))
            delete_task_button.setStyleSheet(style_sheet(3))
            delete_task_button.setFixedHeight(30)
            task_layout.addWidget(delete_task_button)
            
            self.layout.addLayout(task_layout)
        self.layout.addStretch()
    
    def add_task(self, project: Project):
        task_name, ok = QInputDialog.getText(self, "Add Task", "Enter task name:")
        if ok and task_name:
            project.tasks.append(Task(name=task_name))
            save_projects(projects)
            self.refresh_ui()
    
    def remove_task(self, task: Task):
        self.project.tasks.remove(task)
        save_projects(projects)
        self.refresh_ui()
    
    def toggle_task_completion(self, task: Task, state):
        task.completed = (state == Qt.CheckState.Checked.value)
        save_projects(projects)
    
    def refresh_ui(self):
        self.centralWidget().deleteLater()
        self.setup_ui()

if __name__ == "__main__":
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
