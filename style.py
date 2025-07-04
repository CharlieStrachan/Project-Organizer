class Style:
    """
    Class to manage the styling of the application.
    Attributes:
        BACKGROUND_COLOR (str): The background color of the application.
        FOREGROUND_COLOR (str): The foreground color of the application.
        ITEMS_COLOR (str): The color of items in the application.
        ITEMS_HOVER_COLOR (str): The hover color for items in the application.
    Methods:
        __init__(mode): Initializes the style based on the provided mode (0 for dark mode, 1 for light mode).
        style_sheet(sheet): Returns a string containing the CSS style sheet for the specified sheet.
    This class allows for easy switching between light and dark modes by changing the color scheme.
    """
    def __init__(self, mode) -> None:
        """
        Initialize the style based on the provided mode.
        Args:
            mode (int): The mode for the style. 0 for dark mode, 1 for light mode.
        Sets the background, foreground, items, and hover colors based on the mode.
        """
        if mode == 0:
            self.BACKGROUND_COLOR, self.FOREGROUND_COLOR, self.ITEMS_COLOR, self.ITEMS_HOVER_COLOR = "#212529", "#FFFFFF", "#343A40", "#495057"
        elif mode == 1:
            self.BACKGROUND_COLOR, self.FOREGROUND_COLOR, self.ITEMS_COLOR, self.ITEMS_HOVER_COLOR = "#F8F9FA", "#212529", "#E9ECEF", "#CED4DA"

    def style_sheet(self, sheet) -> str:
        """
        Returns a string containing the CSS style sheet for the specified sheet.
        Args:
            sheet (int): The sheet number for which to return the style. 
                         1 for main window styles, 2 for button styles, 3 for checkbox and button hover styles.
        Returns:
            str: A string containing the CSS style sheet for the specified sheet.
        This method allows for different styles to be applied based on the context of the application.
        """
        if sheet == 1:
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
            return """
            QPushButton {
                height: 50px;
            }
            """
        elif sheet == 3:
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
