import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
import database
from main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Търсачка - Вход")
        self.setGeometry(400, 300, 400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0d7377;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel("📄 PDF Търсачка")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Потребителско име")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Парола")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.login_btn = QPushButton("Вход")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("Нямаш акаунт? Регистрация")
        self.register_btn.setStyleSheet("background-color: #3c3c3c;")
        self.register_btn.clicked.connect(self.open_register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Грешка", "Моля, попълни всички полета!")
            return
        
        success, message = database.login_user(username, password)
        if success:
            QMessageBox.information(self, "Успех", f"Добре дошъл, {username}!")
            self.close()
            self.main_window = MainWindow(username)
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Грешка", message)
    
    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Търсачка - Регистрация")
        self.setGeometry(400, 300, 400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #0d7377;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Потребителско име")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Парола")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Потвърди парола")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_input)
        
        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
    
    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Грешка", "Моля, попълни всички полета!")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Грешка", "Паролите не съвпадат!")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "Грешка", "Паролата трябва да е поне 4 символа!")
            return
        
        success, message = database.register_user(username, password)
        if success:
            QMessageBox.information(self, "Успех", message)
            self.close()
        else:
            QMessageBox.warning(self, "Грешка", message)

if __name__ == "__main__":
    database.init_database()
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
