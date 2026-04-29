import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QFrame,
    QFileDialog, QMessageBox, QProgressDialog, QApplication,
    QDialog, QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt
import database
from pdf_processor import index_pdf_folder

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.user_id = database.get_user_id(username)
        self.setWindowTitle(f"PDF Търсачка - Добре дошъл, {username}")
        self.setGeometry(300, 200, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0d7377;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                font-family: monospace;
                font-size: 13px;
            }
            QFrame {
                background-color: #252525;
                border-radius: 10px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        top_frame = QFrame()
        top_layout = QHBoxLayout()
        
        welcome_label = QLabel(f"👤 Здравей, {self.username}!")
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.logout_btn = QPushButton("Изход")
        self.logout_btn.setStyleSheet("background-color: #c0392b;")
        self.logout_btn.clicked.connect(self.logout)
        
        top_layout.addWidget(welcome_label)
        top_layout.addStretch()
        top_layout.addWidget(self.logout_btn)
        top_frame.setLayout(top_layout)
        main_layout.addWidget(top_frame)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3c3c3c;")
        main_layout.addWidget(separator)
        
        search_frame = QFrame()
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Въведи дума или фраза за търсене...")
        self.search_input.returnPressed.connect(self.search)
        
        self.search_btn = QPushButton("Търси")
        self.search_btn.clicked.connect(self.search)
        
        search_layout.addWidget(self.search_input, 4)
        search_layout.addWidget(self.search_btn, 1)
        search_frame.setLayout(search_layout)
        main_layout.addWidget(search_frame)
        
        results_label = QLabel("📄 Резултати от търсенето:")
        results_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Тук ще се покажат резултатите...")
        main_layout.addWidget(self.results_text, 1)
        
        bottom_layout = QHBoxLayout()
        
        self.index_btn = QPushButton("📁 Индексирай PDF папка")
        self.index_btn.clicked.connect(self.index_pdfs)
        
        self.my_files_btn = QPushButton("📚 Моите файлове")
        self.my_files_btn.clicked.connect(self.show_my_files)

        self.delete_btn = QPushButton("🗑 Изтрий файл")
        self.delete_btn.clicked.connect(self.delete_file)
        self.delete_btn.setStyleSheet("background-color: #c0392b;")
        bottom_layout.addWidget(self.delete_btn)
        
        bottom_layout.addWidget(self.index_btn)
        bottom_layout.addWidget(self.my_files_btn)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
    
    def search(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Грешка", "Моля, въведи какво да търся!")
            return
        
        self.results_text.clear()
        self.results_text.append(f"🔍 Търсене на: '{query}'\n")
        self.results_text.append("-" * 50)
        
        results = database.search_words(self.user_id, query)
        
        if not results:
            self.results_text.append("\n❌ Няма намерени резултати.")
            self.results_text.append("\n💡 Съвети:")
            self.results_text.append("   • Увери се, че си индексирал PDF файлове (бутон 'Индексирай PDF папка')")
            self.results_text.append("   • Провери дали думата е написана правилно")
            return
        
        files_dict = {}
        for filename, page_num in results:
            if filename not in files_dict:
                files_dict[filename] = []
            if page_num not in files_dict[filename]:
                files_dict[filename].append(page_num)
        
        self.results_text.append(f"\n✅ Намерени резултати в {len(files_dict)} файла:\n")
        
        for filename, pages in files_dict.items():
            pages_str = ", ".join([f"стр. {p}" for p in sorted(pages)])
            self.results_text.append(f"📄 **{filename}**")
            self.results_text.append(f"   → {pages_str}")
            self.results_text.append("")
    
    def index_pdfs(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Избери папка с PDF файлове", 
            ""
        )
        if not folder:
            return
        
        progress = QProgressDialog("Индексиране на PDF файлове...", "Отказ", 0, 100, self)
        progress.setWindowTitle("Моля, изчакайте")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        def update_progress(current, total, filename):
            percent = int((current / total) * 100)
            progress.setLabelText(f"Обработвам: {filename}\n({current} от {total})")
            progress.setValue(percent)
            QApplication.processEvents()
        
        successful, failed, message = index_pdf_folder(
            folder, 
            self.username, 
            update_progress
        )
        
        progress.setValue(100)
        QMessageBox.information(self, "Индексиране завършено", message)
        
        if successful > 0:
            self.results_text.clear()
            self.results_text.append(f"✅ Успешно индексирани {successful} PDF файла!")
            self.results_text.append(f"\nСега може да търсиш в тях с полето за търсене горе.")
    
    def show_my_files(self):
        files = database.get_user_files(self.user_id)
        
        if not files:
            QMessageBox.information(
                self, 
                "Моите файлове", 
                "Все още нямаш индексирани PDF файлове.\n\nНатисни 'Индексирай PDF папка' за да добавиш."
            )
            return
        
        message = "📚 Индексирани файлове:\n\n" + "\n".join([f"• {f}" for f in files])
        QMessageBox.information(self, "Моите файлове", message)
    
    def delete_file(self):
        files = database.get_user_files(self.user_id)
        
        if not files:
            QMessageBox.information(
                self, 
                "Изтриване на файл", 
                "Нямаш индексирани файлове за изтриване."
            )
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Изтриване на файл")
        dialog.setGeometry(450, 350, 400, 150)
        dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout()
        
        label = QLabel("Избери файл за изтриване от индекса:")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.addItems(files)
        layout.addWidget(combo)
        
        layout.addSpacing(20)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_file = combo.currentText()
            self.confirm_delete(selected_file)
    
    def confirm_delete(self, filename):
        reply = QMessageBox.question(
            self,
            "Потвърди изтриване",
            f"Сигурен ли си, че искаш да изтриеш:\n\n📄 {filename}\n\nСлед това няма да можеш да търсиш в този файл, докато не го индексираш отново.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, count, message = database.delete_file_from_index(self.user_id, filename)
            
            if success:
                QMessageBox.information(self, "Успех", message)
                self.results_text.clear()
                self.results_text.append(f"Файлът '{filename}' беше изтрит от индекса.")
                self.results_text.append(f"Изтрити {count} записа (уникални думи).")
            else:
                QMessageBox.warning(self, "Грешка", message)
        
    def logout(self):
        self.close()
        from main import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()