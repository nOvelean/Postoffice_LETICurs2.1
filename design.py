#Local imports
import logging
from Structure import *
from HelpScripts import *
from db_file import *
from logFileSetup import *


#Global imports
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
    QHBoxLayout, QDialog, QFormLayout, QComboBox, QDialogButtonBox, QDialog,
    QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QMessageBox
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont




class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        logging.info("Попытка Зайти")
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            logging.info("Успешно")
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            logging.info("Не Успешно")
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")


class EditAddressDialog(QDialog):
    def __init__(self, address, postmen, clients):
        super().__init__()
        self.setWindowTitle("Редактировать адрес")
        self.address = address
        self.postmen = postmen
        self.clients = clients

        self.layout = QFormLayout()

        self.city_input = QLineEdit(self)
        self.city_input.setText(address.GetCity())
        self.layout.addRow("Город:", self.city_input)

        self.street_input = QLineEdit(self)
        self.street_input.setText(address.GetStreet())
        self.layout.addRow("Улица:", self.street_input)

        self.house_number_input = QLineEdit(self)
        self.house_number_input.setText(address.GetHouseNumber())
        self.layout.addRow("Номер дома:", self.house_number_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addRow(self.save_button)

        self.setLayout(self.layout)

    def save_changes(self):
        try:
            self.address.SetCity(self.city_input.text())
            self.address.SetStreet(self.street_input.text())

            house_number = int(self.house_number_input.text())
            self.address.SetHouseNumber(house_number)

            self.accept()
        except NotAvailableHouseNumber:
            QMessageBox.warning(self, "Ошибка", "Номер дома должен быть числом")
        except NotAvailableName:
            QMessageBox.warning(self, "Ошибка", "Название содержит недопустимые символы")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить изменения: {str(e)}")


class EditClientDialog(QDialog):
    def __init__(self, client, addresses, newspapers):
        super().__init__()
        self.setWindowTitle("Редактировать клиента")
        self.client = client
        self.addresses = addresses
        self.newspapers = newspapers

        self.layout = QVBoxLayout()
        self.name_input = QLineEdit(self)
        self.name_input.setText(client.GetFullName())
        self.layout.addWidget(QLabel("Имя:"))
        self.layout.addWidget(self.name_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setText(client.GetPhone())
        self.layout.addWidget(QLabel("Телефон:"))
        self.layout.addWidget(self.phone_input)

        self.address_combo = QComboBox(self)
        self.address_combo.addItems([f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}" for address in addresses])
        if client.GetAddress():
            self.address_combo.setCurrentText(f"{client.GetAddress().GetCity()} {client.GetAddress().GetStreet()} {client.GetAddress().GetHouseNumber()}")
        self.layout.addWidget(QLabel("Адрес:"))
        self.layout.addWidget(self.address_combo)

        self.newspapers_table = QTableWidget(0, 1)  # 1 колонка для названий газет
        self.newspapers_table.setHorizontalHeaderLabels(["Газеты"])
        self.layout.addWidget(QLabel("Подписки на газеты:"))
        self.layout.addWidget(self.newspapers_table)

        newspaper_button_layout = QHBoxLayout()
        self.add_newspaper_button = QPushButton("Добавить газету")
        self.add_newspaper_button.clicked.connect(self.add_newspaper)
        self.remove_newspaper_button = QPushButton("Удалить газету")
        self.remove_newspaper_button.clicked.connect(self.remove_newspaper)
        self.remove_newspaper_button.setEnabled(False)  # Изначально отключаем
        newspaper_button_layout.addWidget(self.add_newspaper_button)
        newspaper_button_layout.addWidget(self.remove_newspaper_button)
        self.layout.addLayout(newspaper_button_layout)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        self.populate_newspapers_table()

        self.newspapers_table.itemSelectionChanged.connect(self.update_remove_newspaper_button)

    def populate_newspapers_table(self):
        for newspaper in self.client.GetSubscriptions():
            row_position = self.newspapers_table.rowCount()
            self.newspapers_table.insertRow(row_position)
            self.newspapers_table.setItem(row_position, 0, QTableWidgetItem(newspaper.GetName()))

    def add_newspaper(self):
        dialog = SelectNewspaperDialog(self.newspapers)
        if dialog.exec_() == QDialog.Accepted:
            selected_newspapers = dialog.get_selected_newspaper()
            for newspaper_name in selected_newspapers:
                row_position = self.newspapers_table.rowCount()
                self.newspapers_table.insertRow(row_position)
                self.newspapers_table.setItem(row_position, 0, QTableWidgetItem(newspaper_name))

    def remove_newspaper(self):
        row_index = self.newspapers_table.currentRow()
        if row_index >= 0:
            self.newspapers_table.removeRow(row_index)

    def save_changes(self):
        try:
            self.client.SetFullName(self.name_input.text())
            self.client.SetPhone(self.phone_input.text())

            selected_address_info = self.address_combo.currentText()
            address = next((a for a in self.addresses if a.GetFullName() == selected_address_info), None)
            if address:
                if self.client.GetAddress():
                    self.client.GetAddress().SetClient(None)
                self.client.SetAddress(address)
                if address.GetClient():
                    address.GetClient().SetAddress(None)
                address.SetClient(self.client)

            self.client.SetSubscriptions([])
            for row in range(self.newspapers_table.rowCount()):
                newspaper_name = self.newspapers_table.item(row, 0).text()
                newspaper = next((n for n in self.newspapers if n.GetName() == newspaper_name), None)
                # print("[INFO]", newspaper.GetName(), newspaper_name)
                if newspaper:
                    self.client.AddSubscription(newspaper)


            self.accept()
        except NotAvailablePhone:
            QMessageBox.warning(self, "Ошибка", f"Номер должен быть из 10 цифр")
        except Exception:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить изменения: {str(Exception)}")

    def update_remove_newspaper_button(self):
        self.remove_newspaper_button.setEnabled(self.newspapers_table.currentRow() >= 0)

    
class SelectNewspaperDialog(QDialog):
    def __init__(self, newspapers):
        super().__init__()
        self.setWindowTitle("Выберите газету")
        self.newspapers = newspapers

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget(self)
        self.list_widget.addItems([newspaper.GetName() for newspaper in newspapers])
        self.layout.addWidget(self.list_widget)

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def get_selected_newspaper(self):
        selected_items = self.list_widget.selectedItems()
        return [item.text() for item in selected_items]


class SelectAddressDialog(QDialog):
    def __init__(self, addresses):
        super().__init__()
        self.setWindowTitle("Выберите адрес")
        self.addresses = addresses

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget(self)
        self.list_widget.addItems([f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}" for address in addresses])
        self.layout.addWidget(self.list_widget)

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def get_selected_address(self):
        selected_items = self.list_widget.selectedItems()
        return [item.text() for item in selected_items]


class EditPostmanDialog(QDialog):
    def __init__(self, postman, newspapers, addresses):
        super().__init__()
        self.setWindowTitle("Редактировать почтальона")
        self.postman = postman
        self.newspapers = newspapers
        self.addresses = addresses

        self.layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setText(postman.GetFullName())
        self.layout.addWidget(QLabel("Имя:"))
        self.layout.addWidget(self.name_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setText(postman.GetPhone())
        self.layout.addWidget(QLabel("Телефон:"))
        self.layout.addWidget(self.phone_input)

        self.newspapers_table = QTableWidget(0, 1)  # 1 колонка для названий газет
        self.newspapers_table.setHorizontalHeaderLabels(["Газеты"])
        self.layout.addWidget(QLabel("Газеты:"))
        self.layout.addWidget(self.newspapers_table)

        newspaper_button_layout = QHBoxLayout()
        self.add_newspaper_button = QPushButton("Добавить газету")
        self.add_newspaper_button.clicked.connect(self.add_newspaper)
        self.remove_newspaper_button = QPushButton("Удалить газету")
        self.remove_newspaper_button.clicked.connect(self.remove_newspaper)
        self.remove_newspaper_button.setEnabled(False)
        newspaper_button_layout.addWidget(self.add_newspaper_button)
        newspaper_button_layout.addWidget(self.remove_newspaper_button)
        self.layout.addLayout(newspaper_button_layout)

        self.addresses_table = QTableWidget(0, 1)
        self.addresses_table.setHorizontalHeaderLabels(["Адреса"])
        self.layout.addWidget(QLabel("Адреса:"))
        self.layout.addWidget(self.addresses_table)

        address_button_layout = QHBoxLayout()
        self.add_address_button = QPushButton("Добавить адрес")
        self.add_address_button.clicked.connect(self.add_address)
        self.remove_address_button = QPushButton("Удалить адрес")
        self.remove_address_button.clicked.connect(self.remove_address)
        self.remove_address_button.setEnabled(False)
        address_button_layout.addWidget(self.add_address_button)
        address_button_layout.addWidget(self.remove_address_button)
        self.layout.addLayout(address_button_layout)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        self.populate_tables()

        self.newspapers_table.itemSelectionChanged.connect(self.update_remove_newspaper_button)
        self.addresses_table.itemSelectionChanged.connect(self.update_remove_address_button)

    def populate_tables(self):
        for newspaper in self.postman.GetListOfNewspapers():
            row_position = self.newspapers_table.rowCount()
            self.newspapers_table.insertRow(row_position)
            self.newspapers_table.setItem(row_position, 0, QTableWidgetItem(newspaper.GetName()))

        for address in self.postman.GetListOfAddresses():
            row_position = self.addresses_table.rowCount()
            self.addresses_table.insertRow(row_position)
            self.addresses_table.setItem(row_position, 0, QTableWidgetItem(f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}"))

    def add_newspaper(self):
        dialog = SelectNewspaperDialog(self.newspapers)
        if dialog.exec_() == QDialog.Accepted:
            selected_newspapers = dialog.get_selected_newspaper()
            for newspaper_name in selected_newspapers:
                row_position = self.newspapers_table.rowCount()
                self.newspapers_table.insertRow(row_position)
                self.newspapers_table.setItem(row_position, 0, QTableWidgetItem(newspaper_name))

    def remove_newspaper(self):
        row_index = self.newspapers_table.currentRow()
        if row_index >= 0:
            self.newspapers_table.removeRow(row_index)

    def add_address(self):
        dialog = SelectAddressDialog(self.addresses)
        if dialog.exec_() == QDialog.Accepted:
            selected_addresses = dialog.get_selected_address()
            for address_info in selected_addresses:
                row_position = self.addresses_table.rowCount()
                self.addresses_table.insertRow(row_position)
                self.addresses_table.setItem(row_position, 0, QTableWidgetItem(address_info))

    def remove_address(self):
        row_index = self.addresses_table.currentRow()
        if row_index >= 0:
            self.addresses_table.removeRow(row_index)

    def save_changes(self):
        try:
            self.postman.SetFullName(self.name_input.text())
            self.postman.SetPhone(self.phone_input.text())

            self.postman.SetNewspapers([])
            for row in range(self.newspapers_table.rowCount()):
                newspaper_name = self.newspapers_table.item(row, 0).text()
                newspaper = next((n for n in self.newspapers if n.GetName() == newspaper_name), None)
                if newspaper:
                    self.postman.AddNewspaper(newspaper)

            self.postman.SetAddresses([])
            for address in self.addresses:
                if self.postman == address.GetPostman():
                    address.SetPostman(None)

            for row in range(self.addresses_table.rowCount()):
                address_info = self.addresses_table.item(row, 0).text()
                address = next((a for a in self.addresses if
                                f"{a.GetCity()} {a.GetStreet()} {a.GetHouseNumber()}" == address_info), None)
                if address:
                    self.postman.AddAddress(address)
                    if address.GetPostman():
                        temp = address.GetPostman().GetListOfAddresses()
                        temp.remove(address)
                        address.GetPostman().SetAddresses(temp)
                    address.SetPostman(self.postman)

            self.accept()
        except Exception:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить изменения: {str(Exception)}")

    def update_remove_newspaper_button(self):
        self.remove_newspaper_button.setEnabled(self.newspapers_table.currentRow() >= 0)

    def update_remove_address_button(self):
        self.remove_address_button.setEnabled(self.addresses_table.currentRow() >= 0)

    def get_newspaper_selection(self):
        return self.newspapers[0].GetName() if self.newspapers else None

    def get_address_selection(self):
        return f"{self.addresses[0].GetCity()} {self.addresses[0].GetStreet()} {self.addresses[0].GetHouseNumber()}" if self.addresses else None


class MainWindow(QMainWindow):

    def __init__(self):
        self.postmen = []
        self.clients = []
        self.addresses = []
        self.newspapers = []
        super().__init__()
        self.setWindowTitle("Почтовое приложение")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.clients_tab = QWidget()
        self.postmen_tab = QWidget()
        self.newspapers_tab = QWidget()
        self.reports_tab = QWidget()
        self.addresses_tab = QWidget()

        self.tabs.addTab(self.clients_tab, "Клиенты")
        self.tabs.addTab(self.postmen_tab, "Почтальоны")
        self.tabs.addTab(self.newspapers_tab, "Газеты")
        self.tabs.addTab(self.addresses_tab, "Адреса")
        self.tabs.addTab(self.reports_tab, "Отчеты")

        self.setup_clients_tab()
        self.setup_postmen_tab()
        self.setup_newspapers_tab()
        self.setup_reports_tab()
        self.setup_addresses_tab()


        self.add_sample_data()

    def update_tables(self):
        self.populate_clients_table()
        self.populate_postmen_table()
        self.populate_newspapers_table()
        self.populate_addresses_table()
        data_exporter = DataExporter(self.clients, self.postmen, self.addresses, self.newspapers)
        data_exporter.connect_to_db()
        data_exporter.clear_database()
        data_exporter.insert_addresses()
        data_exporter.insert_postmen()
        data_exporter.insert_newspapers()
        data_exporter.insert_clients()
        data_exporter.insert_subscriptions()
        data_exporter.insert_postman_addresses()
        data_exporter.insert_postman_newspapers()
        data_exporter.close_connection()

    def populate_clients_table(self):
        self.clients_table.setRowCount(0)
        for client in self.clients:
            row_position = self.clients_table.rowCount()
            self.clients_table.insertRow(row_position)

            self.clients_table.setItem(row_position, 0, QTableWidgetItem(client.GetFullName()))

            address = client.GetAddress()
            address_text = f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}" if address else "Нет адреса"
            self.clients_table.setItem(row_position, 1, QTableWidgetItem(address_text))

            self.clients_table.setItem(row_position, 2, QTableWidgetItem(client.GetPhone()))

            newspapers = client.GetSubscriptions()
            newspaper_list = ", ".join([newspaper.GetName() for newspaper in newspapers]) if newspapers else "Нет газет"
            self.clients_table.setItem(row_position, 3, QTableWidgetItem(newspaper_list))

    def populate_postmen_table(self):
        self.postmen_table.setRowCount(0)
        for postman in self.postmen:
            row_position = self.postmen_table.rowCount()
            self.postmen_table.insertRow(row_position)

            self.postmen_table.setItem(row_position, 0, QTableWidgetItem(postman.GetFullName()))

            addresses = postman.GetListOfAddresses()  # Предполагаем, что этот метод возвращает список адресов
            address_list = ", ".join(
                [f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}" for address in addresses])
            self.postmen_table.setItem(row_position, 1,
                                       QTableWidgetItem(address_list if address_list else "Нет адресов"))

            newspapers = postman.GetListOfNewspapers()  # Предполагаем, что этот метод возвращает список газет
            newspaper_list = ", ".join([newspaper.GetName() for newspaper in newspapers])
            self.postmen_table.setItem(row_position, 2,
                                       QTableWidgetItem(newspaper_list if newspaper_list else "Нет газет"))

            self.postmen_table.setItem(row_position, 3, QTableWidgetItem(postman.GetPhone()))

    def populate_newspapers_table(self):
        self.newspapers_table.setRowCount(0)
        for newspaper in self.newspapers:
            row_position = self.newspapers_table.rowCount()
            self.newspapers_table.insertRow(row_position)

            self.newspapers_table.setItem(row_position, 0, QTableWidgetItem(newspaper.GetName()))

            self.newspapers_table.setItem(row_position, 1, QTableWidgetItem(newspaper.GetText()))

            self.newspapers_table.setItem(row_position, 2, QTableWidgetItem(str(newspaper.GetAmount())))

    def populate_addresses_table(self):
        self.addresses_table.setRowCount(0)
        for address in self.addresses:
            row_position = self.addresses_table.rowCount()
            self.addresses_table.insertRow(row_position)

            address_text = f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}"
            self.addresses_table.setItem(row_position, 0, QTableWidgetItem(address_text))

            postman = address.GetPostman()  # Предполагаем, что этот метод возвращает объект почтальона
            postman_name = postman.GetFullName() if postman else "Нет почтальона"
            self.addresses_table.setItem(row_position, 1, QTableWidgetItem(postman_name))

            client = address.GetClient()
            client_name = client.GetFullName() if client else "Нет клиента"
            self.addresses_table.setItem(row_position, 2, QTableWidgetItem(client_name))

    def setup_clients_tab(self):
        layout = QVBoxLayout()
        self.clients_table = QTableWidget(0, 4)
        self.clients_table.setHorizontalHeaderLabels(["Имя", "Адрес", "Телефон", "Газеты"])

        self.search_address_input = QLineEdit()
        self.search_address_input.setPlaceholderText("Поиск адреса...")
        self.search_address_input.textChanged.connect(self.filter_addresses)

        self.search_client_input = QLineEdit()
        self.search_client_input.setPlaceholderText("Поиск клиента...")
        self.search_client_input.textChanged.connect(self.filter_clients)

        button_layout = QHBoxLayout()
        self.add_client_button = QPushButton("Добавить клиента")
        self.add_client_button.clicked.connect(self.add_client)

        self.edit_client_button = QPushButton("Редактировать клиента")
        self.edit_client_button.clicked.connect(self.edit_client)

        self.delete_client_button = QPushButton("Удалить клиента")
        self.delete_client_button.clicked.connect(self.delete_client)

        button_layout.addWidget(self.add_client_button)
        button_layout.addWidget(self.edit_client_button)
        button_layout.addWidget(self.delete_client_button)

        layout.addWidget(self.search_client_input)
        layout.addWidget(self.clients_table)
        layout.addLayout(button_layout)
        self.clients_tab.setLayout(layout)

    def setup_postmen_tab(self):
        layout = QVBoxLayout()
        self.postmen_table = QTableWidget(0, 4)
        self.postmen_table.setHorizontalHeaderLabels(["Имя", "Адреса", "Газеты", "Телефон"])

        self.search_postman_input = QLineEdit()
        self.search_postman_input.setPlaceholderText("Поиск почтальона...")
        self.search_postman_input.textChanged.connect(self.filter_postmen)

        button_layout = QHBoxLayout()
        self.add_postman_button = QPushButton("Добавить почтальона")
        self.add_postman_button.clicked.connect(self.add_postman)

        self.edit_postman_button = QPushButton("Редактировать почтальона")
        self.edit_postman_button.clicked.connect(self.edit_postman)

        self.delete_postman_button = QPushButton("Удалить почтальона")
        self.delete_postman_button.clicked.connect(self.delete_postman)

        button_layout.addWidget(self.add_postman_button)
        button_layout.addWidget(self.edit_postman_button)
        button_layout.addWidget(self.delete_postman_button)

        layout.addWidget(self.search_postman_input)
        layout.addWidget(self.postmen_table)
        layout.addLayout(button_layout)
        self.postmen_tab.setLayout(layout)

    def setup_newspapers_tab(self):
        layout = QVBoxLayout()
        self.newspapers_table = QTableWidget(0, 3)
        self.newspapers_table.setHorizontalHeaderLabels(["Название", "Номенклатура", "Количество"])

        self.search_newspaper_input = QLineEdit()
        self.search_newspaper_input.setPlaceholderText("Поиск газеты...")
        self.search_newspaper_input.textChanged.connect(self.filter_newspapers)

        button_layout = QHBoxLayout()
        self.add_newspaper_button = QPushButton("Добавить газету")
        self.add_newspaper_button.clicked.connect(self.add_newspaper)

        self.edit_newspaper_button = QPushButton("Редактировать газету")
        self.edit_newspaper_button.clicked.connect(self.edit_newspaper)

        self.delete_newspaper_button = QPushButton("Удалить газету")
        self.delete_newspaper_button.clicked.connect(self.delete_newspaper)

        self.find_readers_button = QPushButton("Найти читателей по газете")
        self.find_readers_button.clicked.connect(self.find_readers_by_selected_newspaper)
        self.find_readers_button.setEnabled(False)

        self.newspapers_table.itemSelectionChanged.connect(self.switch_find_readers_button)

        button_layout.addWidget(self.add_newspaper_button)
        button_layout.addWidget(self.edit_newspaper_button)
        button_layout.addWidget(self.delete_newspaper_button)
        button_layout.addWidget(self.find_readers_button)

        layout.addWidget(self.search_newspaper_input)
        layout.addWidget(self.newspapers_table)
        layout.addLayout(button_layout)
        self.newspapers_tab.setLayout(layout)

    def setup_reports_tab(self):
        layout = QVBoxLayout()

        postman_report_button = QPushButton("Сгенерировать отчет по почтальонам")
        postman_report_button.clicked.connect(self.generate_postman_report)
        layout.addWidget(postman_report_button)

        client_report_button = QPushButton("Сгенерировать отчет по клиентам")
        client_report_button.clicked.connect(self.generate_client_report)
        layout.addWidget(client_report_button)

        self.reports_tab.setLayout(layout)

    def generate_postman_report(self):
        pdf_file_path = "postman_report.pdf"
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter
        print("[INFO] in generate_postman_report")
        pdfmetrics.registerFont(TTFont('DejaVu', 'C:/Users/alex/Desktop/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf'))
        c.setFont('DejaVu', 12)

        c.drawString(100, height - 50, "Отчет по почтальонам")
        c.drawString(100, height - 70, "--------------------------------")


        y_position = height - 100
        for postman in self.postmen:
            c.drawString(100, y_position,
                         f"Имя: {postman.GetFullName()}, Телефон: {postman.GetPhone()}")
            y_position -= 20

            addresses = postman.GetListOfAddresses()
            if addresses:
                c.drawString(100, y_position, "Адреса:")
                y_position -= 15
                for address in addresses:
                    c.drawString(120, y_position,
                                 f"{address.GetFullName()}")
                    y_position -= 15

            newspapers = postman.GetListOfNewspapers()
            if newspapers:
                c.drawString(100, y_position, "Газеты:")
                y_position -= 15
                for newspaper in newspapers:
                    c.drawString(120, y_position, newspaper.GetName())
                    y_position -= 15

            y_position -= 10

        c.save()
        QMessageBox.information(self, "Успех", f"Отчет по почтальонам сгенерирован: {pdf_file_path}")

    def generate_client_report(self):
        pdf_file_path = "client_report.pdf"
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter

        pdfmetrics.registerFont(TTFont('DejaVu', 'C:/Users/alex/Desktop/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf'))
        c.setFont('DejaVu', 12)
        print("[INFO] в generate_client_report")

        c.drawString(100, height - 50, "Отчет по клиентам")
        c.drawString(100, height - 70, "--------------------------------")

        y_position = height - 100
        for client in self.clients:
            c.drawString(100, y_position,
                         f"Имя: {client.GetFullName()}, Телефон: {client.GetPhone()}")
            y_position -= 20
            address = client.GetAddress()
            if address:
                c.drawString(100, y_position, "Адрес:")
                y_position -= 15
                c.drawString(120, y_position, address.GetFullName())
                y_position -= 15


            newspapers = client.GetSubscriptions()
            if newspapers:
                c.drawString(100, y_position, "Газеты:")
                y_position -= 15
                for newspaper in newspapers:
                    c.drawString(120, y_position, newspaper.GetName())
                    y_position -= 15

            y_position -= 10

        c.save()
        QMessageBox.information(self, "Успех", f"Отчет по клиентам сгенерирован: {pdf_file_path}")

    def setup_addresses_tab(self):
        layout = QVBoxLayout()
        self.addresses_table = QTableWidget(0, 3)
        self.addresses_table.setHorizontalHeaderLabels(["Адрес", "Почтальон", "Клиент"])

        button_layout = QHBoxLayout()
        self.add_address_button = QPushButton("Добавить адрес")
        self.add_address_button.clicked.connect(self.add_address)

        self.edit_address_button = QPushButton("Редактировать адрес")
        self.edit_address_button.clicked.connect(self.edit_address)

        self.delete_address_button = QPushButton("Удалить адрес")
        self.delete_address_button.clicked.connect(self.delete_address)

        button_layout.addWidget(self.add_address_button)
        button_layout.addWidget(self.edit_address_button)
        button_layout.addWidget(self.delete_address_button)

        layout.addWidget(self.search_address_input)
        layout.addWidget(self.addresses_table)
        layout.addLayout(button_layout)
        self.addresses_tab.setLayout(layout)


    def add_sample_data(self):
        for newspaper in data_importer.newspapers:
            self.newspapers.append(Newspaper(newspaper['name'], int(newspaper['amount']), newspaper['text']))
            self.newspapers[-1].SetId(int(newspaper['id']))

        for address in data_importer.addresses:
            self.addresses.append(Address(address['city'], address['street'], int(address['house_number'])))
            self.addresses[-1].SetId(int(address['id']))

        for client in data_importer.clients:
            self.clients.append(Client(0, client['full_name'], int(client['id']), PhoneMask(client['phone'])))

        for postman in data_importer.postmen:
            self.postmen.append(Postman(0, postman['full_name'], int(postman['id']), PhoneMask(postman['phone'])))

        for client in data_importer.clients:
            Chosen_client = SearchbyId(int(client['id']), self.clients)
            if client['address_id'] is not None:
                Chosen_address = SearchbyId(int(client['address_id']), self.addresses)
                Chosen_client.SetAddress(Chosen_address)
                Chosen_address.SetClient(Chosen_client)

        for subscription in data_importer.subscriptions:
            Chosen_client = SearchbyId(int(subscription['client_id']), self.clients)
            Chosen_newspaper = SearchbyId(int(subscription['newspaper_id']), self.newspapers)
            Chosen_client.AddSubscription(Chosen_newspaper)

        for Postman_Newspapers in data_importer.postman_newspapers:
            Chosen_postman = SearchbyId(int(Postman_Newspapers['postman_id']), self.postmen)
            Chosen_newspaper = SearchbyId(int(Postman_Newspapers['newspaper_id']), self.newspapers)
            Chosen_postman.AddNewspaper(Chosen_newspaper)

        for Postman_Address in data_importer.postman_addresses:
            Chosen_postman = SearchbyId(int(Postman_Address['postman_id']), self.postmen)
            Chosen_address = SearchbyId(int(Postman_Address['address_id']), self.addresses)
            Chosen_postman.AddAddress(Chosen_address)
            Chosen_address.SetPostman(Chosen_postman)

        for client in self.clients:
            self.add_client_to_table(client)

        for postman in self.postmen:
            self.add_postman_to_table(postman)

        for newspaper in self.newspapers:
            self.add_newspaper_to_table(newspaper)

        for address in self.addresses:
            self.add_address_to_table(address)
        #print("[INFO] in add_sample_data")


    def add_client_to_table(self, client):
        row_position = self.clients_table.rowCount()
        self.clients_table.insertRow(row_position)
        self.clients_table.setItem(row_position, 0, QTableWidgetItem(client.GetFullName()))
        if client.GetAddress():
            self.clients_table.setItem(row_position, 1, QTableWidgetItem(client.GetAddress().GetFullName()))
        self.clients_table.setItem(row_position, 2, QTableWidgetItem(client.GetPhone()))
        if client.GetSubscriptions():
            self.clients_table.setItem(row_position, 3, QTableWidgetItem(
                ", ".join(newspaper.GetName() for newspaper in client.GetSubscriptions())))

    def add_postman_to_table(self, postman):
        row_position = self.postmen_table.rowCount()
        self.postmen_table.insertRow(row_position)
        self.postmen_table.setItem(row_position, 0, QTableWidgetItem(postman.GetFullName()))

        addresses = postman.GetListOfAddresses()
        address_list = ", ".join(address.GetCity()+ " " + address.GetStreet() + " " + address.GetHouseNumber() for address in addresses) if addresses else "Нет адресов"
        self.postmen_table.setItem(row_position, 1, QTableWidgetItem(address_list))

        newspapers = postman.GetListOfNewspapers()
        newspaper_list = ", ".join(newspaper.GetName() for newspaper in newspapers) if newspapers else "Нет газет"
        self.postmen_table.setItem(row_position, 2, QTableWidgetItem(newspaper_list))

        self.postmen_table.setItem(row_position, 3, QTableWidgetItem(postman.GetPhone()))

    def add_newspaper_to_table(self, newspaper):
        row_position = self.newspapers_table.rowCount()
        self.newspapers_table.insertRow(row_position)
        self.newspapers_table.setItem(row_position, 0, QTableWidgetItem(newspaper.GetName()))
        self.newspapers_table.setItem(row_position, 1, QTableWidgetItem(newspaper.GetText()))
        self.newspapers_table.setItem(row_position, 2, QTableWidgetItem(str(newspaper.GetAmount())))

    def add_address_to_table(self, address):
        row_position = self.addresses_table.rowCount()
        self.addresses_table.insertRow(row_position)
        self.addresses_table.setItem(row_position, 0, QTableWidgetItem(address.GetFullName()))
        self.addresses_table.setItem(row_position, 1, QTableWidgetItem(
            address.GetPostman().GetFullName() if address.GetPostman() else "Нет почтальона"))
        self.addresses_table.setItem(row_position, 2, QTableWidgetItem(
            address.GetClient().GetFullName() if address.GetClient() else "Нет клиента"))

    def delete_client(self):
        logging.info("Попытка удаления клиента")
        row_index = self.clients_table.currentRow()

        if row_index >= 0:
            client_to_delete = self.clients[row_index]
            logging.debug(f"Клиент для удаления: {client_to_delete.GetFullName()}")

            reply = QMessageBox.question(self, "Подтверждение удаления",
                                         f"Вы уверены, что хотите удалить клиента {client_to_delete.GetFullName()}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    for address in self.addresses:
                        if address.GetClient() == client_to_delete:
                            address.SetClient(None)
                            logging.debug(
                                f"Ссылка на клиента {client_to_delete.GetFullName()} удалена из адреса {address.GetFullName()}")

                    self.clients.pop(row_index)
                    self.clients_table.removeRow(row_index)
                    self.update_tables()
                    logging.info(f"Клиент {client_to_delete.GetFullName()} успешно удален")
                except Exception as e:
                    logging.error(f"Ошибка при удалении клиента {client_to_delete.GetFullName()}: {e}")
                    QMessageBox.critical(self, "Ошибка", "Произошла ошибка при удалении клиента.")
            else:
                logging.info("Удаление клиента отменено пользователем.")
        else:
            logging.warning("Не удалось удалить клиента: не выбран клиент")
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите клиента для удаления.")

    def delete_postman(self):
        logging.info("Попытка удаления почтальона")
        row_index = self.postmen_table.currentRow()

        if row_index >= 0:
            postman_to_delete = self.postmen[row_index]
            logging.debug(f"Почтальон для удаления: {postman_to_delete.GetFullName()}")

            reply = QMessageBox.question(self, "Подтверждение удаления",
                                         f"Вы уверены, что хотите удалить почтальона {postman_to_delete.GetFullName()}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    for address in self.addresses:
                        if address.GetPostman() == postman_to_delete:
                            address.SetPostman(None)
                            logging.debug(
                                f"Ссылка на почтальона {postman_to_delete.GetFullName()} удалена из адреса {address.GetFullName()}")

                    self.postmen.pop(row_index)
                    self.postmen_table.removeRow(row_index)
                    self.update_tables()
                    logging.info(f"Почтальон {postman_to_delete.GetFullName()} успешно удален")
                except Exception as e:
                    logging.error(f"Ошибка при удалении почтальона {postman_to_delete.GetFullName()}: {e}")
                    QMessageBox.critical(self, "Ошибка", "Произошла ошибка при удалении почтальона.")
            else:
                logging.info("Удаление почтальона отменено пользователем.")
        else:
            logging.warning("Не удалось удалить почтальона: не выбран почтальон")
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите почтальона для удаления.")

    def delete_newspaper(self):
        logging.info("Попытка удаления газеты")
        row_index = self.newspapers_table.currentRow()

        if row_index >= 0:
            newspaper_to_delete = self.newspapers[row_index]
            logging.debug(f"Газета для удаления: {newspaper_to_delete.GetName()}")

            reply = QMessageBox.question(self, "Подтверждение удаления",
                                         f"Вы уверены, что хотите удалить газету {newspaper_to_delete.GetName()}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    for client in self.clients:
                        subscriptions = client.GetSubscriptions()
                        new_subscriptions = [n for n in subscriptions if n != newspaper_to_delete]
                        client.SetSubscriptions(new_subscriptions)
                        logging.debug(
                            f"Газета {newspaper_to_delete.GetName()} удалена из подписок клиента {client.GetFullName()}")

                    for postman in self.postmen:
                        newspapers = postman.GetListOfNewspapers()
                        new_newspapers = [n for n in newspapers if n != newspaper_to_delete]
                        postman.SetNewspapers(new_newspapers)
                        logging.debug(
                            f"Газета {newspaper_to_delete.GetName()} удалена из списка газет почтальона {postman.GetFullName()}")

                    self.newspapers.pop(row_index)
                    self.newspapers_table.removeRow(row_index)
                    self.update_tables()
                    logging.info(f"Газета {newspaper_to_delete.GetName()} успешно удалена")
                except Exception as e:
                    logging.error(f"Ошибка при удалении газеты {newspaper_to_delete.GetName()}: {e}")
                    QMessageBox.critical(self, "Ошибка", "Произошла ошибка при удалении газеты.")
            else:
                logging.info("Удаление газеты отменено пользователем.")
        else:
            logging.warning("Не удалось удалить газету: не выбрана газета")
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите газету для удаления.")

    def delete_address(self):
        logging.info("Попытка удаления адреса")
        row_index = self.addresses_table.currentRow()

        if row_index >= 0:
            address_to_delete = self.addresses[row_index]
            logging.debug(f"Адрес для удаления: {address_to_delete.GetFullName()}")

            reply = QMessageBox.question(self, "Подтверждение удаления",
                                         f"Вы уверены, что хотите удалить адрес {address_to_delete.GetFullName()}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    for client in self.clients:
                        if client.GetAddress() == address_to_delete:
                            client.SetAddress(None)
                            logging.debug(
                                f"Адрес {address_to_delete.GetFullName()} удален у клиента {client.GetFullName()}")

                    for postman in self.postmen:
                        addresses = postman.GetListOfAddresses()
                        if address_to_delete in addresses:
                            new_addresses = [n for n in addresses if n != address_to_delete]
                            postman.SetAddresses(new_addresses)
                            logging.debug(
                                f"Адрес {address_to_delete.GetFullName()} удален из списка адресов почтальона {postman.GetFullName()}")

                    self.addresses.pop(row_index)
                    self.addresses_table.removeRow(row_index)
                    self.update_tables()
                    logging.info(f"Адрес {address_to_delete.GetFullName()} успешно удален")
                except Exception as e:
                    logging.error(f"Ошибка при удалении адреса {address_to_delete.GetFullName()}: {e}")
                    QMessageBox.critical(self, "Ошибка", "Произошла ошибка при удалении адреса.")
            else:
                logging.info("Удаление адреса отменено пользователем.")
        else:
            logging.warning("Не удалось удалить адрес: не выбран адрес")
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите адрес для удаления.")


    def edit_client(self):
        row_index = self.clients_table.currentRow()
        """Исправить редактирование адреса -- никак не влияет на результат"""
        if row_index >= 0:
            client = self.clients[row_index]

            if client:
                dialog = EditClientDialog(client, self.addresses, self.newspapers)
                if dialog.exec_() == QDialog.Accepted:
                    self.update_tables()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите клиента для редактирования.")

    def edit_postman(self):
        row_index = self.postmen_table.currentRow()
        if row_index >= 0:
            postman = self.postmen[row_index]

            if postman:
                dialog = EditPostmanDialog(postman, self.newspapers, self.addresses)
                if dialog.exec_() == QDialog.Accepted:
                    self.update_tables()


        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите почтальона для редактирования.")

    def edit_newspaper(self):
        row_index = self.newspapers_table.currentRow()
        if row_index >= 0:
            current_name = self.newspapers_table.item(row_index, 0).text()
            current_text = self.newspapers_table.item(row_index, 1).text()
            current_amount = self.newspapers_table.item(row_index, 2).text()

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать газету")

            layout = QFormLayout(dialog)

            name_input = QLineEdit(current_name)
            text_input = QLineEdit(current_text)
            amount_input = QLineEdit(current_amount)

            layout.addRow("Название:", name_input)
            layout.addRow("Номенклатура:", text_input)
            layout.addRow("Количество:", amount_input)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
            layout.addWidget(button_box)

            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)

            if dialog.exec_() == QDialog.Accepted:
                try:
                    Current_newspaper = SearchbyName(current_name, self.newspapers)
                    if Current_newspaper is None:
                        raise Exception("Газета не найдена.")

                    Current_newspaper.SetName(name_input.text())
                    Current_newspaper.SetText(text_input.text())
                    Current_newspaper.SetAmount(int(amount_input.text()))

                    self.update_tables()
                except NotAvailableAmount:
                    QMessageBox.warning(self, "Ошибка", "Количество должно быть числом.")
                    return
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось обновить газету: {str(e)}")
                    return

        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите газету для редактирования.")

    def edit_address(self):
        row_index = self.addresses_table.currentRow()
        if row_index >= 0:
            address = self.addresses[row_index]

            if address:
                dialog = EditAddressDialog(address, self.postmen, self.clients)
                if dialog.exec_() == QDialog.Accepted:
                    self.update_tables()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите адрес для редактирования.")


    def filter_clients(self):
        filter_text = self.search_client_input.text().lower()
        for row in range(self.clients_table.rowCount()):
            item = self.clients_table.item(row, 0)
            self.clients_table.setRowHidden(row, filter_text not in item.text().lower() if item else True)

    def filter_postmen(self):
        filter_text = self.search_postman_input.text().lower()
        for row in range(self.postmen_table.rowCount()):
            item = self.postmen_table.item(row, 0)
            self.postmen_table.setRowHidden(row, filter_text not in item.text().lower() if item else True)

    def filter_addresses(self):
        filter_text = self.search_address_input.text().lower()
        for row in range(self.addresses_table.rowCount()):
            item = self.addresses_table.item(row, 0)
            self.addresses_table.setRowHidden(row, filter_text not in item.text().lower() if item else True)

    def filter_newspapers(self):
        filter_text = self.search_newspaper_input.text().lower()
        for row in range(self.newspapers_table.rowCount()):
            item = self.newspapers_table.item(row, 0)
            self.newspapers_table.setRowHidden(row, filter_text not in item.text().lower() if item else True)


    def add_address(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новый адрес")

        layout = QFormLayout(dialog)

        city_input = QLineEdit()
        street_input = QLineEdit()
        house_number_input = QLineEdit()

        layout.addRow("Город:", city_input)
        layout.addRow("Улица:", street_input)
        layout.addRow("Номер дома:", house_number_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            city = city_input.text()
            street = street_input.text()
            house_number = house_number_input.text()

            if not city or not street or not house_number:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
                return
            try:
                new_address = Address(city, street, int(house_number))
            except NotAvailableHouseNumber:
                QMessageBox.warning(self, "Ошибка", "Номер дома должен быть числом.")
                return
            except NotAvailableName:
                QMessageBox.warning(self, "Ошибка", "Название содержит недопустимые символы")
                return
            except Exception:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать адрес: {str(Exception)}")
                return
            try:
                self.addresses.append(new_address)
                self.update_tables()
            except Exception:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить адрес в список: {str(Exception)}")
                return

    def add_client(self):
        # Создаем диалоговое окно для добавления нового клиента
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить нового клиента")

        layout = QFormLayout(dialog)

        # Поля для ввода данных
        name_input = QLineEdit()
        phone_input = QLineEdit()

        layout.addRow("Имя:", name_input)
        layout.addRow("Телефон:", phone_input)

        # Комбобокс для выбора адреса
        address_combobox = QComboBox()
        for address in self.addresses:  # Предполагаем, что self.addresses - это список адресов
            address_text = f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}"
            address_combobox.addItem(address_text, address)  # Сохраняем объект адреса как данные

        layout.addRow("Адрес:", address_combobox)

        # Список для выбора газет
        newspaper_list_widget = QListWidget()
        newspaper_list_widget.setSelectionMode(QListWidget.MultiSelection)  # Позволяем множественный выбор
        for newspaper in self.newspapers:  # Предполагаем, что self.newspapers - это список газет
            newspaper_list_widget.addItem(newspaper.GetName())  # Добавляем название газеты

        layout.addRow("Газеты:", newspaper_list_widget)

        # Кнопка для подтверждения добавления
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)

        # Обработка нажатия кнопки "Ok"
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            # Получаем новые данные из полей ввода
            name = name_input.text()
            phone = phone_input.text()
            selected_address = address_combobox.currentData()  # Получаем выбранный адрес
            selected_newspapers = newspaper_list_widget.selectedItems()  # Получаем выбранные газеты

            # Проверка на пустые поля
            if not name or not phone or not selected_address:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
                return

            # Создаем нового клиента
            try:
                new_client = Client(0, name, len(self.clients) + 1, phone)  # Используем длину списка клиентов для ID
            except NotAvailableName:
                QMessageBox.warning(self, "Ошибка", f"Имя содержит недопустимые символы")
                return
            except NotAvailablePhone:
                QMessageBox.warning(self, "Ошибка", f"Номер должен состоять из 10 цифр")
                return
            except Exception:
                QMessageBox.warning(self, "Ошибка", f"Неизвестна ошибка {Exception}")
                return

            # Если у выбранного адреса уже есть клиент, устанавливаем его адрес в None
            current_client = selected_address.GetClient()
            if current_client:
                try:
                    current_client.SetAddress(None)  # Устанавливаем адрес клиента в None
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось обновить адрес текущего клиента: {str(e)}")
                    return

            # Устанавливаем новый адрес для клиента
            try:
                new_client.SetAddress(selected_address)
                selected_address.SetClient(new_client)  # Устанавливаем клиента для адреса
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось установить адрес для клиента: {str(e)}")
                return

            # Добавляем выбранные газеты в подписки клиента
            for item in selected_newspapers:
                newspaper_name = item.text()
                newspaper = next((n for n in self.newspapers if n.GetName() == newspaper_name), None)
                if newspaper:
                    try:
                        new_client.AddSubscription(newspaper)
                    except Exception as e:
                        QMessageBox.warning(self, "Ошибка",
                                            f"Не удалось добавить подписку на газету '{newspaper_name}': {str(e)}")
                        return

            # Добавляем нового клиента в список и в таблицу
            try:
                self.clients.append(new_client)
                self.update_tables()  # Обновляем таблицы
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить клиента в список: {str(e)}")
                return

    def add_postman(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить нового почтальона")

        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        phone_input = QLineEdit()

        layout.addRow("Имя:", name_input)
        layout.addRow("Телефон:", phone_input)

        address_list_widget = QListWidget()
        address_list_widget.setSelectionMode(QListWidget.MultiSelection)
        for address in self.addresses:
            address_list_widget.addItem(
                f"{address.GetCity()} {address.GetStreet()} {address.GetHouseNumber()}")

        layout.addRow("Адреса:", address_list_widget)

        newspaper_list_widget = QListWidget()
        newspaper_list_widget.setSelectionMode(QListWidget.MultiSelection)
        for newspaper in self.newspapers:
            newspaper_list_widget.addItem(newspaper.GetName())

        layout.addRow("Газеты:", newspaper_list_widget)


        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)


        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text()
            phone = phone_input.text()
            selected_addresses = address_list_widget.selectedItems()
            selected_newspapers = newspaper_list_widget.selectedItems()

            if not name or not phone:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
                return
            try:
                phone = PhoneMask(phone)
                NameMask(name)
            except NotAvailablePhone:
                QMessageBox.warning(self, "Ошибка", "Телефон должен состоять из 10 цифр")
                return
            except NotAvailableName:
                QMessageBox.warning(self, "Ошибка", "Недопустимые символы в имени")
                return

            try:
                new_postman = Postman(0, name, len(self.postmen) + 1,
                                      phone)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))
                return

            for item in selected_addresses:
                address_text = item.text()
                address = next((a for a in self.addresses if
                                a.GetFullName() == address_text),
                               None)
                if address:
                    current_postman = address.GetPostman()
                    if current_postman:
                        current_postman.RemoveAddress(address)
                        address.SetPostman(None)

                    new_postman.AddAddress(address)
                    address.SetPostman(new_postman)

            for item in selected_newspapers:
                newspaper_name = item.text()
                newspaper = next((n for n in self.newspapers if n.GetName() == newspaper_name), None)
                if newspaper:
                    new_postman.AddNewspaper(newspaper)

            self.postmen.append(new_postman)
            self.update_tables()

    def add_newspaper(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новую газету")

        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        amount_input = QLineEdit()
        text_input = QLineEdit()

        layout.addRow("Название:", name_input)
        layout.addRow("Количество:", amount_input)
        layout.addRow("Номенклатура:", text_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text()
            amount = amount_input.text()
            text = text_input.text()

            if not name or not amount or not text:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
                return
            try:
                new_newspaper = Newspaper(name, int(amount), text)  # Создаем объект газеты
            except NotAvailableAmount:
                QMessageBox.warning(self, "Ошибка", "Количество должно быть числом.")
                return
            except Exception:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать газету: {str(Exception)}")
                return
            try:
                self.newspapers.append(new_newspaper)
                self.update_tables()
            except Exception:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить газету в список: {str(Exception)}")
                return


    def find_readers_by_selected_newspaper(self):
        try:
            selected_items = self.newspapers_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите газету.")
                return

            selected_newspaper_name = selected_items[0].text()

            readers_found = [client for client in self.clients if
                             selected_newspaper_name in [newspaper.GetName() for newspaper in
                                                         client.GetSubscriptions()]]
            # print("[INFO] in readers_found")
            if readers_found:
                readers_dialog = QDialog(self)
                readers_dialog.setWindowTitle(f"Читатели газеты '{selected_newspaper_name}'")
                readers_layout = QVBoxLayout(readers_dialog)

                readers_table = QTableWidget(len(readers_found), 3)
                readers_table.setHorizontalHeaderLabels(["Имя", "Телефон", "Адрес"])

                for row, reader in enumerate(readers_found):
                    readers_table.setItem(row, 0, QTableWidgetItem(reader.GetFullName()))
                    readers_table.setItem(row, 1, QTableWidgetItem(reader.GetPhone()))
                    readers_table.setItem(row, 2, QTableWidgetItem(
                        reader.GetAddress().GetFullName()))

                readers_layout.addWidget(readers_table)
                readers_dialog.setLayout(readers_layout)
                readers_dialog.exec_()
            else:
                QMessageBox.information(self, "Результат", "Читатели не найдены.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def switch_find_readers_button(self):
        selected_items = self.newspapers_table.selectedItems()
        self.find_readers_button.setEnabled(len(selected_items) > 0)
