import sys
import elevate
import sqlite3
import jdatetime
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QTime, Qt, QSize
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QMenuBar,
    QMenu,
    QAction,
    QToolBar,
    QGridLayout,
    QTextBrowser,
)


class ProgramStatus:
    def __init__(self):
        self.status_file = "status.db"
        self.conn = sqlite3.connect(self.status_file)
        self.cursor = self.conn.cursor()
        self.initialize_status_table()

    def initialize_status_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS program_status (
            id INTEGER PRIMARY KEY,
            running INTEGER
        )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

        select_query = """
        SELECT * FROM program_status WHERE id = 1
        """
        self.cursor.execute(select_query)
        result = self.cursor.fetchone()
        if not result:
            insert_query = """
            INSERT INTO program_status (id, running) VALUES (?, ?)
            """
            values = (1, 0)
            self.cursor.execute(insert_query, values)
            self.conn.commit()

    def start_program(self):
        update_query = """
        UPDATE program_status SET running = ? WHERE id = ?
        """
        values = (1, 1)
        self.cursor.execute(update_query, values)
        self.conn.commit()

    def stop_program(self):
        update_query = """
        UPDATE program_status SET running = ? WHERE id = ?
        """
        values = (0, 1)
        self.cursor.execute(update_query, values)
        self.conn.commit()

    def is_running(self):
        select_query = """
        SELECT running FROM program_status WHERE id = ?
        """
        values = (1,)
        self.cursor.execute(select_query, values)
        result = self.cursor.fetchone()
        if result:
            return bool(result[0])
        return False


class InvoiceDB:
    def __init__(self):
        self.db_name = "invoices.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Invoice (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                device_name TEXT,
                                hourly_rate TEXT,
                                snack_invoice TEXT,
                                device_invoice TEXT,
                                total_invoice TEXT,
                                invoice_time TEXT,
                                invoice_date TEXT
                            )"""
        )
        self.conn.commit()

    def add_to_db(
        self,
        device_name,
        hourly_rate,
        snack_invoice,
        device_invoice,
        total_invoice,
        invoice_time,
        invoice_date,
    ):
        self.cursor.execute(
            """INSERT INTO Invoice (device_name, hourly_rate, snack_invoice, device_invoice, total_invoice, invoice_time, invoice_date)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                device_name,
                hourly_rate,
                snack_invoice,
                device_invoice,
                total_invoice,
                invoice_time,
                invoice_date,
            ),
        )
        self.conn.commit()

    def load_from_db(self):
        self.cursor.execute("SELECT * FROM Invoice")
        data = self.cursor.fetchall()
        return data

    def delete_all_data_from_table(self):
        self.cursor.execute("DELETE FROM Invoice")
        self.conn.commit()

    def close_db(self):
        self.cursor.close()
        self.conn.close()


class DailyInvoiceDB:
    def __init__(self):
        self.db_name = "daily-invoices.db"
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS DailyInvoice (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                total_device_invoice TEXT,
                                total_snack_invoice TEXT,
                                total_device_and_snack_invoice TEXT,
                                last_refresh_time TEXT
                            )"""
        )
        self.conn.commit()

    def add_to_db(
        self,
        total_device_invoice,
        total_snack_invoice,
        total_device_and_snack_invoice,
        last_refresh_time,
    ):
        self.cursor.execute(
            """INSERT INTO DailyInvoice (total_device_invoice, total_snack_invoice, total_device_and_snack_invoice, last_refresh_time)
                               VALUES (?, ?, ?, ?)""",
            (
                total_device_invoice,
                total_snack_invoice,
                total_device_and_snack_invoice,
                last_refresh_time,
            ),
        )
        self.conn.commit()

    def load_from_db(self):
        self.cursor.execute("SELECT * FROM DailyInvoice")
        data = self.cursor.fetchall()
        return data

    def delete_all_data_from_table(self):
        self.cursor.execute("DELETE FROM DailyInvoice")
        self.conn.commit()

    def close_db(self):
        self.cursor.close()
        self.conn.close()


class DebtorListDB:
    def __init__(self):
        self.conn = sqlite3.connect("debtor-list.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS debtors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            device_debt INTEGER,
            snack_debt INTEGER,
            time TEXT,
            date TEXT
        )"""
        self.cursor.execute(query)
        self.conn.commit()

    def add_debtor(self, first_name, last_name, device_debt, snack_debt, time, date):
        query = """INSERT INTO debtors (first_name, last_name, device_debt, snack_debt, time, date)
                   VALUES (?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(
            query, (first_name, last_name, device_debt, snack_debt, time, date)
        )
        self.conn.commit()

    def get_debtors(self):
        query = """SELECT * FROM debtors"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def edit_debtor(
        self, debtor_id, first_name, last_name, device_debt, snack_debt, time, date
    ):
        query = """UPDATE debtors SET first_name = ?, last_name = ?, device_debt = ?, snack_debt = ?, time = ?, date = ?
                WHERE id = ?"""
        self.cursor.execute(
            query,
            (first_name, last_name, device_debt, snack_debt, time, date, debtor_id),
        )
        self.conn.commit()

    def delete_debtor(self, debtor_id):
        query = """DELETE FROM debtors WHERE id = ?"""
        self.cursor.execute(query, (debtor_id,))
        self.conn.commit()

    def delete_all_debtors(self):
        query = """DELETE FROM debtors"""
        self.cursor.execute(query)
        self.conn.commit()


class PaymentMethodDB:
    def __init__(self):
        self.conn = sqlite3.connect("payment-method.db")
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()

        query = """CREATE TABLE IF NOT EXISTS payments (
                    cash INTEGER,
                    card INTEGER,
                    total INTEGER,
                    time TEXT,
                    date TEXT
                  )"""
        cursor.execute(query)

    def add_payment(self, cash, card, total, time, date):
        cursor = self.conn.cursor()

        query = "INSERT INTO payments VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (cash, card, total, time, date))

        self.conn.commit()

    def delete_payment(self, cash, card):
        cursor = self.conn.cursor()

        query = "DELETE FROM payments WHERE cash=? AND card=?"
        cursor.execute(query, (cash, card))

        self.conn.commit()

    def delete_all_payments(self):
        cursor = self.conn.cursor()

        query = "DELETE FROM payments"
        cursor.execute(query)

        self.conn.commit()

    def get_payments(self):
        cursor = self.conn.cursor()

        query = "SELECT * FROM payments"
        cursor.execute(query)

        return cursor.fetchall()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_title = "PlayNet"
        self.app_icon = QIcon("main-window.ico")
        self.app_size = 1025, 700
        self.app_start_point = 100, 100
        self.app_version = "1.0"

        self.time_zero = "00:00:00"

        self.invoice_db = InvoiceDB()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.app_title)
        self.setWindowIcon(self.app_icon)
        self.setGeometry(*self.app_start_point, *self.app_size)

        menubar = QMenuBar()

        menubar.setStyleSheet(
            """
            QMenuBar {
                background-color: #f2f2f2;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            
            QMenuBar::item {
                color: #333333;
                padding: 10px;
                background-color: transparent;
            }
            
            QMenuBar::item:selected {
                background-color: #e6e6e6;
            }
            
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 5px 20px;
            }
            
            QMenu::item:selected {
                background-color: #e6e6e6;
            }
        """
        )

        help_menu = QMenu("Help", self)
        menubar.addMenu(help_menu)

        about_action = QAction("About", self)
        about_action.setShortcut("Ctrl+A")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        help_menu.addSeparator()

        contact_action = QAction("Contact", self)
        contact_action.setShortcut("Ctrl+B")
        contact_action.triggered.connect(self.contact)
        help_menu.addAction(contact_action)

        help_menu.addSeparator()

        manual_action = QAction("Manual", self)
        manual_action.setShortcut("Ctrl+C")
        manual_action.triggered.connect(self.manual)
        help_menu.addAction(manual_action)

        self.setMenuBar(menubar)

        toolbar = QToolBar()

        toolbar.setStyleSheet(
            """
            QToolBar {
                background-color: #f2f2f2;
                border: none;
                padding: 5px;
            }

            QToolButton {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border: none;
                background-color: transparent;
            }

            QToolButton:hover {
                background-color: #e6e6e6;
            }

            QToolButton:pressed {
                background-color: #cccccc;
            }
        """
        )

        toolbar.setIconSize(QSize(75, 75))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        invoice_window_action = QAction(QIcon("invoice-window.ico"), "Invoice", self)
        toolbar.addAction(invoice_window_action)
        invoice_window_action.triggered.connect(self.invoice)

        daily_invoice_window_action = QAction(
            QIcon("daily-invoice-window.ico"), "Daily Invoice", self
        )
        toolbar.addAction(daily_invoice_window_action)
        daily_invoice_window_action.triggered.connect(self.daily_invoice)

        debtor_list_window_action = QAction(
            QIcon("debtor-list-window.ico"), "Debtor List", self
        )
        toolbar.addAction(debtor_list_window_action)
        debtor_list_window_action.triggered.connect(self.debtor_list)

        payment_method_window_action = QAction(
            QIcon("payment-method-window.ico"), "Payment Method", self
        )
        toolbar.addAction(payment_method_window_action)
        payment_method_window_action.triggered.connect(self.payment_method)

        self.addToolBar(toolbar)

        main_layout = QHBoxLayout()
        tab_widget = QTabWidget()

        tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: none;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                color: #333333;
                background-color: #f2f2f2;
                padding: 15px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:hover {
                background-color: #e6e6e6;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                font-weight: bold;
            }
            
            QTabWidget::tab-pane {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-top: none;
                padding: 20px;
            }
        """
        )

        main_layout.addWidget(tab_widget)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        ########################################################################################################################

        self.timer_1 = QTimer()
        self.timer_1.timeout.connect(self.update_timer_1)

        timer_label_1 = QLabel("Timer:")
        start_time_label_1 = QLabel("Start Time:")
        stop_time_label_1 = QLabel("Stop Time:")

        self.timer_lineedit_1 = QLineEdit()
        self.start_time_lineedit_1 = QLineEdit()
        self.stop_time_lineedit_1 = QLineEdit()

        self.timer_lineedit_1.setReadOnly(True)
        self.start_time_lineedit_1.setReadOnly(True)
        self.stop_time_lineedit_1.setReadOnly(True)

        self.timer_lineedit_1.setText(self.time_zero)

        device_box_1_1 = QGroupBox()
        device_box_layout_1_1 = QFormLayout(device_box_1_1)
        device_box_layout_1_1.addRow(timer_label_1, self.timer_lineedit_1)
        device_box_layout_1_1.addRow(start_time_label_1, self.start_time_lineedit_1)
        device_box_layout_1_1.addRow(stop_time_label_1, self.stop_time_lineedit_1)

        self.start_timer_button_1 = QPushButton("Start Timer")
        self.stop_timer_button_1 = QPushButton("Stop Timer")
        self.reset_timer_button_1 = QPushButton("Reset Timer")

        self.start_timer_button_1.clicked.connect(self.start_timer_1)
        self.stop_timer_button_1.clicked.connect(self.stop_timer_1)
        self.reset_timer_button_1.clicked.connect(self.reset_timer_1)

        self.stop_timer_button_1.setDisabled(True)
        self.reset_timer_button_1.setDisabled(True)

        device_box_2_1 = QGroupBox()
        device_box_layout_2_1 = QFormLayout(device_box_2_1)
        device_box_layout_2_1.addRow(self.start_timer_button_1)
        device_box_layout_2_1.addRow(self.stop_timer_button_1)
        device_box_layout_2_1.addRow(self.reset_timer_button_1)

        device_groupbox_1 = QGroupBox("Device")
        device_layout_1 = QVBoxLayout(device_groupbox_1)
        device_layout_1.addWidget(device_box_1_1)
        device_layout_1.addStretch()
        device_layout_1.addWidget(device_box_2_1)

        snack_name_label_1 = QLabel("Name:")
        snack_price_label_1 = QLabel("Price:")

        self.snack_name_lineedit_1 = QLineEdit()
        self.snack_price_lineedit_1 = QLineEdit()

        snack_box_1_1 = QGroupBox()
        snack_box_layout_1_1 = QFormLayout(snack_box_1_1)
        snack_box_layout_1_1.addRow(snack_name_label_1, self.snack_name_lineedit_1)
        snack_box_layout_1_1.addRow(snack_price_label_1, self.snack_price_lineedit_1)

        snack_list_label_1 = QLabel("List")
        self.snack_table_1 = QTableWidget()

        self.snack_table_1.setColumnCount(2)
        self.snack_table_1.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_1.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_1.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_1 = QGroupBox()
        snack_box_layout_2_1 = QFormLayout(snack_box_2_1)
        snack_box_layout_2_1.addRow(snack_list_label_1)
        snack_box_layout_2_1.addRow(self.snack_table_1)

        self.snack_add_button_1 = QPushButton("Add Snack")
        self.reset_snack_list_button_1 = QPushButton("Reset list")

        self.snack_add_button_1.clicked.connect(self.add_snack_to_table_1)
        self.reset_snack_list_button_1.clicked.connect(self.reset_snack_list_1)

        self.snack_add_button_1.setDisabled(True)
        self.reset_snack_list_button_1.setDisabled(True)

        snack_box_3_1 = QGroupBox()
        snack_box_layout_3_1 = QFormLayout(snack_box_3_1)
        snack_box_layout_3_1.addRow(self.snack_add_button_1)
        snack_box_layout_3_1.addRow(self.reset_snack_list_button_1)

        snack_groupbox_1 = QGroupBox("Snack")
        snack_layout_1 = QVBoxLayout(snack_groupbox_1)
        snack_layout_1.addWidget(snack_box_1_1)
        snack_layout_1.addStretch()
        snack_layout_1.addWidget(snack_box_2_1)
        snack_layout_1.addStretch()
        snack_layout_1.addWidget(snack_box_3_1)

        device_name_label_1 = QLabel("Device:")
        hourly_rate_label_1 = QLabel("Hourly Rate:")
        snack_invoice_label_1 = QLabel("Snack Invoice:")
        device_invoice_label_1 = QLabel("Device Invoice:")
        total_invoice_label_1 = QLabel("Total Invoice:")
        invoice_time_label_1 = QLabel("Invoice Time:")
        invoice_date_label_1 = QLabel("Invoice Date :")

        self.device_name_lineedit_1 = QLineEdit()
        self.hourly_rate_lineedit_1 = QLineEdit()
        self.snack_invoice_lineedit_1 = QLineEdit()
        self.device_invoice_lineedit_1 = QLineEdit()
        self.total_invoice_lineedit_1 = QLineEdit()
        self.invoice_time_lineedit_1 = QLineEdit()
        self.invoice_date_lineedit_1 = QLineEdit()

        self.snack_invoice_lineedit_1.setReadOnly(True)
        self.device_invoice_lineedit_1.setReadOnly(True)
        self.total_invoice_lineedit_1.setReadOnly(True)
        self.invoice_time_lineedit_1.setReadOnly(True)
        self.invoice_date_lineedit_1.setReadOnly(True)

        self.device_name_lineedit_1.setText("A")
        self.hourly_rate_lineedit_1.setText("50000")

        self.device_name_lineedit_1.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_1.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_1 = QGroupBox()
        invoice_box_layout_1_1 = QFormLayout(invoice_box_1_1)
        invoice_box_layout_1_1.addRow(device_name_label_1, self.device_name_lineedit_1)
        invoice_box_layout_1_1.addRow(hourly_rate_label_1, self.hourly_rate_lineedit_1)
        invoice_box_layout_1_1.addRow(
            device_invoice_label_1, self.device_invoice_lineedit_1
        )
        invoice_box_layout_1_1.addRow(
            snack_invoice_label_1, self.snack_invoice_lineedit_1
        )
        invoice_box_layout_1_1.addRow(
            total_invoice_label_1, self.total_invoice_lineedit_1
        )
        invoice_box_layout_1_1.addRow(
            invoice_time_label_1, self.invoice_time_lineedit_1
        )
        invoice_box_layout_1_1.addRow(
            invoice_date_label_1, self.invoice_date_lineedit_1
        )

        self.calculate_invoice_button_1 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_1 = QPushButton("Pay Invoice")
        self.reset_invoice_button_1 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_1.clicked.connect(self.calculate_invoice_1)
        self.pay_invoice_button_1.clicked.connect(self.pay_invoice_1)
        self.reset_invoice_button_1.clicked.connect(self.reset_invoice_1)

        self.calculate_invoice_button_1.setDisabled(True)
        self.pay_invoice_button_1.setDisabled(True)

        invoice_box_2_1 = QGroupBox()
        invoice_box_layout_2_1 = QFormLayout(invoice_box_2_1)
        invoice_box_layout_2_1.addRow(self.calculate_invoice_button_1)
        invoice_box_layout_2_1.addRow(self.pay_invoice_button_1)
        invoice_box_layout_2_1.addRow(self.reset_invoice_button_1)

        invoice_groupbox_1 = QGroupBox("Invoce")
        invoice_layout_1 = QVBoxLayout(invoice_groupbox_1)
        invoice_layout_1.addWidget(invoice_box_1_1)
        invoice_layout_1.addStretch()
        invoice_layout_1.addWidget(invoice_box_2_1)

        tab_1 = QWidget()
        tab_widget.addTab(tab_1, "System A")

        main_layout_1 = QHBoxLayout()
        main_layout_1.addWidget(device_groupbox_1)
        main_layout_1.addWidget(snack_groupbox_1)
        main_layout_1.addWidget(invoice_groupbox_1)
        tab_1.setLayout(main_layout_1)

        ########################################################################################################################

        self.timer_2 = QTimer()
        self.timer_2.timeout.connect(self.update_timer_2)

        timer_label_2 = QLabel("Timer:")
        start_time_label_2 = QLabel("Start Time:")
        stop_time_label_2 = QLabel("Stop Time:")

        self.timer_lineedit_2 = QLineEdit()
        self.start_time_lineedit_2 = QLineEdit()
        self.stop_time_lineedit_2 = QLineEdit()

        self.timer_lineedit_2.setReadOnly(True)
        self.start_time_lineedit_2.setReadOnly(True)
        self.stop_time_lineedit_2.setReadOnly(True)

        self.timer_lineedit_2.setText(self.time_zero)

        device_box_1_2 = QGroupBox()
        device_box_layout_1_2 = QFormLayout(device_box_1_2)
        device_box_layout_1_2.addRow(timer_label_2, self.timer_lineedit_2)
        device_box_layout_1_2.addRow(start_time_label_2, self.start_time_lineedit_2)
        device_box_layout_1_2.addRow(stop_time_label_2, self.stop_time_lineedit_2)

        self.start_timer_button_2 = QPushButton("Start Timer")
        self.stop_timer_button_2 = QPushButton("Stop Timer")
        self.reset_timer_button_2 = QPushButton("Reset Timer")

        self.start_timer_button_2.clicked.connect(self.start_timer_2)
        self.stop_timer_button_2.clicked.connect(self.stop_timer_2)
        self.reset_timer_button_2.clicked.connect(self.reset_timer_2)

        self.stop_timer_button_2.setDisabled(True)
        self.reset_timer_button_2.setDisabled(True)

        device_box_2_2 = QGroupBox()
        device_box_layout_2_2 = QFormLayout(device_box_2_2)
        device_box_layout_2_2.addRow(self.start_timer_button_2)
        device_box_layout_2_2.addRow(self.stop_timer_button_2)
        device_box_layout_2_2.addRow(self.reset_timer_button_2)

        device_groupbox_2 = QGroupBox("Device")
        device_layout_2 = QVBoxLayout(device_groupbox_2)
        device_layout_2.addWidget(device_box_1_2)
        device_layout_2.addStretch()
        device_layout_2.addWidget(device_box_2_2)

        snack_name_label_2 = QLabel("Name:")
        snack_price_label_2 = QLabel("Price:")

        self.snack_name_lineedit_2 = QLineEdit()
        self.snack_price_lineedit_2 = QLineEdit()

        snack_box_1_2 = QGroupBox()
        snack_box_layout_1_2 = QFormLayout(snack_box_1_2)
        snack_box_layout_1_2.addRow(snack_name_label_2, self.snack_name_lineedit_2)
        snack_box_layout_1_2.addRow(snack_price_label_2, self.snack_price_lineedit_2)

        snack_list_label_2 = QLabel("List")
        self.snack_table_2 = QTableWidget()

        self.snack_table_2.setColumnCount(2)
        self.snack_table_2.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_2.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_2.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_2 = QGroupBox()
        snack_box_layout_2_2 = QFormLayout(snack_box_2_2)
        snack_box_layout_2_2.addRow(snack_list_label_2)
        snack_box_layout_2_2.addRow(self.snack_table_2)

        self.snack_add_button_2 = QPushButton("Add Snack")
        self.reset_snack_list_button_2 = QPushButton("Reset list")

        self.snack_add_button_2.clicked.connect(self.add_snack_to_table_2)
        self.reset_snack_list_button_2.clicked.connect(self.reset_snack_list_2)

        self.snack_add_button_2.setDisabled(True)
        self.reset_snack_list_button_2.setDisabled(True)

        snack_box_3_2 = QGroupBox()
        snack_box_layout_3_2 = QFormLayout(snack_box_3_2)
        snack_box_layout_3_2.addRow(self.snack_add_button_2)
        snack_box_layout_3_2.addRow(self.reset_snack_list_button_2)

        snack_groupbox_2 = QGroupBox("Snack")
        snack_layout_2 = QVBoxLayout(snack_groupbox_2)
        snack_layout_2.addWidget(snack_box_1_2)
        snack_layout_2.addStretch()
        snack_layout_2.addWidget(snack_box_2_2)
        snack_layout_2.addStretch()
        snack_layout_2.addWidget(snack_box_3_2)

        device_name_label_2 = QLabel("Device:")
        hourly_rate_label_2 = QLabel("Hourly Rate:")
        snack_invoice_label_2 = QLabel("Snack Invoice:")
        device_invoice_label_2 = QLabel("Device Invoice:")
        total_invoice_label_2 = QLabel("Total Invoice:")
        invoice_time_label_2 = QLabel("Invoice Time:")
        invoice_date_label_2 = QLabel("Invoice Date :")

        self.device_name_lineedit_2 = QLineEdit()
        self.hourly_rate_lineedit_2 = QLineEdit()
        self.snack_invoice_lineedit_2 = QLineEdit()
        self.device_invoice_lineedit_2 = QLineEdit()
        self.total_invoice_lineedit_2 = QLineEdit()
        self.invoice_time_lineedit_2 = QLineEdit()
        self.invoice_date_lineedit_2 = QLineEdit()

        self.snack_invoice_lineedit_2.setReadOnly(True)
        self.device_invoice_lineedit_2.setReadOnly(True)
        self.total_invoice_lineedit_2.setReadOnly(True)
        self.invoice_time_lineedit_2.setReadOnly(True)
        self.invoice_date_lineedit_2.setReadOnly(True)

        self.device_name_lineedit_2.setText("B")
        self.hourly_rate_lineedit_2.setText("50000")

        self.device_name_lineedit_2.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_2.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_2 = QGroupBox()
        invoice_box_layout_1_2 = QFormLayout(invoice_box_1_2)
        invoice_box_layout_1_2.addRow(device_name_label_2, self.device_name_lineedit_2)
        invoice_box_layout_1_2.addRow(hourly_rate_label_2, self.hourly_rate_lineedit_2)
        invoice_box_layout_1_2.addRow(
            device_invoice_label_2, self.device_invoice_lineedit_2
        )
        invoice_box_layout_1_2.addRow(
            snack_invoice_label_2, self.snack_invoice_lineedit_2
        )
        invoice_box_layout_1_2.addRow(
            total_invoice_label_2, self.total_invoice_lineedit_2
        )
        invoice_box_layout_1_2.addRow(
            invoice_time_label_2, self.invoice_time_lineedit_2
        )
        invoice_box_layout_1_2.addRow(
            invoice_date_label_2, self.invoice_date_lineedit_2
        )

        self.calculate_invoice_button_2 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_2 = QPushButton("Pay Invoice")
        self.reset_invoice_button_2 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_2.clicked.connect(self.calculate_invoice_2)
        self.pay_invoice_button_2.clicked.connect(self.pay_invoice_2)
        self.reset_invoice_button_2.clicked.connect(self.reset_invoice_2)

        self.calculate_invoice_button_2.setDisabled(True)
        self.pay_invoice_button_2.setDisabled(True)

        invoice_box_2_2 = QGroupBox()
        invoice_box_layout_2_2 = QFormLayout(invoice_box_2_2)
        invoice_box_layout_2_2.addRow(self.calculate_invoice_button_2)
        invoice_box_layout_2_2.addRow(self.pay_invoice_button_2)
        invoice_box_layout_2_2.addRow(self.reset_invoice_button_2)

        invoice_groupbox_2 = QGroupBox("Invoce")
        invoice_layout_2 = QVBoxLayout(invoice_groupbox_2)
        invoice_layout_2.addWidget(invoice_box_1_2)
        invoice_layout_2.addStretch()
        invoice_layout_2.addWidget(invoice_box_2_2)

        tab_2 = QWidget()
        tab_widget.addTab(tab_2, "System B")

        main_layout_2 = QHBoxLayout()
        main_layout_2.addWidget(device_groupbox_2)
        main_layout_2.addWidget(snack_groupbox_2)
        main_layout_2.addWidget(invoice_groupbox_2)
        tab_2.setLayout(main_layout_2)

        ########################################################################################################################

        self.timer_3 = QTimer()
        self.timer_3.timeout.connect(self.update_timer_3)

        timer_label_3 = QLabel("Timer:")
        start_time_label_3 = QLabel("Start Time:")
        stop_time_label_3 = QLabel("Stop Time:")

        self.timer_lineedit_3 = QLineEdit()
        self.start_time_lineedit_3 = QLineEdit()
        self.stop_time_lineedit_3 = QLineEdit()

        self.timer_lineedit_3.setReadOnly(True)
        self.start_time_lineedit_3.setReadOnly(True)
        self.stop_time_lineedit_3.setReadOnly(True)

        self.timer_lineedit_3.setText(self.time_zero)

        device_box_1_3 = QGroupBox()
        device_box_layout_1_3 = QFormLayout(device_box_1_3)
        device_box_layout_1_3.addRow(timer_label_3, self.timer_lineedit_3)
        device_box_layout_1_3.addRow(start_time_label_3, self.start_time_lineedit_3)
        device_box_layout_1_3.addRow(stop_time_label_3, self.stop_time_lineedit_3)

        self.start_timer_button_3 = QPushButton("Start Timer")
        self.stop_timer_button_3 = QPushButton("Stop Timer")
        self.reset_timer_button_3 = QPushButton("Reset Timer")

        self.start_timer_button_3.clicked.connect(self.start_timer_3)
        self.stop_timer_button_3.clicked.connect(self.stop_timer_3)
        self.reset_timer_button_3.clicked.connect(self.reset_timer_3)

        self.stop_timer_button_3.setDisabled(True)
        self.reset_timer_button_3.setDisabled(True)

        device_box_2_3 = QGroupBox()
        device_box_layout_2_3 = QFormLayout(device_box_2_3)
        device_box_layout_2_3.addRow(self.start_timer_button_3)
        device_box_layout_2_3.addRow(self.stop_timer_button_3)
        device_box_layout_2_3.addRow(self.reset_timer_button_3)

        device_groupbox_3 = QGroupBox("Device")
        device_layout_3 = QVBoxLayout(device_groupbox_3)
        device_layout_3.addWidget(device_box_1_3)
        device_layout_3.addStretch()
        device_layout_3.addWidget(device_box_2_3)

        snack_name_label_3 = QLabel("Name:")
        snack_price_label_3 = QLabel("Price:")

        self.snack_name_lineedit_3 = QLineEdit()
        self.snack_price_lineedit_3 = QLineEdit()

        snack_box_1_3 = QGroupBox()
        snack_box_layout_1_3 = QFormLayout(snack_box_1_3)
        snack_box_layout_1_3.addRow(snack_name_label_3, self.snack_name_lineedit_3)
        snack_box_layout_1_3.addRow(snack_price_label_3, self.snack_price_lineedit_3)

        snack_list_label_3 = QLabel("List")
        self.snack_table_3 = QTableWidget()

        self.snack_table_3.setColumnCount(2)
        self.snack_table_3.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_3.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_3.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_3 = QGroupBox()
        snack_box_layout_2_3 = QFormLayout(snack_box_2_3)
        snack_box_layout_2_3.addRow(snack_list_label_3)
        snack_box_layout_2_3.addRow(self.snack_table_3)

        self.snack_add_button_3 = QPushButton("Add Snack")
        self.reset_snack_list_button_3 = QPushButton("Reset list")

        self.snack_add_button_3.clicked.connect(self.add_snack_to_table_3)
        self.reset_snack_list_button_3.clicked.connect(self.reset_snack_list_3)

        self.snack_add_button_3.setDisabled(True)
        self.reset_snack_list_button_3.setDisabled(True)

        snack_box_3_3 = QGroupBox()
        snack_box_layout_3_3 = QFormLayout(snack_box_3_3)
        snack_box_layout_3_3.addRow(self.snack_add_button_3)
        snack_box_layout_3_3.addRow(self.reset_snack_list_button_3)

        snack_groupbox_3 = QGroupBox("Snack")
        snack_layout_3 = QVBoxLayout(snack_groupbox_3)
        snack_layout_3.addWidget(snack_box_1_3)
        snack_layout_3.addStretch()
        snack_layout_3.addWidget(snack_box_2_3)
        snack_layout_3.addStretch()
        snack_layout_3.addWidget(snack_box_3_3)

        device_name_label_3 = QLabel("Device:")
        hourly_rate_label_3 = QLabel("Hourly Rate:")
        snack_invoice_label_3 = QLabel("Snack Invoice:")
        device_invoice_label_3 = QLabel("Device Invoice:")
        total_invoice_label_3 = QLabel("Total Invoice:")
        invoice_time_label_3 = QLabel("Invoice Time:")
        invoice_date_label_3 = QLabel("Invoice Date :")

        self.device_name_lineedit_3 = QLineEdit()
        self.hourly_rate_lineedit_3 = QLineEdit()
        self.snack_invoice_lineedit_3 = QLineEdit()
        self.device_invoice_lineedit_3 = QLineEdit()
        self.total_invoice_lineedit_3 = QLineEdit()
        self.invoice_time_lineedit_3 = QLineEdit()
        self.invoice_date_lineedit_3 = QLineEdit()

        self.snack_invoice_lineedit_3.setReadOnly(True)
        self.device_invoice_lineedit_3.setReadOnly(True)
        self.total_invoice_lineedit_3.setReadOnly(True)
        self.invoice_time_lineedit_3.setReadOnly(True)
        self.invoice_date_lineedit_3.setReadOnly(True)

        self.device_name_lineedit_3.setText("C")
        self.hourly_rate_lineedit_3.setText("50000")

        self.device_name_lineedit_3.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_3.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_3 = QGroupBox()
        invoice_box_layout_1_3 = QFormLayout(invoice_box_1_3)
        invoice_box_layout_1_3.addRow(device_name_label_3, self.device_name_lineedit_3)
        invoice_box_layout_1_3.addRow(hourly_rate_label_3, self.hourly_rate_lineedit_3)
        invoice_box_layout_1_3.addRow(
            device_invoice_label_3, self.device_invoice_lineedit_3
        )
        invoice_box_layout_1_3.addRow(
            snack_invoice_label_3, self.snack_invoice_lineedit_3
        )
        invoice_box_layout_1_3.addRow(
            total_invoice_label_3, self.total_invoice_lineedit_3
        )
        invoice_box_layout_1_3.addRow(
            invoice_time_label_3, self.invoice_time_lineedit_3
        )
        invoice_box_layout_1_3.addRow(
            invoice_date_label_3, self.invoice_date_lineedit_3
        )

        self.calculate_invoice_button_3 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_3 = QPushButton("Pay Invoice")
        self.reset_invoice_button_3 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_3.clicked.connect(self.calculate_invoice_3)
        self.pay_invoice_button_3.clicked.connect(self.pay_invoice_3)
        self.reset_invoice_button_3.clicked.connect(self.reset_invoice_3)

        self.calculate_invoice_button_3.setDisabled(True)
        self.pay_invoice_button_3.setDisabled(True)

        invoice_box_2_3 = QGroupBox()
        invoice_box_layout_2_3 = QFormLayout(invoice_box_2_3)
        invoice_box_layout_2_3.addRow(self.calculate_invoice_button_3)
        invoice_box_layout_2_3.addRow(self.pay_invoice_button_3)
        invoice_box_layout_2_3.addRow(self.reset_invoice_button_3)

        invoice_groupbox_3 = QGroupBox("Invoce")
        invoice_layout_3 = QVBoxLayout(invoice_groupbox_3)
        invoice_layout_3.addWidget(invoice_box_1_3)
        invoice_layout_3.addStretch()
        invoice_layout_3.addWidget(invoice_box_2_3)

        tab_3 = QWidget()
        tab_widget.addTab(tab_3, "System C")

        main_layout_3 = QHBoxLayout()
        main_layout_3.addWidget(device_groupbox_3)
        main_layout_3.addWidget(snack_groupbox_3)
        main_layout_3.addWidget(invoice_groupbox_3)
        tab_3.setLayout(main_layout_3)

        ########################################################################################################################

        self.timer_4 = QTimer()
        self.timer_4.timeout.connect(self.update_timer_4)

        timer_label_4 = QLabel("Timer:")
        start_time_label_4 = QLabel("Start Time:")
        stop_time_label_4 = QLabel("Stop Time:")

        self.timer_lineedit_4 = QLineEdit()
        self.start_time_lineedit_4 = QLineEdit()
        self.stop_time_lineedit_4 = QLineEdit()

        self.timer_lineedit_4.setReadOnly(True)
        self.start_time_lineedit_4.setReadOnly(True)
        self.stop_time_lineedit_4.setReadOnly(True)

        self.timer_lineedit_4.setText(self.time_zero)

        device_box_1_4 = QGroupBox()
        device_box_layout_1_4 = QFormLayout(device_box_1_4)
        device_box_layout_1_4.addRow(timer_label_4, self.timer_lineedit_4)
        device_box_layout_1_4.addRow(start_time_label_4, self.start_time_lineedit_4)
        device_box_layout_1_4.addRow(stop_time_label_4, self.stop_time_lineedit_4)

        self.start_timer_button_4 = QPushButton("Start Timer")
        self.stop_timer_button_4 = QPushButton("Stop Timer")
        self.reset_timer_button_4 = QPushButton("Reset Timer")

        self.start_timer_button_4.clicked.connect(self.start_timer_4)
        self.stop_timer_button_4.clicked.connect(self.stop_timer_4)
        self.reset_timer_button_4.clicked.connect(self.reset_timer_4)

        self.stop_timer_button_4.setDisabled(True)
        self.reset_timer_button_4.setDisabled(True)

        device_box_2_4 = QGroupBox()
        device_box_layout_2_4 = QFormLayout(device_box_2_4)
        device_box_layout_2_4.addRow(self.start_timer_button_4)
        device_box_layout_2_4.addRow(self.stop_timer_button_4)
        device_box_layout_2_4.addRow(self.reset_timer_button_4)

        device_groupbox_4 = QGroupBox("Device")
        device_layout_4 = QVBoxLayout(device_groupbox_4)
        device_layout_4.addWidget(device_box_1_4)
        device_layout_4.addStretch()
        device_layout_4.addWidget(device_box_2_4)

        snack_name_label_4 = QLabel("Name:")
        snack_price_label_4 = QLabel("Price:")

        self.snack_name_lineedit_4 = QLineEdit()
        self.snack_price_lineedit_4 = QLineEdit()

        snack_box_1_4 = QGroupBox()
        snack_box_layout_1_4 = QFormLayout(snack_box_1_4)
        snack_box_layout_1_4.addRow(snack_name_label_4, self.snack_name_lineedit_4)
        snack_box_layout_1_4.addRow(snack_price_label_4, self.snack_price_lineedit_4)

        snack_list_label_4 = QLabel("List")
        self.snack_table_4 = QTableWidget()

        self.snack_table_4.setColumnCount(2)
        self.snack_table_4.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_4.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_4.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_4 = QGroupBox()
        snack_box_layout_2_4 = QFormLayout(snack_box_2_4)
        snack_box_layout_2_4.addRow(snack_list_label_4)
        snack_box_layout_2_4.addRow(self.snack_table_4)

        self.snack_add_button_4 = QPushButton("Add Snack")
        self.reset_snack_list_button_4 = QPushButton("Reset list")

        self.snack_add_button_4.clicked.connect(self.add_snack_to_table_4)
        self.reset_snack_list_button_4.clicked.connect(self.reset_snack_list_4)

        self.snack_add_button_4.setDisabled(True)
        self.reset_snack_list_button_4.setDisabled(True)

        snack_box_3_4 = QGroupBox()
        snack_box_layout_3_4 = QFormLayout(snack_box_3_4)
        snack_box_layout_3_4.addRow(self.snack_add_button_4)
        snack_box_layout_3_4.addRow(self.reset_snack_list_button_4)

        snack_groupbox_4 = QGroupBox("Snack")
        snack_layout_4 = QVBoxLayout(snack_groupbox_4)
        snack_layout_4.addWidget(snack_box_1_4)
        snack_layout_4.addStretch()
        snack_layout_4.addWidget(snack_box_2_4)
        snack_layout_4.addStretch()
        snack_layout_4.addWidget(snack_box_3_4)

        device_name_label_4 = QLabel("Device:")
        hourly_rate_label_4 = QLabel("Hourly Rate:")
        snack_invoice_label_4 = QLabel("Snack Invoice:")
        device_invoice_label_4 = QLabel("Device Invoice:")
        total_invoice_label_4 = QLabel("Total Invoice:")
        invoice_time_label_4 = QLabel("Invoice Time:")
        invoice_date_label_4 = QLabel("Invoice Date :")

        self.device_name_lineedit_4 = QLineEdit()
        self.hourly_rate_lineedit_4 = QLineEdit()
        self.snack_invoice_lineedit_4 = QLineEdit()
        self.device_invoice_lineedit_4 = QLineEdit()
        self.total_invoice_lineedit_4 = QLineEdit()
        self.invoice_time_lineedit_4 = QLineEdit()
        self.invoice_date_lineedit_4 = QLineEdit()

        self.snack_invoice_lineedit_4.setReadOnly(True)
        self.device_invoice_lineedit_4.setReadOnly(True)
        self.total_invoice_lineedit_4.setReadOnly(True)
        self.invoice_time_lineedit_4.setReadOnly(True)
        self.invoice_date_lineedit_4.setReadOnly(True)

        self.device_name_lineedit_4.setText("D")
        self.hourly_rate_lineedit_4.setText("50000")

        self.device_name_lineedit_4.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_4.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_4 = QGroupBox()
        invoice_box_layout_1_4 = QFormLayout(invoice_box_1_4)
        invoice_box_layout_1_4.addRow(device_name_label_4, self.device_name_lineedit_4)
        invoice_box_layout_1_4.addRow(hourly_rate_label_4, self.hourly_rate_lineedit_4)
        invoice_box_layout_1_4.addRow(
            device_invoice_label_4, self.device_invoice_lineedit_4
        )
        invoice_box_layout_1_4.addRow(
            snack_invoice_label_4, self.snack_invoice_lineedit_4
        )
        invoice_box_layout_1_4.addRow(
            total_invoice_label_4, self.total_invoice_lineedit_4
        )
        invoice_box_layout_1_4.addRow(
            invoice_time_label_4, self.invoice_time_lineedit_4
        )
        invoice_box_layout_1_4.addRow(
            invoice_date_label_4, self.invoice_date_lineedit_4
        )

        self.calculate_invoice_button_4 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_4 = QPushButton("Pay Invoice")
        self.reset_invoice_button_4 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_4.clicked.connect(self.calculate_invoice_4)
        self.pay_invoice_button_4.clicked.connect(self.pay_invoice_4)
        self.reset_invoice_button_4.clicked.connect(self.reset_invoice_4)

        self.calculate_invoice_button_4.setDisabled(True)
        self.pay_invoice_button_4.setDisabled(True)

        invoice_box_2_4 = QGroupBox()
        invoice_box_layout_2_4 = QFormLayout(invoice_box_2_4)
        invoice_box_layout_2_4.addRow(self.calculate_invoice_button_4)
        invoice_box_layout_2_4.addRow(self.pay_invoice_button_4)
        invoice_box_layout_2_4.addRow(self.reset_invoice_button_4)

        invoice_groupbox_4 = QGroupBox("Invoce")
        invoice_layout_4 = QVBoxLayout(invoice_groupbox_4)
        invoice_layout_4.addWidget(invoice_box_1_4)
        invoice_layout_4.addStretch()
        invoice_layout_4.addWidget(invoice_box_2_4)

        tab_4 = QWidget()
        tab_widget.addTab(tab_4, "System D")

        main_layout_4 = QHBoxLayout()
        main_layout_4.addWidget(device_groupbox_4)
        main_layout_4.addWidget(snack_groupbox_4)
        main_layout_4.addWidget(invoice_groupbox_4)
        tab_4.setLayout(main_layout_4)

        ########################################################################################################################

        self.timer_5 = QTimer()
        self.timer_5.timeout.connect(self.update_timer_5)

        timer_label_5 = QLabel("Timer:")
        start_time_label_5 = QLabel("Start Time:")
        stop_time_label_5 = QLabel("Stop Time:")

        self.timer_lineedit_5 = QLineEdit()
        self.start_time_lineedit_5 = QLineEdit()
        self.stop_time_lineedit_5 = QLineEdit()

        self.timer_lineedit_5.setReadOnly(True)
        self.start_time_lineedit_5.setReadOnly(True)
        self.stop_time_lineedit_5.setReadOnly(True)

        self.timer_lineedit_5.setText(self.time_zero)

        device_box_1_5 = QGroupBox()
        device_box_layout_1_5 = QFormLayout(device_box_1_5)
        device_box_layout_1_5.addRow(timer_label_5, self.timer_lineedit_5)
        device_box_layout_1_5.addRow(start_time_label_5, self.start_time_lineedit_5)
        device_box_layout_1_5.addRow(stop_time_label_5, self.stop_time_lineedit_5)

        self.start_timer_button_5 = QPushButton("Start Timer")
        self.stop_timer_button_5 = QPushButton("Stop Timer")
        self.reset_timer_button_5 = QPushButton("Reset Timer")

        self.start_timer_button_5.clicked.connect(self.start_timer_5)
        self.stop_timer_button_5.clicked.connect(self.stop_timer_5)
        self.reset_timer_button_5.clicked.connect(self.reset_timer_5)

        self.stop_timer_button_5.setDisabled(True)
        self.reset_timer_button_5.setDisabled(True)

        device_box_2_5 = QGroupBox()
        device_box_layout_2_5 = QFormLayout(device_box_2_5)
        device_box_layout_2_5.addRow(self.start_timer_button_5)
        device_box_layout_2_5.addRow(self.stop_timer_button_5)
        device_box_layout_2_5.addRow(self.reset_timer_button_5)

        device_groupbox_5 = QGroupBox("Device")
        device_layout_5 = QVBoxLayout(device_groupbox_5)
        device_layout_5.addWidget(device_box_1_5)
        device_layout_5.addStretch()
        device_layout_5.addWidget(device_box_2_5)

        snack_name_label_5 = QLabel("Name:")
        snack_price_label_5 = QLabel("Price:")

        self.snack_name_lineedit_5 = QLineEdit()
        self.snack_price_lineedit_5 = QLineEdit()

        snack_box_1_5 = QGroupBox()
        snack_box_layout_1_5 = QFormLayout(snack_box_1_5)
        snack_box_layout_1_5.addRow(snack_name_label_5, self.snack_name_lineedit_5)
        snack_box_layout_1_5.addRow(snack_price_label_5, self.snack_price_lineedit_5)

        snack_list_label_5 = QLabel("List")
        self.snack_table_5 = QTableWidget()

        self.snack_table_5.setColumnCount(2)
        self.snack_table_5.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_5.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_5.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_5 = QGroupBox()
        snack_box_layout_2_5 = QFormLayout(snack_box_2_5)
        snack_box_layout_2_5.addRow(snack_list_label_5)
        snack_box_layout_2_5.addRow(self.snack_table_5)

        self.snack_add_button_5 = QPushButton("Add Snack")
        self.reset_snack_list_button_5 = QPushButton("Reset list")

        self.snack_add_button_5.clicked.connect(self.add_snack_to_table_5)
        self.reset_snack_list_button_5.clicked.connect(self.reset_snack_list_5)

        self.snack_add_button_5.setDisabled(True)
        self.reset_snack_list_button_5.setDisabled(True)

        snack_box_3_5 = QGroupBox()
        snack_box_layout_3_5 = QFormLayout(snack_box_3_5)
        snack_box_layout_3_5.addRow(self.snack_add_button_5)
        snack_box_layout_3_5.addRow(self.reset_snack_list_button_5)

        snack_groupbox_5 = QGroupBox("Snack")
        snack_layout_5 = QVBoxLayout(snack_groupbox_5)
        snack_layout_5.addWidget(snack_box_1_5)
        snack_layout_5.addStretch()
        snack_layout_5.addWidget(snack_box_2_5)
        snack_layout_5.addStretch()
        snack_layout_5.addWidget(snack_box_3_5)

        device_name_label_5 = QLabel("Device:")
        hourly_rate_label_5 = QLabel("Hourly Rate:")
        snack_invoice_label_5 = QLabel("Snack Invoice:")
        device_invoice_label_5 = QLabel("Device Invoice:")
        total_invoice_label_5 = QLabel("Total Invoice:")
        invoice_time_label_5 = QLabel("Invoice Time:")
        invoice_date_label_5 = QLabel("Invoice Date :")

        self.device_name_lineedit_5 = QLineEdit()
        self.hourly_rate_lineedit_5 = QLineEdit()
        self.snack_invoice_lineedit_5 = QLineEdit()
        self.device_invoice_lineedit_5 = QLineEdit()
        self.total_invoice_lineedit_5 = QLineEdit()
        self.invoice_time_lineedit_5 = QLineEdit()
        self.invoice_date_lineedit_5 = QLineEdit()

        self.snack_invoice_lineedit_5.setReadOnly(True)
        self.device_invoice_lineedit_5.setReadOnly(True)
        self.total_invoice_lineedit_5.setReadOnly(True)
        self.invoice_time_lineedit_5.setReadOnly(True)
        self.invoice_date_lineedit_5.setReadOnly(True)

        self.device_name_lineedit_5.setText("E")
        self.hourly_rate_lineedit_5.setText("50000")

        self.device_name_lineedit_5.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_5.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_5 = QGroupBox()
        invoice_box_layout_1_5 = QFormLayout(invoice_box_1_5)
        invoice_box_layout_1_5.addRow(device_name_label_5, self.device_name_lineedit_5)
        invoice_box_layout_1_5.addRow(hourly_rate_label_5, self.hourly_rate_lineedit_5)
        invoice_box_layout_1_5.addRow(
            device_invoice_label_5, self.device_invoice_lineedit_5
        )
        invoice_box_layout_1_5.addRow(
            snack_invoice_label_5, self.snack_invoice_lineedit_5
        )
        invoice_box_layout_1_5.addRow(
            total_invoice_label_5, self.total_invoice_lineedit_5
        )
        invoice_box_layout_1_5.addRow(
            invoice_time_label_5, self.invoice_time_lineedit_5
        )
        invoice_box_layout_1_5.addRow(
            invoice_date_label_5, self.invoice_date_lineedit_5
        )

        self.calculate_invoice_button_5 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_5 = QPushButton("Pay Invoice")
        self.reset_invoice_button_5 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_5.clicked.connect(self.calculate_invoice_5)
        self.pay_invoice_button_5.clicked.connect(self.pay_invoice_5)
        self.reset_invoice_button_5.clicked.connect(self.reset_invoice_5)

        self.calculate_invoice_button_5.setDisabled(True)
        self.pay_invoice_button_5.setDisabled(True)

        invoice_box_2_5 = QGroupBox()
        invoice_box_layout_2_5 = QFormLayout(invoice_box_2_5)
        invoice_box_layout_2_5.addRow(self.calculate_invoice_button_5)
        invoice_box_layout_2_5.addRow(self.pay_invoice_button_5)
        invoice_box_layout_2_5.addRow(self.reset_invoice_button_5)

        invoice_groupbox_5 = QGroupBox("Invoce")
        invoice_layout_5 = QVBoxLayout(invoice_groupbox_5)
        invoice_layout_5.addWidget(invoice_box_1_5)
        invoice_layout_5.addStretch()
        invoice_layout_5.addWidget(invoice_box_2_5)

        tab_5 = QWidget()
        tab_widget.addTab(tab_5, "System E")

        main_layout_5 = QHBoxLayout()
        main_layout_5.addWidget(device_groupbox_5)
        main_layout_5.addWidget(snack_groupbox_5)
        main_layout_5.addWidget(invoice_groupbox_5)
        tab_5.setLayout(main_layout_5)

        ########################################################################################################################

        self.timer_6 = QTimer()
        self.timer_6.timeout.connect(self.update_timer_6)

        timer_label_6 = QLabel("Timer:")
        start_time_label_6 = QLabel("Start Time:")
        stop_time_label_6 = QLabel("Stop Time:")

        self.timer_lineedit_6 = QLineEdit()
        self.start_time_lineedit_6 = QLineEdit()
        self.stop_time_lineedit_6 = QLineEdit()

        self.timer_lineedit_6.setReadOnly(True)
        self.start_time_lineedit_6.setReadOnly(True)
        self.stop_time_lineedit_6.setReadOnly(True)

        self.timer_lineedit_6.setText(self.time_zero)

        device_box_1_6 = QGroupBox()
        device_box_layout_1_6 = QFormLayout(device_box_1_6)
        device_box_layout_1_6.addRow(timer_label_6, self.timer_lineedit_6)
        device_box_layout_1_6.addRow(start_time_label_6, self.start_time_lineedit_6)
        device_box_layout_1_6.addRow(stop_time_label_6, self.stop_time_lineedit_6)

        self.start_timer_button_6 = QPushButton("Start Timer")
        self.stop_timer_button_6 = QPushButton("Stop Timer")
        self.reset_timer_button_6 = QPushButton("Reset Timer")

        self.start_timer_button_6.clicked.connect(self.start_timer_6)
        self.stop_timer_button_6.clicked.connect(self.stop_timer_6)
        self.reset_timer_button_6.clicked.connect(self.reset_timer_6)

        self.stop_timer_button_6.setDisabled(True)
        self.reset_timer_button_6.setDisabled(True)

        device_box_2_6 = QGroupBox()
        device_box_layout_2_6 = QFormLayout(device_box_2_6)
        device_box_layout_2_6.addRow(self.start_timer_button_6)
        device_box_layout_2_6.addRow(self.stop_timer_button_6)
        device_box_layout_2_6.addRow(self.reset_timer_button_6)

        device_groupbox_6 = QGroupBox("Device")
        device_layout_6 = QVBoxLayout(device_groupbox_6)
        device_layout_6.addWidget(device_box_1_6)
        device_layout_6.addStretch()
        device_layout_6.addWidget(device_box_2_6)

        snack_name_label_6 = QLabel("Name:")
        snack_price_label_6 = QLabel("Price:")

        self.snack_name_lineedit_6 = QLineEdit()
        self.snack_price_lineedit_6 = QLineEdit()

        snack_box_1_6 = QGroupBox()
        snack_box_layout_1_6 = QFormLayout(snack_box_1_6)
        snack_box_layout_1_6.addRow(snack_name_label_6, self.snack_name_lineedit_6)
        snack_box_layout_1_6.addRow(snack_price_label_6, self.snack_price_lineedit_6)

        snack_list_label_6 = QLabel("List")
        self.snack_table_6 = QTableWidget()

        self.snack_table_6.setColumnCount(2)
        self.snack_table_6.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_6.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_6.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_6 = QGroupBox()
        snack_box_layout_2_6 = QFormLayout(snack_box_2_6)
        snack_box_layout_2_6.addRow(snack_list_label_6)
        snack_box_layout_2_6.addRow(self.snack_table_6)

        self.snack_add_button_6 = QPushButton("Add Snack")
        self.reset_snack_list_button_6 = QPushButton("Reset list")

        self.snack_add_button_6.clicked.connect(self.add_snack_to_table_6)
        self.reset_snack_list_button_6.clicked.connect(self.reset_snack_list_6)

        self.snack_add_button_6.setDisabled(True)
        self.reset_snack_list_button_6.setDisabled(True)

        snack_box_3_6 = QGroupBox()
        snack_box_layout_3_6 = QFormLayout(snack_box_3_6)
        snack_box_layout_3_6.addRow(self.snack_add_button_6)
        snack_box_layout_3_6.addRow(self.reset_snack_list_button_6)

        snack_groupbox_6 = QGroupBox("Snack")
        snack_layout_6 = QVBoxLayout(snack_groupbox_6)
        snack_layout_6.addWidget(snack_box_1_6)
        snack_layout_6.addStretch()
        snack_layout_6.addWidget(snack_box_2_6)
        snack_layout_6.addStretch()
        snack_layout_6.addWidget(snack_box_3_6)

        device_name_label_6 = QLabel("Device:")
        hourly_rate_label_6 = QLabel("Hourly Rate:")
        snack_invoice_label_6 = QLabel("Snack Invoice:")
        device_invoice_label_6 = QLabel("Device Invoice:")
        total_invoice_label_6 = QLabel("Total Invoice:")
        invoice_time_label_6 = QLabel("Invoice Time:")
        invoice_date_label_6 = QLabel("Invoice Date :")

        self.device_name_lineedit_6 = QLineEdit()
        self.hourly_rate_lineedit_6 = QLineEdit()
        self.snack_invoice_lineedit_6 = QLineEdit()
        self.device_invoice_lineedit_6 = QLineEdit()
        self.total_invoice_lineedit_6 = QLineEdit()
        self.invoice_time_lineedit_6 = QLineEdit()
        self.invoice_date_lineedit_6 = QLineEdit()

        self.snack_invoice_lineedit_6.setReadOnly(True)
        self.device_invoice_lineedit_6.setReadOnly(True)
        self.total_invoice_lineedit_6.setReadOnly(True)
        self.invoice_time_lineedit_6.setReadOnly(True)
        self.invoice_date_lineedit_6.setReadOnly(True)

        self.device_name_lineedit_6.setText("F")
        self.hourly_rate_lineedit_6.setText("50000")

        self.device_name_lineedit_6.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_6.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_6 = QGroupBox()
        invoice_box_layout_1_6 = QFormLayout(invoice_box_1_6)
        invoice_box_layout_1_6.addRow(device_name_label_6, self.device_name_lineedit_6)
        invoice_box_layout_1_6.addRow(hourly_rate_label_6, self.hourly_rate_lineedit_6)
        invoice_box_layout_1_6.addRow(
            device_invoice_label_6, self.device_invoice_lineedit_6
        )
        invoice_box_layout_1_6.addRow(
            snack_invoice_label_6, self.snack_invoice_lineedit_6
        )
        invoice_box_layout_1_6.addRow(
            total_invoice_label_6, self.total_invoice_lineedit_6
        )
        invoice_box_layout_1_6.addRow(
            invoice_time_label_6, self.invoice_time_lineedit_6
        )
        invoice_box_layout_1_6.addRow(
            invoice_date_label_6, self.invoice_date_lineedit_6
        )

        self.calculate_invoice_button_6 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_6 = QPushButton("Pay Invoice")
        self.reset_invoice_button_6 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_6.clicked.connect(self.calculate_invoice_6)
        self.pay_invoice_button_6.clicked.connect(self.pay_invoice_6)
        self.reset_invoice_button_6.clicked.connect(self.reset_invoice_6)

        self.calculate_invoice_button_6.setDisabled(True)
        self.pay_invoice_button_6.setDisabled(True)

        invoice_box_2_6 = QGroupBox()
        invoice_box_layout_2_6 = QFormLayout(invoice_box_2_6)
        invoice_box_layout_2_6.addRow(self.calculate_invoice_button_6)
        invoice_box_layout_2_6.addRow(self.pay_invoice_button_6)
        invoice_box_layout_2_6.addRow(self.reset_invoice_button_6)

        invoice_groupbox_6 = QGroupBox("Invoce")
        invoice_layout_6 = QVBoxLayout(invoice_groupbox_6)
        invoice_layout_6.addWidget(invoice_box_1_6)
        invoice_layout_6.addStretch()
        invoice_layout_6.addWidget(invoice_box_2_6)

        tab_6 = QWidget()
        tab_widget.addTab(tab_6, "System F")

        main_layout_6 = QHBoxLayout()
        main_layout_6.addWidget(device_groupbox_6)
        main_layout_6.addWidget(snack_groupbox_6)
        main_layout_6.addWidget(invoice_groupbox_6)
        tab_6.setLayout(main_layout_6)

        ########################################################################################################################

        self.timer_7 = QTimer()
        self.timer_7.timeout.connect(self.update_timer_7)

        timer_label_7 = QLabel("Timer:")
        start_time_label_7 = QLabel("Start Time:")
        stop_time_label_7 = QLabel("Stop Time:")

        self.timer_lineedit_7 = QLineEdit()
        self.start_time_lineedit_7 = QLineEdit()
        self.stop_time_lineedit_7 = QLineEdit()

        self.timer_lineedit_7.setReadOnly(True)
        self.start_time_lineedit_7.setReadOnly(True)
        self.stop_time_lineedit_7.setReadOnly(True)

        self.timer_lineedit_7.setText(self.time_zero)

        device_box_1_7 = QGroupBox()
        device_box_layout_1_7 = QFormLayout(device_box_1_7)
        device_box_layout_1_7.addRow(timer_label_7, self.timer_lineedit_7)
        device_box_layout_1_7.addRow(start_time_label_7, self.start_time_lineedit_7)
        device_box_layout_1_7.addRow(stop_time_label_7, self.stop_time_lineedit_7)

        self.start_timer_button_7 = QPushButton("Start Timer")
        self.stop_timer_button_7 = QPushButton("Stop Timer")
        self.reset_timer_button_7 = QPushButton("Reset Timer")

        self.start_timer_button_7.clicked.connect(self.start_timer_7)
        self.stop_timer_button_7.clicked.connect(self.stop_timer_7)
        self.reset_timer_button_7.clicked.connect(self.reset_timer_7)

        self.stop_timer_button_7.setDisabled(True)
        self.reset_timer_button_7.setDisabled(True)

        device_box_2_7 = QGroupBox()
        device_box_layout_2_7 = QFormLayout(device_box_2_7)
        device_box_layout_2_7.addRow(self.start_timer_button_7)
        device_box_layout_2_7.addRow(self.stop_timer_button_7)
        device_box_layout_2_7.addRow(self.reset_timer_button_7)

        device_groupbox_7 = QGroupBox("Device")
        device_layout_7 = QVBoxLayout(device_groupbox_7)
        device_layout_7.addWidget(device_box_1_7)
        device_layout_7.addStretch()
        device_layout_7.addWidget(device_box_2_7)

        snack_name_label_7 = QLabel("Name:")
        snack_price_label_7 = QLabel("Price:")

        self.snack_name_lineedit_7 = QLineEdit()
        self.snack_price_lineedit_7 = QLineEdit()

        snack_box_1_7 = QGroupBox()
        snack_box_layout_1_7 = QFormLayout(snack_box_1_7)
        snack_box_layout_1_7.addRow(snack_name_label_7, self.snack_name_lineedit_7)
        snack_box_layout_1_7.addRow(snack_price_label_7, self.snack_price_lineedit_7)

        snack_list_label_7 = QLabel("List")
        self.snack_table_7 = QTableWidget()

        self.snack_table_7.setColumnCount(2)
        self.snack_table_7.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_7.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_7.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_7 = QGroupBox()
        snack_box_layout_2_7 = QFormLayout(snack_box_2_7)
        snack_box_layout_2_7.addRow(snack_list_label_7)
        snack_box_layout_2_7.addRow(self.snack_table_7)

        self.snack_add_button_7 = QPushButton("Add Snack")
        self.reset_snack_list_button_7 = QPushButton("Reset list")

        self.snack_add_button_7.clicked.connect(self.add_snack_to_table_7)
        self.reset_snack_list_button_7.clicked.connect(self.reset_snack_list_7)

        self.snack_add_button_7.setDisabled(True)
        self.reset_snack_list_button_7.setDisabled(True)

        snack_box_3_7 = QGroupBox()
        snack_box_layout_3_7 = QFormLayout(snack_box_3_7)
        snack_box_layout_3_7.addRow(self.snack_add_button_7)
        snack_box_layout_3_7.addRow(self.reset_snack_list_button_7)

        snack_groupbox_7 = QGroupBox("Snack")
        snack_layout_7 = QVBoxLayout(snack_groupbox_7)
        snack_layout_7.addWidget(snack_box_1_7)
        snack_layout_7.addStretch()
        snack_layout_7.addWidget(snack_box_2_7)
        snack_layout_7.addStretch()
        snack_layout_7.addWidget(snack_box_3_7)

        device_name_label_7 = QLabel("Device:")
        hourly_rate_label_7 = QLabel("Hourly Rate:")
        snack_invoice_label_7 = QLabel("Snack Invoice:")
        device_invoice_label_7 = QLabel("Device Invoice:")
        total_invoice_label_7 = QLabel("Total Invoice:")
        invoice_time_label_7 = QLabel("Invoice Time:")
        invoice_date_label_7 = QLabel("Invoice Date :")

        self.device_name_lineedit_7 = QLineEdit()
        self.hourly_rate_lineedit_7 = QLineEdit()
        self.snack_invoice_lineedit_7 = QLineEdit()
        self.device_invoice_lineedit_7 = QLineEdit()
        self.total_invoice_lineedit_7 = QLineEdit()
        self.invoice_time_lineedit_7 = QLineEdit()
        self.invoice_date_lineedit_7 = QLineEdit()

        self.snack_invoice_lineedit_7.setReadOnly(True)
        self.device_invoice_lineedit_7.setReadOnly(True)
        self.total_invoice_lineedit_7.setReadOnly(True)
        self.invoice_time_lineedit_7.setReadOnly(True)
        self.invoice_date_lineedit_7.setReadOnly(True)

        self.device_name_lineedit_7.setText("G")
        self.hourly_rate_lineedit_7.setText("50000")

        self.device_name_lineedit_7.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_7.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_7 = QGroupBox()
        invoice_box_layout_1_7 = QFormLayout(invoice_box_1_7)
        invoice_box_layout_1_7.addRow(device_name_label_7, self.device_name_lineedit_7)
        invoice_box_layout_1_7.addRow(hourly_rate_label_7, self.hourly_rate_lineedit_7)
        invoice_box_layout_1_7.addRow(
            device_invoice_label_7, self.device_invoice_lineedit_7
        )
        invoice_box_layout_1_7.addRow(
            snack_invoice_label_7, self.snack_invoice_lineedit_7
        )
        invoice_box_layout_1_7.addRow(
            total_invoice_label_7, self.total_invoice_lineedit_7
        )
        invoice_box_layout_1_7.addRow(
            invoice_time_label_7, self.invoice_time_lineedit_7
        )
        invoice_box_layout_1_7.addRow(
            invoice_date_label_7, self.invoice_date_lineedit_7
        )

        self.calculate_invoice_button_7 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_7 = QPushButton("Pay Invoice")
        self.reset_invoice_button_7 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_7.clicked.connect(self.calculate_invoice_7)
        self.pay_invoice_button_7.clicked.connect(self.pay_invoice_7)
        self.reset_invoice_button_7.clicked.connect(self.reset_invoice_7)

        self.calculate_invoice_button_7.setDisabled(True)
        self.pay_invoice_button_7.setDisabled(True)

        invoice_box_2_7 = QGroupBox()
        invoice_box_layout_2_7 = QFormLayout(invoice_box_2_7)
        invoice_box_layout_2_7.addRow(self.calculate_invoice_button_7)
        invoice_box_layout_2_7.addRow(self.pay_invoice_button_7)
        invoice_box_layout_2_7.addRow(self.reset_invoice_button_7)

        invoice_groupbox_7 = QGroupBox("Invoce")
        invoice_layout_7 = QVBoxLayout(invoice_groupbox_7)
        invoice_layout_7.addWidget(invoice_box_1_7)
        invoice_layout_7.addStretch()
        invoice_layout_7.addWidget(invoice_box_2_7)

        tab_7 = QWidget()
        tab_widget.addTab(tab_7, "System G")

        main_layout_7 = QHBoxLayout()
        main_layout_7.addWidget(device_groupbox_7)
        main_layout_7.addWidget(snack_groupbox_7)
        main_layout_7.addWidget(invoice_groupbox_7)
        tab_7.setLayout(main_layout_7)

        ########################################################################################################################

        self.timer_8 = QTimer()
        self.timer_8.timeout.connect(self.update_timer_8)

        timer_label_8 = QLabel("Timer:")
        start_time_label_8 = QLabel("Start Time:")
        stop_time_label_8 = QLabel("Stop Time:")

        self.timer_lineedit_8 = QLineEdit()
        self.start_time_lineedit_8 = QLineEdit()
        self.stop_time_lineedit_8 = QLineEdit()

        self.timer_lineedit_8.setReadOnly(True)
        self.start_time_lineedit_8.setReadOnly(True)
        self.stop_time_lineedit_8.setReadOnly(True)

        self.timer_lineedit_8.setText(self.time_zero)

        device_box_1_8 = QGroupBox()
        device_box_layout_1_8 = QFormLayout(device_box_1_8)
        device_box_layout_1_8.addRow(timer_label_8, self.timer_lineedit_8)
        device_box_layout_1_8.addRow(start_time_label_8, self.start_time_lineedit_8)
        device_box_layout_1_8.addRow(stop_time_label_8, self.stop_time_lineedit_8)

        self.start_timer_button_8 = QPushButton("Start Timer")
        self.stop_timer_button_8 = QPushButton("Stop Timer")
        self.reset_timer_button_8 = QPushButton("Reset Timer")

        self.start_timer_button_8.clicked.connect(self.start_timer_8)
        self.stop_timer_button_8.clicked.connect(self.stop_timer_8)
        self.reset_timer_button_8.clicked.connect(self.reset_timer_8)

        self.stop_timer_button_8.setDisabled(True)
        self.reset_timer_button_8.setDisabled(True)

        device_box_2_8 = QGroupBox()
        device_box_layout_2_8 = QFormLayout(device_box_2_8)
        device_box_layout_2_8.addRow(self.start_timer_button_8)
        device_box_layout_2_8.addRow(self.stop_timer_button_8)
        device_box_layout_2_8.addRow(self.reset_timer_button_8)

        device_groupbox_8 = QGroupBox("Device")
        device_layout_8 = QVBoxLayout(device_groupbox_8)
        device_layout_8.addWidget(device_box_1_8)
        device_layout_8.addStretch()
        device_layout_8.addWidget(device_box_2_8)

        snack_name_label_8 = QLabel("Name:")
        snack_price_label_8 = QLabel("Price:")

        self.snack_name_lineedit_8 = QLineEdit()
        self.snack_price_lineedit_8 = QLineEdit()

        snack_box_1_8 = QGroupBox()
        snack_box_layout_1_8 = QFormLayout(snack_box_1_8)
        snack_box_layout_1_8.addRow(snack_name_label_8, self.snack_name_lineedit_8)
        snack_box_layout_1_8.addRow(snack_price_label_8, self.snack_price_lineedit_8)

        snack_list_label_8 = QLabel("List")
        self.snack_table_8 = QTableWidget()

        self.snack_table_8.setColumnCount(2)
        self.snack_table_8.setHorizontalHeaderLabels(["Name", "Price"])
        self.snack_table_8.setStyleSheet("QTableWidget {alignment: center;}")
        self.snack_table_8.setEditTriggers(QAbstractItemView.NoEditTriggers)

        snack_box_2_8 = QGroupBox()
        snack_box_layout_2_8 = QFormLayout(snack_box_2_8)
        snack_box_layout_2_8.addRow(snack_list_label_8)
        snack_box_layout_2_8.addRow(self.snack_table_8)

        self.snack_add_button_8 = QPushButton("Add Snack")
        self.reset_snack_list_button_8 = QPushButton("Reset list")

        self.snack_add_button_8.clicked.connect(self.add_snack_to_table_8)
        self.reset_snack_list_button_8.clicked.connect(self.reset_snack_list_8)

        self.snack_add_button_8.setDisabled(True)
        self.reset_snack_list_button_8.setDisabled(True)

        snack_box_3_8 = QGroupBox()
        snack_box_layout_3_8 = QFormLayout(snack_box_3_8)
        snack_box_layout_3_8.addRow(self.snack_add_button_8)
        snack_box_layout_3_8.addRow(self.reset_snack_list_button_8)

        snack_groupbox_8 = QGroupBox("Snack")
        snack_layout_8 = QVBoxLayout(snack_groupbox_8)
        snack_layout_8.addWidget(snack_box_1_8)
        snack_layout_8.addStretch()
        snack_layout_8.addWidget(snack_box_2_8)
        snack_layout_8.addStretch()
        snack_layout_8.addWidget(snack_box_3_8)

        device_name_label_8 = QLabel("Device:")
        hourly_rate_label_8 = QLabel("Hourly Rate:")
        snack_invoice_label_8 = QLabel("Snack Invoice:")
        device_invoice_label_8 = QLabel("Device Invoice:")
        total_invoice_label_8 = QLabel("Total Invoice:")
        invoice_time_label_8 = QLabel("Invoice Time:")
        invoice_date_label_8 = QLabel("Invoice Date :")

        self.device_name_lineedit_8 = QLineEdit()
        self.hourly_rate_lineedit_8 = QLineEdit()
        self.snack_invoice_lineedit_8 = QLineEdit()
        self.device_invoice_lineedit_8 = QLineEdit()
        self.total_invoice_lineedit_8 = QLineEdit()
        self.invoice_time_lineedit_8 = QLineEdit()
        self.invoice_date_lineedit_8 = QLineEdit()

        self.snack_invoice_lineedit_8.setReadOnly(True)
        self.device_invoice_lineedit_8.setReadOnly(True)
        self.total_invoice_lineedit_8.setReadOnly(True)
        self.invoice_time_lineedit_8.setReadOnly(True)
        self.invoice_date_lineedit_8.setReadOnly(True)

        self.device_name_lineedit_8.setText("H")
        self.hourly_rate_lineedit_8.setText("50000")

        self.device_name_lineedit_8.setPlaceholderText("Enter Device Name")
        self.hourly_rate_lineedit_8.setPlaceholderText("Enter Hourly Rate")

        invoice_box_1_8 = QGroupBox()
        invoice_box_layout_1_8 = QFormLayout(invoice_box_1_8)
        invoice_box_layout_1_8.addRow(device_name_label_8, self.device_name_lineedit_8)
        invoice_box_layout_1_8.addRow(hourly_rate_label_8, self.hourly_rate_lineedit_8)
        invoice_box_layout_1_8.addRow(
            device_invoice_label_8, self.device_invoice_lineedit_8
        )
        invoice_box_layout_1_8.addRow(
            snack_invoice_label_8, self.snack_invoice_lineedit_8
        )
        invoice_box_layout_1_8.addRow(
            total_invoice_label_8, self.total_invoice_lineedit_8
        )
        invoice_box_layout_1_8.addRow(
            invoice_time_label_8, self.invoice_time_lineedit_8
        )
        invoice_box_layout_1_8.addRow(
            invoice_date_label_8, self.invoice_date_lineedit_8
        )

        self.calculate_invoice_button_8 = QPushButton("Calculate Invoice")
        self.pay_invoice_button_8 = QPushButton("Pay Invoice")
        self.reset_invoice_button_8 = QPushButton("Reset Invoice")

        self.calculate_invoice_button_8.clicked.connect(self.calculate_invoice_8)
        self.pay_invoice_button_8.clicked.connect(self.pay_invoice_8)
        self.reset_invoice_button_8.clicked.connect(self.reset_invoice_8)

        self.calculate_invoice_button_8.setDisabled(True)
        self.pay_invoice_button_8.setDisabled(True)

        invoice_box_2_8 = QGroupBox()
        invoice_box_layout_2_8 = QFormLayout(invoice_box_2_8)
        invoice_box_layout_2_8.addRow(self.calculate_invoice_button_8)
        invoice_box_layout_2_8.addRow(self.pay_invoice_button_8)
        invoice_box_layout_2_8.addRow(self.reset_invoice_button_8)

        invoice_groupbox_8 = QGroupBox("Invoce")
        invoice_layout_8 = QVBoxLayout(invoice_groupbox_8)
        invoice_layout_8.addWidget(invoice_box_1_8)
        invoice_layout_8.addStretch()
        invoice_layout_8.addWidget(invoice_box_2_8)

        tab_8 = QWidget()
        tab_widget.addTab(tab_8, "System H")

        main_layout_8 = QHBoxLayout()
        main_layout_8.addWidget(device_groupbox_8)
        main_layout_8.addWidget(snack_groupbox_8)
        main_layout_8.addWidget(invoice_groupbox_8)
        tab_8.setLayout(main_layout_8)

        ########################################################################################################################

        device_invoice_label_separate = QLabel("Invoice:")

        self.device_invoice_lineedit_separate = QLineEdit()

        device_invoice_box_1_separate = QGroupBox()
        device_invoice_box_layout_1_separate = QFormLayout(
            device_invoice_box_1_separate
        )
        device_invoice_box_layout_1_separate.addRow(
            device_invoice_label_separate, self.device_invoice_lineedit_separate
        )

        device_invoice_pay_separate = QPushButton("Pay")

        device_invoice_pay_separate.clicked.connect(self.separate_device_invoice_pay)

        device_invoice_box_2_separate = QGroupBox()
        device_invoice_box_layout_2_separate = QFormLayout(
            device_invoice_box_2_separate
        )
        device_invoice_box_layout_2_separate.addRow(device_invoice_pay_separate)

        device_groupbox_separate = QGroupBox("Device")
        device_layout_separate = QVBoxLayout(device_groupbox_separate)
        device_layout_separate.addWidget(device_invoice_box_1_separate)
        device_layout_separate.addStretch()
        device_layout_separate.addWidget(device_invoice_box_2_separate)

        snack_invoice_label_separate = QLabel("Invoice:")

        self.snack_invoice_lineedit_separate = QLineEdit()

        snack_invoice_box_1_separate = QGroupBox()
        snack_invoice_box_layout_1_separate = QFormLayout(snack_invoice_box_1_separate)
        snack_invoice_box_layout_1_separate.addRow(
            snack_invoice_label_separate, self.snack_invoice_lineedit_separate
        )

        snack_invoice_pay_separate = QPushButton("Pay")

        snack_invoice_pay_separate.clicked.connect(self.separate_snack_invoice_pay)

        snack_invoice_box_2_separate = QGroupBox()
        snack_invoice_box_layout_2_separate = QFormLayout(snack_invoice_box_2_separate)
        snack_invoice_box_layout_2_separate.addRow(snack_invoice_pay_separate)

        snack_groupbox_separate = QGroupBox("snack")
        snack_layout_separate = QVBoxLayout(snack_groupbox_separate)
        snack_layout_separate.addWidget(snack_invoice_box_1_separate)
        snack_layout_separate.addStretch()
        snack_layout_separate.addWidget(snack_invoice_box_2_separate)

        tab_separate = QWidget()
        tab_widget.addTab(tab_separate, "Separate Invoice")

        main_layout_separate = QHBoxLayout()
        main_layout_separate.addWidget(device_groupbox_separate)
        main_layout_separate.addWidget(snack_groupbox_separate)
        tab_separate.setLayout(main_layout_separate)

    ########################################################################################################################

    def about(self):
        about_text = f"""PLAY NET.
        \nVersion: {self.app_version}
        \nDeveloper: Sparky
        \nCompany: SPARKS"""
        QMessageBox.about(self, "About", about_text)

    def contact(self):
        contact_text = f"""PLAY NET.
        \nContact: Sparky#2273 on Discord or Sparky2273 on Telegram"""
        QMessageBox.about(self, "Contact", contact_text)

    def manual(self):
        self.manual_window = PlayNetWindowManual()
        if self.manual_window.isHidden():
            self.manual_window.show()

    def invoice(self):
        self.invoice_window = InvoiceWindow()
        if self.invoice_window.isHidden():
            self.invoice_window.show()

    def daily_invoice(self):
        self.daily_invoice_window = DailyInvoiceWindow()
        if self.daily_invoice_window.isHidden():
            self.daily_invoice_window.show()

    def debtor_list(self):
        self.debtor_list_window = DebtorListWindow()
        if self.debtor_list_window.isHidden():
            self.debtor_list_window.show()

    def payment_method(self):
        self.payment_method_window = PaymentMethodWindow()
        if self.payment_method_window.isHidden():
            self.payment_method_window.show()

    def closeEvent(self, event):
        program_status = ProgramStatus()
        program_status.stop_program()
        sys.exit(1)

    ########################################################################################################################

    def start_timer_1(self):
        if not self.hourly_rate_lineedit_1.text() == "":
            self.start_timer_button_1.setDisabled(True)
            self.stop_timer_button_1.setEnabled(True)
            self.reset_timer_button_1.setEnabled(True)

            self.start_time_lineedit_1.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_1.start(1000)

            self.snack_add_button_1.setEnabled(True)
            self.reset_snack_list_button_1.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_1(self):
        self.stop_timer_button_1.setDisabled(True)
        self.timer_1.stop()

        self.stop_time_lineedit_1.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_1.setEnabled(True)

    def update_timer_1(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_1.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_1.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_1.text())

        work_done = int(elapsed_time / 3600 * rate)

        self.device_invoice_lineedit_1.setText(str(work_done))

    def reset_timer_1(self):
        self.start_timer_button_1.setEnabled(True)
        self.stop_timer_button_1.setDisabled(True)
        self.reset_timer_button_1.setDisabled(True)

        self.calculate_invoice_button_1.setDisabled(True)

        self.timer_1.stop()

        self.timer_lineedit_1.setText(self.time_zero)
        self.start_time_lineedit_1.clear()
        self.stop_time_lineedit_1.clear()
        self.device_invoice_lineedit_1.clear()

    def add_snack_to_table_1(self):
        if not self.snack_price_lineedit_1.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_1.text())
            price = QTableWidgetItem(self.snack_price_lineedit_1.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_1.rowCount()
            self.snack_table_1.insertRow(row_count)
            self.snack_table_1.setItem(row_count, 0, name)
            self.snack_table_1.setItem(row_count, 1, price)

            self.snack_name_lineedit_1.clear()
            self.snack_price_lineedit_1.clear()

            total = 0
            for row in range(self.snack_table_1.rowCount()):
                price = int(self.snack_table_1.item(row, 1).text())
                total += price

            self.snack_invoice_1 = total

            self.snack_invoice_lineedit_1.setText(str(self.snack_invoice_1))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_1(self):
        self.snack_table_1.clearContents()
        self.snack_table_1.setRowCount(0)
        self.snack_invoice_lineedit_1.clear()
        self.snack_name_lineedit_1.clear()
        self.snack_price_lineedit_1.clear()

    def calculate_invoice_1(self):
        if self.device_invoice_lineedit_1.text() == "":
            self.device_invoice_lineedit_1.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_1.text()

        if self.snack_invoice_lineedit_1.text() == "":
            self.snack_invoice_lineedit_1.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_1.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_1.setText(str(total_invoice))

        self.invoice_time_lineedit_1.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_1.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_1.setEnabled(True)
        self.calculate_invoice_button_1.setDisabled(True)

        self.snack_add_button_1.setDisabled(True)
        self.reset_snack_list_button_1.setDisabled(True)

        self.reset_timer_button_1.setDisabled(True)

    def pay_invoice_1(self):
        self.pay_invoice_button_1.setDisabled(True)
        self.calculate_invoice_button_1.setDisabled(True)

        device_name = self.device_name_lineedit_1.text()
        hourly_rate = self.hourly_rate_lineedit_1.text()
        snack_invoice = self.snack_invoice_lineedit_1.text()
        device_invoice = self.device_invoice_lineedit_1.text()
        total_invoice = self.total_invoice_lineedit_1.text()
        invoice_time = self.invoice_time_lineedit_1.text()
        invoice_date = self.invoice_date_lineedit_1.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_1(self):
        self.calculate_invoice_button_1.setEnabled(True)

        self.device_invoice_lineedit_1.clear()
        self.snack_invoice_lineedit_1.clear()
        self.total_invoice_lineedit_1.clear()
        self.invoice_time_lineedit_1.clear()
        self.invoice_date_lineedit_1.clear()

        self.reset_timer_1()
        self.reset_snack_list_1()

    ########################################################################################################################

    def start_timer_2(self):
        if not self.hourly_rate_lineedit_2.text() == "":
            self.start_timer_button_2.setDisabled(True)
            self.stop_timer_button_2.setEnabled(True)
            self.reset_timer_button_2.setEnabled(True)

            self.start_time_lineedit_2.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_2.start(1000)

            self.snack_add_button_2.setEnabled(True)
            self.reset_snack_list_button_2.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_2(self):
        self.stop_timer_button_2.setDisabled(True)
        self.timer_2.stop()

        self.stop_time_lineedit_2.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_2.setEnabled(True)

    def update_timer_2(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_2.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_2.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_2.text())

        work_done = int(elapsed_time / 3600 * rate)

        self.device_invoice_lineedit_2.setText(str(work_done))

    def reset_timer_2(self):
        self.start_timer_button_2.setEnabled(True)
        self.stop_timer_button_2.setDisabled(True)
        self.reset_timer_button_2.setDisabled(True)

        self.calculate_invoice_button_2.setDisabled(True)

        self.timer_2.stop()

        self.timer_lineedit_2.setText(self.time_zero)
        self.start_time_lineedit_2.clear()
        self.stop_time_lineedit_2.clear()
        self.device_invoice_lineedit_2.clear()

    def add_snack_to_table_2(self):
        if not self.snack_price_lineedit_2.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_2.text())
            price = QTableWidgetItem(self.snack_price_lineedit_2.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_2.rowCount()
            self.snack_table_2.insertRow(row_count)
            self.snack_table_2.setItem(row_count, 0, name)
            self.snack_table_2.setItem(row_count, 1, price)

            self.snack_name_lineedit_2.clear()
            self.snack_price_lineedit_2.clear()

            total = 0
            for row in range(self.snack_table_2.rowCount()):
                price = int(self.snack_table_2.item(row, 1).text())
                total += price

            self.snack_invoice_2 = total

            self.snack_invoice_lineedit_2.setText(str(self.snack_invoice_2))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_2(self):
        self.snack_table_2.clearContents()
        self.snack_table_2.setRowCount(0)
        self.snack_invoice_lineedit_2.clear()
        self.snack_name_lineedit_2.clear()
        self.snack_price_lineedit_2.clear()

    def calculate_invoice_2(self):
        if self.device_invoice_lineedit_2.text() == "":
            self.device_invoice_lineedit_2.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_2.text()

        if self.snack_invoice_lineedit_2.text() == "":
            self.snack_invoice_lineedit_2.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_2.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_2.setText(str(total_invoice))

        self.invoice_time_lineedit_2.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_2.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_2.setEnabled(True)
        self.calculate_invoice_button_2.setDisabled(True)

        self.snack_add_button_2.setDisabled(True)
        self.reset_snack_list_button_2.setDisabled(True)

        self.reset_timer_button_2.setDisabled(True)

    def pay_invoice_2(self):
        self.pay_invoice_button_2.setDisabled(True)
        self.calculate_invoice_button_2.setDisabled(True)

        device_name = self.device_name_lineedit_2.text()
        hourly_rate = self.hourly_rate_lineedit_2.text()
        snack_invoice = self.snack_invoice_lineedit_2.text()
        device_invoice = self.device_invoice_lineedit_2.text()
        total_invoice = self.total_invoice_lineedit_2.text()
        invoice_time = self.invoice_time_lineedit_2.text()
        invoice_date = self.invoice_date_lineedit_2.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_2(self):
        self.calculate_invoice_button_2.setEnabled(True)

        self.device_invoice_lineedit_2.clear()
        self.snack_invoice_lineedit_2.clear()
        self.total_invoice_lineedit_2.clear()
        self.invoice_time_lineedit_2.clear()
        self.invoice_date_lineedit_2.clear()

        self.reset_timer_2()
        self.reset_snack_list_2()

    ########################################################################################################################

    def start_timer_3(self):
        if not self.hourly_rate_lineedit_3.text() == "":
            self.start_timer_button_3.setDisabled(True)
            self.stop_timer_button_3.setEnabled(True)
            self.reset_timer_button_3.setEnabled(True)

            self.start_time_lineedit_3.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_3.start(1000)

            self.snack_add_button_3.setEnabled(True)
            self.reset_snack_list_button_3.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_3(self):
        self.stop_timer_button_3.setDisabled(True)
        self.timer_3.stop()

        self.stop_time_lineedit_3.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_3.setEnabled(True)

    def update_timer_3(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_3.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_3.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_3.text())

        work_done = int(elapsed_time / 3600 * rate)

        self.device_invoice_lineedit_3.setText(str(work_done))

    def reset_timer_3(self):
        self.start_timer_button_3.setEnabled(True)
        self.stop_timer_button_3.setDisabled(True)
        self.reset_timer_button_3.setDisabled(True)

        self.calculate_invoice_button_3.setDisabled(True)

        self.timer_3.stop()

        self.timer_lineedit_3.setText(self.time_zero)
        self.start_time_lineedit_3.clear()
        self.stop_time_lineedit_3.clear()
        self.device_invoice_lineedit_3.clear()

    def add_snack_to_table_3(self):
        if not self.snack_price_lineedit_3.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_3.text())
            price = QTableWidgetItem(self.snack_price_lineedit_3.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_3.rowCount()
            self.snack_table_3.insertRow(row_count)
            self.snack_table_3.setItem(row_count, 0, name)
            self.snack_table_3.setItem(row_count, 1, price)

            self.snack_name_lineedit_3.clear()
            self.snack_price_lineedit_3.clear()

            total = 0
            for row in range(self.snack_table_3.rowCount()):
                price = int(self.snack_table_3.item(row, 1).text())
                total += price

            self.snack_invoice_3 = total

            self.snack_invoice_lineedit_3.setText(str(self.snack_invoice_3))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_3(self):
        self.snack_table_3.clearContents()
        self.snack_table_3.setRowCount(0)
        self.snack_invoice_lineedit_3.clear()
        self.snack_name_lineedit_3.clear()
        self.snack_price_lineedit_3.clear()

    def calculate_invoice_3(self):
        if self.device_invoice_lineedit_3.text() == "":
            self.device_invoice_lineedit_3.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_3.text()

        if self.snack_invoice_lineedit_3.text() == "":
            self.snack_invoice_lineedit_3.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_3.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_3.setText(str(total_invoice))

        self.invoice_time_lineedit_3.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_3.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_3.setEnabled(True)
        self.calculate_invoice_button_3.setDisabled(True)

        self.snack_add_button_3.setDisabled(True)
        self.reset_snack_list_button_3.setDisabled(True)

        self.reset_timer_button_3.setDisabled(True)

    def pay_invoice_3(self):
        self.pay_invoice_button_3.setDisabled(True)
        self.calculate_invoice_button_3.setDisabled(True)

        device_name = self.device_name_lineedit_3.text()
        hourly_rate = self.hourly_rate_lineedit_3.text()
        snack_invoice = self.snack_invoice_lineedit_3.text()
        device_invoice = self.device_invoice_lineedit_3.text()
        total_invoice = self.total_invoice_lineedit_3.text()
        invoice_time = self.invoice_time_lineedit_3.text()
        invoice_date = self.invoice_date_lineedit_3.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_3(self):
        self.calculate_invoice_button_3.setEnabled(True)

        self.device_invoice_lineedit_3.clear()
        self.snack_invoice_lineedit_3.clear()
        self.total_invoice_lineedit_3.clear()
        self.invoice_time_lineedit_3.clear()
        self.invoice_date_lineedit_3.clear()

        self.reset_timer_3()
        self.reset_snack_list_3()

    ########################################################################################################################

    def start_timer_4(self):
        if not self.hourly_rate_lineedit_4.text() == "":
            self.start_timer_button_4.setDisabled(True)
            self.stop_timer_button_4.setEnabled(True)
            self.reset_timer_button_4.setEnabled(True)

            self.start_time_lineedit_4.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_4.start(1000)

            self.snack_add_button_4.setEnabled(True)
            self.reset_snack_list_button_4.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_4(self):
        self.stop_timer_button_4.setDisabled(True)
        self.timer_4.stop()

        self.stop_time_lineedit_4.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_4.setEnabled(True)

    def update_timer_4(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_4.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_4.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_4.text())

        work_done = int(elapsed_time / 3600 * rate)

        self.device_invoice_lineedit_4.setText(str(work_done))

    def reset_timer_4(self):
        self.start_timer_button_4.setEnabled(True)
        self.stop_timer_button_4.setDisabled(True)
        self.reset_timer_button_4.setDisabled(True)

        self.calculate_invoice_button_4.setDisabled(True)

        self.timer_4.stop()

        self.timer_lineedit_4.setText(self.time_zero)
        self.start_time_lineedit_4.clear()
        self.stop_time_lineedit_4.clear()
        self.device_invoice_lineedit_4.clear()

    def add_snack_to_table_4(self):
        if not self.snack_price_lineedit_4.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_4.text())
            price = QTableWidgetItem(self.snack_price_lineedit_4.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_4.rowCount()
            self.snack_table_4.insertRow(row_count)
            self.snack_table_4.setItem(row_count, 0, name)
            self.snack_table_4.setItem(row_count, 1, price)

            self.snack_name_lineedit_4.clear()
            self.snack_price_lineedit_4.clear()

            total = 0
            for row in range(self.snack_table_4.rowCount()):
                price = int(self.snack_table_4.item(row, 1).text())
                total += price

            self.snack_invoice_4 = total

            self.snack_invoice_lineedit_4.setText(str(self.snack_invoice_4))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_4(self):
        self.snack_table_4.clearContents()
        self.snack_table_4.setRowCount(0)
        self.snack_invoice_lineedit_4.clear()
        self.snack_name_lineedit_4.clear()
        self.snack_price_lineedit_4.clear()

    def calculate_invoice_4(self):
        if self.device_invoice_lineedit_4.text() == "":
            self.device_invoice_lineedit_4.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_4.text()

        if self.snack_invoice_lineedit_4.text() == "":
            self.snack_invoice_lineedit_4.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_4.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_4.setText(str(total_invoice))

        self.invoice_time_lineedit_4.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_4.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_4.setEnabled(True)
        self.calculate_invoice_button_4.setDisabled(True)

        self.snack_add_button_4.setDisabled(True)
        self.reset_snack_list_button_4.setDisabled(True)

        self.reset_timer_button_4.setDisabled(True)

    def pay_invoice_4(self):
        self.pay_invoice_button_4.setDisabled(True)
        self.calculate_invoice_button_4.setDisabled(True)

        device_name = self.device_name_lineedit_4.text()
        hourly_rate = self.hourly_rate_lineedit_4.text()
        snack_invoice = self.snack_invoice_lineedit_4.text()
        device_invoice = self.device_invoice_lineedit_4.text()
        total_invoice = self.total_invoice_lineedit_4.text()
        invoice_time = self.invoice_time_lineedit_4.text()
        invoice_date = self.invoice_date_lineedit_4.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_4(self):
        self.calculate_invoice_button_4.setEnabled(True)

        self.device_invoice_lineedit_4.clear()
        self.snack_invoice_lineedit_4.clear()
        self.total_invoice_lineedit_4.clear()
        self.invoice_time_lineedit_4.clear()
        self.invoice_date_lineedit_4.clear()

        self.reset_timer_4()
        self.reset_snack_list_4()

    ########################################################################################################################

    def start_timer_5(self):
        if not self.hourly_rate_lineedit_5.text() == "":
            self.start_timer_button_5.setDisabled(True)
            self.stop_timer_button_5.setEnabled(True)
            self.reset_timer_button_5.setEnabled(True)

            self.start_time_lineedit_5.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_5.start(1000)

            self.snack_add_button_5.setEnabled(True)
            self.reset_snack_list_button_5.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_5(self):
        self.stop_timer_button_5.setDisabled(True)
        self.timer_5.stop()

        self.stop_time_lineedit_5.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_5.setEnabled(True)

    def update_timer_5(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_5.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_5.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_5.text())

        work_done = int(elapsed_time / 3600 * rate)

        self.device_invoice_lineedit_5.setText(str(work_done))

    def reset_timer_5(self):
        self.start_timer_button_5.setEnabled(True)
        self.stop_timer_button_5.setDisabled(True)
        self.reset_timer_button_5.setDisabled(True)

        self.calculate_invoice_button_5.setDisabled(True)

        self.timer_5.stop()

        self.timer_lineedit_5.setText(self.time_zero)
        self.start_time_lineedit_5.clear()
        self.stop_time_lineedit_5.clear()
        self.device_invoice_lineedit_5.clear()

    def add_snack_to_table_5(self):
        if not self.snack_price_lineedit_5.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_5.text())
            price = QTableWidgetItem(self.snack_price_lineedit_5.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_5.rowCount()
            self.snack_table_5.insertRow(row_count)
            self.snack_table_5.setItem(row_count, 0, name)
            self.snack_table_5.setItem(row_count, 1, price)

            self.snack_name_lineedit_5.clear()
            self.snack_price_lineedit_5.clear()

            total = 0
            for row in range(self.snack_table_5.rowCount()):
                price = int(self.snack_table_5.item(row, 1).text())
                total += price

            self.snack_invoice_5 = total

            self.snack_invoice_lineedit_5.setText(str(self.snack_invoice_5))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_5(self):
        self.snack_table_5.clearContents()
        self.snack_table_5.setRowCount(0)
        self.snack_invoice_lineedit_5.clear()
        self.snack_name_lineedit_5.clear()
        self.snack_price_lineedit_5.clear()

    def calculate_invoice_5(self):
        if self.device_invoice_lineedit_5.text() == "":
            self.device_invoice_lineedit_5.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_5.text()

        if self.snack_invoice_lineedit_5.text() == "":
            self.snack_invoice_lineedit_5.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_5.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_5.setText(str(total_invoice))

        self.invoice_time_lineedit_5.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_5.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_5.setEnabled(True)
        self.calculate_invoice_button_5.setDisabled(True)

        self.snack_add_button_5.setDisabled(True)
        self.reset_snack_list_button_5.setDisabled(True)

        self.reset_timer_button_5.setDisabled(True)

    def pay_invoice_5(self):
        self.pay_invoice_button_5.setDisabled(True)
        self.calculate_invoice_button_5.setDisabled(True)

        device_name = self.device_name_lineedit_5.text()
        hourly_rate = self.hourly_rate_lineedit_5.text()
        snack_invoice = self.snack_invoice_lineedit_5.text()
        device_invoice = self.device_invoice_lineedit_5.text()
        total_invoice = self.total_invoice_lineedit_5.text()
        invoice_time = self.invoice_time_lineedit_5.text()
        invoice_date = self.invoice_date_lineedit_5.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_5(self):
        self.calculate_invoice_button_5.setEnabled(True)

        self.device_invoice_lineedit_5.clear()
        self.snack_invoice_lineedit_5.clear()
        self.total_invoice_lineedit_5.clear()
        self.invoice_time_lineedit_5.clear()
        self.invoice_date_lineedit_5.clear()

        self.reset_timer_5()
        self.reset_snack_list_5()

    ########################################################################################################################

    def start_timer_6(self):
        if not self.hourly_rate_lineedit_6.text() == "":
            self.start_timer_button_6.setDisabled(True)
            self.stop_timer_button_6.setEnabled(True)
            self.reset_timer_button_6.setEnabled(True)

            self.start_time_lineedit_6.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_6.start(1000)

            self.snack_add_button_6.setEnabled(True)
            self.reset_snack_list_button_6.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_6(self):
        self.stop_timer_button_6.setDisabled(True)
        self.timer_6.stop()

        self.stop_time_lineedit_6.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_6.setEnabled(True)

    def update_timer_6(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_6.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_6.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_6.text())

        work_done = int(elapsed_time / 3600 * rate)

        self.device_invoice_lineedit_6.setText(str(work_done))

    def reset_timer_6(self):
        self.start_timer_button_6.setEnabled(True)
        self.stop_timer_button_6.setDisabled(True)
        self.reset_timer_button_6.setDisabled(True)

        self.calculate_invoice_button_6.setDisabled(True)

        self.timer_6.stop()

        self.timer_lineedit_6.setText(self.time_zero)
        self.start_time_lineedit_6.clear()
        self.stop_time_lineedit_6.clear()
        self.device_invoice_lineedit_6.clear()

    def add_snack_to_table_6(self):
        if not self.snack_price_lineedit_6.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_6.text())
            price = QTableWidgetItem(self.snack_price_lineedit_6.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_6.rowCount()
            self.snack_table_6.insertRow(row_count)
            self.snack_table_6.setItem(row_count, 0, name)
            self.snack_table_6.setItem(row_count, 1, price)

            self.snack_name_lineedit_6.clear()
            self.snack_price_lineedit_6.clear()

            total = 0
            for row in range(self.snack_table_6.rowCount()):
                price = int(self.snack_table_6.item(row, 1).text())
                total += price

            self.snack_invoice_6 = total

            self.snack_invoice_lineedit_6.setText(str(self.snack_invoice_6))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_6(self):
        self.snack_table_6.clearContents()
        self.snack_table_6.setRowCount(0)
        self.snack_invoice_lineedit_6.clear()
        self.snack_name_lineedit_6.clear()
        self.snack_price_lineedit_6.clear()

    def calculate_invoice_6(self):
        if self.device_invoice_lineedit_6.text() == "":
            self.device_invoice_lineedit_6.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_6.text()

        if self.snack_invoice_lineedit_6.text() == "":
            self.snack_invoice_lineedit_6.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_6.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_6.setText(str(total_invoice))

        self.invoice_time_lineedit_6.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_6.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_6.setEnabled(True)
        self.calculate_invoice_button_6.setDisabled(True)

        self.snack_add_button_6.setDisabled(True)
        self.reset_snack_list_button_6.setDisabled(True)

        self.reset_timer_button_6.setDisabled(True)

    def pay_invoice_6(self):
        self.pay_invoice_button_6.setDisabled(True)
        self.calculate_invoice_button_6.setDisabled(True)

        device_name = self.device_name_lineedit_6.text()
        hourly_rate = self.hourly_rate_lineedit_6.text()
        snack_invoice = self.snack_invoice_lineedit_6.text()
        device_invoice = self.device_invoice_lineedit_6.text()
        total_invoice = self.total_invoice_lineedit_6.text()
        invoice_time = self.invoice_time_lineedit_6.text()
        invoice_date = self.invoice_date_lineedit_6.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_6(self):
        self.calculate_invoice_button_6.setEnabled(True)

        self.device_invoice_lineedit_6.clear()
        self.snack_invoice_lineedit_6.clear()
        self.total_invoice_lineedit_6.clear()
        self.invoice_time_lineedit_6.clear()
        self.invoice_date_lineedit_6.clear()

        self.reset_timer_6()
        self.reset_snack_list_6()

    ########################################################################################################################

    def start_timer_7(self):
        if not self.hourly_rate_lineedit_7.text() == "":
            self.start_timer_button_7.setDisabled(True)
            self.stop_timer_button_7.setEnabled(True)
            self.reset_timer_button_7.setEnabled(True)

            self.start_time_lineedit_7.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_7.start(1000)

            self.snack_add_button_7.setEnabled(True)
            self.reset_snack_list_button_7.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_7(self):
        self.stop_timer_button_7.setDisabled(True)
        self.timer_7.stop()

        self.stop_time_lineedit_7.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_7.setEnabled(True)

    def update_timer_7(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_7.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_7.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_7.text())

        work_done = int(elapsed_time / 3700 * rate)

        self.device_invoice_lineedit_7.setText(str(work_done))

    def reset_timer_7(self):
        self.start_timer_button_7.setEnabled(True)
        self.stop_timer_button_7.setDisabled(True)
        self.reset_timer_button_7.setDisabled(True)

        self.calculate_invoice_button_7.setDisabled(True)

        self.timer_7.stop()

        self.timer_lineedit_7.setText(self.time_zero)
        self.start_time_lineedit_7.clear()
        self.stop_time_lineedit_7.clear()
        self.device_invoice_lineedit_7.clear()

    def add_snack_to_table_7(self):
        if not self.snack_price_lineedit_7.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_7.text())
            price = QTableWidgetItem(self.snack_price_lineedit_7.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_7.rowCount()
            self.snack_table_7.insertRow(row_count)
            self.snack_table_7.setItem(row_count, 0, name)
            self.snack_table_7.setItem(row_count, 1, price)

            self.snack_name_lineedit_7.clear()
            self.snack_price_lineedit_7.clear()

            total = 0
            for row in range(self.snack_table_7.rowCount()):
                price = int(self.snack_table_7.item(row, 1).text())
                total += price

            self.snack_invoice_7 = total

            self.snack_invoice_lineedit_7.setText(str(self.snack_invoice_7))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_7(self):
        self.snack_table_7.clearContents()
        self.snack_table_7.setRowCount(0)
        self.snack_invoice_lineedit_7.clear()
        self.snack_name_lineedit_7.clear()
        self.snack_price_lineedit_7.clear()

    def calculate_invoice_7(self):
        if self.device_invoice_lineedit_7.text() == "":
            self.device_invoice_lineedit_7.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_7.text()

        if self.snack_invoice_lineedit_7.text() == "":
            self.snack_invoice_lineedit_7.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_7.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_7.setText(str(total_invoice))

        self.invoice_time_lineedit_7.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_7.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_7.setEnabled(True)
        self.calculate_invoice_button_7.setDisabled(True)

        self.snack_add_button_7.setDisabled(True)
        self.reset_snack_list_button_7.setDisabled(True)

        self.reset_timer_button_7.setDisabled(True)

    def pay_invoice_7(self):
        self.pay_invoice_button_7.setDisabled(True)
        self.calculate_invoice_button_7.setDisabled(True)

        device_name = self.device_name_lineedit_7.text()
        hourly_rate = self.hourly_rate_lineedit_7.text()
        snack_invoice = self.snack_invoice_lineedit_7.text()
        device_invoice = self.device_invoice_lineedit_7.text()
        total_invoice = self.total_invoice_lineedit_7.text()
        invoice_time = self.invoice_time_lineedit_7.text()
        invoice_date = self.invoice_date_lineedit_7.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_7(self):
        self.calculate_invoice_button_7.setEnabled(True)

        self.device_invoice_lineedit_7.clear()
        self.snack_invoice_lineedit_7.clear()
        self.total_invoice_lineedit_7.clear()
        self.invoice_time_lineedit_7.clear()
        self.invoice_date_lineedit_7.clear()

        self.reset_timer_7()
        self.reset_snack_list_7()

    ########################################################################################################################

    def start_timer_8(self):
        if not self.hourly_rate_lineedit_8.text() == "":
            self.start_timer_button_8.setDisabled(True)
            self.stop_timer_button_8.setEnabled(True)
            self.reset_timer_button_8.setEnabled(True)

            self.start_time_lineedit_8.setText(
                QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            )

            self.timer_8.start(1000)

            self.snack_add_button_8.setEnabled(True)
            self.reset_snack_list_button_8.setEnabled(True)

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Hourly Rate!")

    def stop_timer_8(self):
        self.stop_timer_button_8.setDisabled(True)
        self.timer_8.stop()

        self.stop_time_lineedit_8.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.calculate_invoice_button_8.setEnabled(True)

    def update_timer_8(self):
        elapsed_time = QTime.fromString(
            self.start_time_lineedit_8.text(), Qt.DefaultLocaleLongDate
        ).secsTo(QTime.currentTime())
        self.timer_lineedit_8.setText(
            QTime(0, 0).addSecs(elapsed_time).toString("hh:mm:ss")
        )

        rate = int(self.hourly_rate_lineedit_8.text())

        work_done = int(elapsed_time / 3800 * rate)

        self.device_invoice_lineedit_8.setText(str(work_done))

    def reset_timer_8(self):
        self.start_timer_button_8.setEnabled(True)
        self.stop_timer_button_8.setDisabled(True)
        self.reset_timer_button_8.setDisabled(True)

        self.calculate_invoice_button_8.setDisabled(True)

        self.timer_8.stop()

        self.timer_lineedit_8.setText(self.time_zero)
        self.start_time_lineedit_8.clear()
        self.stop_time_lineedit_8.clear()
        self.device_invoice_lineedit_8.clear()

    def add_snack_to_table_8(self):
        if not self.snack_price_lineedit_8.text() == "":
            name = QTableWidgetItem(self.snack_name_lineedit_8.text())
            price = QTableWidgetItem(self.snack_price_lineedit_8.text())

            name.setTextAlignment(Qt.AlignCenter)
            price.setTextAlignment(Qt.AlignCenter)

            row_count = self.snack_table_8.rowCount()
            self.snack_table_8.insertRow(row_count)
            self.snack_table_8.setItem(row_count, 0, name)
            self.snack_table_8.setItem(row_count, 1, price)

            self.snack_name_lineedit_8.clear()
            self.snack_price_lineedit_8.clear()

            total = 0
            for row in range(self.snack_table_8.rowCount()):
                price = int(self.snack_table_8.item(row, 1).text())
                total += price

            self.snack_invoice_8 = total

            self.snack_invoice_lineedit_8.setText(str(self.snack_invoice_8))

        else:
            QMessageBox.warning(self, "Empty Field", "Enter the Price of Snack!")

    def reset_snack_list_8(self):
        self.snack_table_8.clearContents()
        self.snack_table_8.setRowCount(0)
        self.snack_invoice_lineedit_8.clear()
        self.snack_name_lineedit_8.clear()
        self.snack_price_lineedit_8.clear()

    def calculate_invoice_8(self):
        if self.device_invoice_lineedit_8.text() == "":
            self.device_invoice_lineedit_8.setText("0")
            device_invoice = 0
        else:
            device_invoice = self.device_invoice_lineedit_8.text()

        if self.snack_invoice_lineedit_8.text() == "":
            self.snack_invoice_lineedit_8.setText("0")
            snack_invoice = 0
        else:
            snack_invoice = self.snack_invoice_lineedit_8.text()

        total_invoice = int(device_invoice) + int(snack_invoice)

        self.total_invoice_lineedit_8.setText(str(total_invoice))

        self.invoice_time_lineedit_8.setText(
            QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
        )

        self.invoice_date_lineedit_8.setText(str(jdatetime.date.today()))

        self.pay_invoice_button_8.setEnabled(True)
        self.calculate_invoice_button_8.setDisabled(True)

        self.snack_add_button_8.setDisabled(True)
        self.reset_snack_list_button_8.setDisabled(True)

        self.reset_timer_button_8.setDisabled(True)

    def pay_invoice_8(self):
        self.pay_invoice_button_8.setDisabled(True)
        self.calculate_invoice_button_8.setDisabled(True)

        device_name = self.device_name_lineedit_8.text()
        hourly_rate = self.hourly_rate_lineedit_8.text()
        snack_invoice = self.snack_invoice_lineedit_8.text()
        device_invoice = self.device_invoice_lineedit_8.text()
        total_invoice = self.total_invoice_lineedit_8.text()
        invoice_time = self.invoice_time_lineedit_8.text()
        invoice_date = self.invoice_date_lineedit_8.text()

        self.invoice_db.add_to_db(
            device_name,
            hourly_rate,
            snack_invoice,
            device_invoice,
            total_invoice,
            invoice_time,
            invoice_date,
        )

        QMessageBox.information(self, "SAVE INFO", "Invoce Saved in DataBase")

    def reset_invoice_8(self):
        self.calculate_invoice_button_8.setEnabled(True)

        self.device_invoice_lineedit_8.clear()
        self.snack_invoice_lineedit_8.clear()
        self.total_invoice_lineedit_8.clear()
        self.invoice_time_lineedit_8.clear()
        self.invoice_date_lineedit_8.clear()

        self.reset_timer_8()
        self.reset_snack_list_8()

    ########################################################################################################################

    def separate_device_invoice_pay(self):
        if not self.device_invoice_lineedit_separate.text() == "":
            device_name = "SEPARATE INVOICE"
            hourly_rate = "SEPARATE INVOICE"
            snack_invoice = "0"
            device_invoice = self.device_invoice_lineedit_separate.text()
            total_invoice = self.device_invoice_lineedit_separate.text()
            invoice_time = QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            invoice_date = str(jdatetime.date.today())

            self.invoice_db.add_to_db(
                device_name,
                hourly_rate,
                snack_invoice,
                device_invoice,
                total_invoice,
                invoice_time,
                invoice_date,
            )

            self.device_invoice_lineedit_separate.clear()
            QMessageBox.information(
                self, "SAVE INFO", "Separate Invoce Saved in DataBase"
            )
        else:
            QMessageBox.critical(self, "Empty Field", "Enter the Invoice of Device!")

    def separate_snack_invoice_pay(self):
        if not self.snack_invoice_lineedit_separate.text() == "":
            device_name = "SEPARATE INVOICE"
            hourly_rate = "SEPARATE INVOICE"
            snack_invoice = self.snack_invoice_lineedit_separate.text()
            device_invoice = "0"
            total_invoice = self.snack_invoice_lineedit_separate.text()
            invoice_time = QTime.currentTime().toString(Qt.DefaultLocaleLongDate)
            invoice_date = str(jdatetime.date.today())

            self.invoice_db.add_to_db(
                device_name,
                hourly_rate,
                snack_invoice,
                device_invoice,
                total_invoice,
                invoice_time,
                invoice_date,
            )

            self.snack_invoice_lineedit_separate.clear()
            QMessageBox.information(
                self, "SAVE INFO", "Separate Invoce Saved in DataBase"
            )
        else:
            QMessageBox.critical(self, "Empty Field", "Enter the Invoice of Snack!")


class InvoiceWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.invoice_db = InvoiceDB()
        self.daily_invoice_db = DailyInvoiceDB()

        self.init_ui()
        self.refresh_invoice_table()

    def init_ui(self):
        self.setWindowTitle("Invoice")
        self.setWindowIcon(QIcon("invoice-window.ico"))
        self.setGeometry(800, 250, 950, 600)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(7)
        self.invoice_table.setStyleSheet("QTableWidget {alignment: center;}")
        self.invoice_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.invoice_table.setHorizontalHeaderLabels(
            [
                "Device Name",
                "Hourly Rate",
                "Snack Invoice",
                "Device Invoice",
                "Total Invoice",
                "Invoice Time",
                "Invoice Date",
            ]
        )

        invoice_table_groupbox = QGroupBox("Invoces")
        invoice_table_layout = QVBoxLayout(invoice_table_groupbox)
        invoice_table_layout.addWidget(self.invoice_table)

        total_device_invoice_label = QLabel("Total Device Invoice:")
        total_snack_invoice_label = QLabel("Total Snack Invoice:")
        total_device_and_snack_invoice_label = QLabel("Total Device and Snack Invoice:")
        last_refresh_time_label = QLabel("Last Refresh Time:")

        self.total_device_invoice_lineedit = QLineEdit()
        self.total_snack_invoice_lineedit = QLineEdit()
        self.total_device_and_snack_invoice_lineedit = QLineEdit()
        self.last_refresh_time_lineedit = QLineEdit()

        self.total_device_invoice_lineedit.setReadOnly(True)
        self.total_snack_invoice_lineedit.setReadOnly(True)
        self.total_device_and_snack_invoice_lineedit.setReadOnly(True)
        self.last_refresh_time_lineedit.setReadOnly(True)

        invoice_record_groupbox = QGroupBox("Records")
        invoice_record_layout = QFormLayout(invoice_record_groupbox)
        invoice_record_layout.addRow(
            total_device_invoice_label, self.total_device_invoice_lineedit
        )
        invoice_record_layout.addRow(
            total_snack_invoice_label, self.total_snack_invoice_lineedit
        )
        invoice_record_layout.addRow(
            total_device_and_snack_invoice_label,
            self.total_device_and_snack_invoice_lineedit,
        )
        invoice_record_layout.addRow(
            last_refresh_time_label,
            self.last_refresh_time_lineedit,
        )

        self.add_daily_invoice_button = QPushButton("Add Daily Invoce")
        delete_table_button = QPushButton("Delete Invoces")

        self.add_daily_invoice_button.clicked.connect(self.add_daily_invoice)
        delete_table_button.clicked.connect(self.delete_invoice_table)

        invoice_button_groupbox = QGroupBox()
        invoice_button_layout = QFormLayout(invoice_button_groupbox)
        invoice_button_layout.addRow(self.add_daily_invoice_button)
        invoice_button_layout.addRow(delete_table_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(invoice_table_groupbox)
        main_layout.addWidget(invoice_record_groupbox)
        main_layout.addWidget(invoice_button_groupbox)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def refresh_invoice_table(self):
        data = self.invoice_db.load_from_db()
        self.invoice_table.setRowCount(len(data))

        for row, item in enumerate(data):
            for col, value in enumerate(item[1:]):
                val = QTableWidgetItem(value)
                val.setTextAlignment(Qt.AlignCenter)
                self.invoice_table.setItem(row, col, val)

        total_snack_invoice = sum(
            int(self.invoice_table.item(row, 2).text())
            for row in range(self.invoice_table.rowCount())
        )

        total_device_invoice = sum(
            int(self.invoice_table.item(row, 3).text())
            for row in range(self.invoice_table.rowCount())
        )

        total_device_and_snack_invoice = total_snack_invoice + total_device_invoice

        self.total_snack_invoice_lineedit.setText(str(total_snack_invoice))
        self.total_device_invoice_lineedit.setText(str(total_device_invoice))
        self.total_device_and_snack_invoice_lineedit.setText(
            str(total_device_and_snack_invoice)
        )
        self.last_refresh_time_lineedit.setText(
            str(
                f"{str(jdatetime.date.today())} _ {QTime.currentTime().toString(Qt.DefaultLocaleLongDate)}"
            )
        )

        QTimer.singleShot(500, self.refresh_invoice_table)

    def add_daily_invoice(self):
        self.refresh_invoice_table()

        self.add_daily_invoice_button.setDisabled(True)

        total_device_invoice = self.total_device_invoice_lineedit.text()
        total_snack_invoice = self.total_snack_invoice_lineedit.text()
        total_device_and_snack_invoice = (
            self.total_device_and_snack_invoice_lineedit.text()
        )
        last_refresh_time = self.last_refresh_time_lineedit.text()

        self.daily_invoice_db.add_to_db(
            total_device_invoice,
            total_snack_invoice,
            total_device_and_snack_invoice,
            last_refresh_time,
        )

        QMessageBox.information(self, "SAVE INFO", "Daily Invoice Saved in DataBase")

    def delete_invoice_table(self):
        self.invoice_db.delete_all_data_from_table()
        self.refresh_invoice_table()
        self.add_daily_invoice_button.setEnabled(True)

    def closeEvent(self, event):
        self.close()


class DailyInvoiceWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.daily_invoice_db = DailyInvoiceDB()

        self.init_ui()
        self.refresh_daily_invoice_table()

    def init_ui(self):
        self.setWindowTitle("Daily Invoice")
        self.setWindowIcon(QIcon("daily-invoice-window.ico"))
        self.setGeometry(800, 350, 850, 600)

        self.daily_invoice_table = QTableWidget()
        self.daily_invoice_table.setColumnCount(4)
        self.daily_invoice_table.setStyleSheet("QTableWidget {alignment: center;}")
        self.daily_invoice_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.daily_invoice_table.setHorizontalHeaderLabels(
            [
                "Total Device Invoice",
                "Total Snack Invoice",
                "Total Device And Snack Invoice",
                "Last Refresh Time",
            ]
        )
        self.daily_invoice_table.resizeColumnsToContents()

        daily_invoice_table_groupbox = QGroupBox("Daily Invoces")
        daily_invoice_table_layout = QVBoxLayout(daily_invoice_table_groupbox)
        daily_invoice_table_layout.addWidget(self.daily_invoice_table)

        total_device_invoice_label = QLabel("Total Device Invoice:")
        total_snack_invoice_label = QLabel("Total Snack Invoice:")
        total_device_and_snack_invoice_label = QLabel("Total Device and Snack Invoice:")
        last_refresh_time_label = QLabel("Last Refresh Time:")

        self.total_device_invoice_lineedit = QLineEdit()
        self.total_snack_invoice_lineedit = QLineEdit()
        self.total_device_and_snack_invoice_lineedit = QLineEdit()
        self.last_refresh_time_lineedit = QLineEdit()

        self.total_device_invoice_lineedit.setReadOnly(True)
        self.total_snack_invoice_lineedit.setReadOnly(True)
        self.total_device_and_snack_invoice_lineedit.setReadOnly(True)
        self.last_refresh_time_lineedit.setReadOnly(True)

        invoice_record_groupbox = QGroupBox("Records")
        invoice_record_layout = QFormLayout(invoice_record_groupbox)
        invoice_record_layout.addRow(
            total_device_invoice_label, self.total_device_invoice_lineedit
        )
        invoice_record_layout.addRow(
            total_snack_invoice_label, self.total_snack_invoice_lineedit
        )
        invoice_record_layout.addRow(
            total_device_and_snack_invoice_label,
            self.total_device_and_snack_invoice_lineedit,
        )
        invoice_record_layout.addRow(
            last_refresh_time_label,
            self.last_refresh_time_lineedit,
        )

        delete_table_button = QPushButton("Delete Invoces")

        delete_table_button.clicked.connect(self.delete_daily_invoice_table)

        invoice_button_groupbox = QGroupBox()
        invoice_button_layout = QFormLayout(invoice_button_groupbox)
        invoice_button_layout.addRow(delete_table_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(daily_invoice_table_groupbox)
        main_layout.addWidget(invoice_record_groupbox)
        main_layout.addWidget(invoice_button_groupbox)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def refresh_daily_invoice_table(self):
        data = self.daily_invoice_db.load_from_db()
        self.daily_invoice_table.setRowCount(len(data))

        for row, item in enumerate(data):
            for col, value in enumerate(item[1:]):
                val = QTableWidgetItem(value)
                val.setTextAlignment(Qt.AlignCenter)
                self.daily_invoice_table.setItem(row, col, val)

        total_device_invoice = sum(
            int(self.daily_invoice_table.item(row, 0).text())
            for row in range(self.daily_invoice_table.rowCount())
        )

        total_snack_invoice = sum(
            int(self.daily_invoice_table.item(row, 1).text())
            for row in range(self.daily_invoice_table.rowCount())
        )

        total_device_and_snack_invoice = total_snack_invoice + total_device_invoice

        self.total_snack_invoice_lineedit.setText(str(total_snack_invoice))
        self.total_device_invoice_lineedit.setText(str(total_device_invoice))
        self.total_device_and_snack_invoice_lineedit.setText(
            str(total_device_and_snack_invoice)
        )
        self.last_refresh_time_lineedit.setText(
            str(
                f"{str(jdatetime.date.today())} _ {QTime.currentTime().toString(Qt.DefaultLocaleLongDate)}"
            )
        )

        QTimer.singleShot(500, self.refresh_daily_invoice_table)

    def delete_daily_invoice_table(self):
        self.daily_invoice_db.delete_all_data_from_table()
        self.refresh_daily_invoice_table()

    def closeEvent(self, event):
        self.close()


class DebtorListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.debtor_list_db = DebtorListDB()

        self.init_ui()
        self.update_table()

    def init_ui(self):
        self.setWindowTitle("Debtor List")
        self.setGeometry(200, 200, 950, 500)
        self.setWindowIcon(QIcon("debtor-list-window.ico"))

        self.debtor_table = QTableWidget()
        self.debtor_table.setColumnCount(7)
        self.debtor_table.itemClicked.connect(self.select_debtor)
        self.debtor_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.debtor_table.setHorizontalHeaderLabels(
            [
                "ID",
                "First Name",
                "Last Name",
                "Device Debt",
                "Snack Debt",
                "Time",
                "Date",
            ]
        )

        debtor_table_groupbox = QGroupBox("List")
        debtor_table_layout = QFormLayout(debtor_table_groupbox)
        debtor_table_layout.addRow(self.debtor_table)

        first_name_label = QLabel("First Name:")
        self.first_name_input = QLineEdit()

        last_name_label = QLabel("Last Name:")
        self.last_name_input = QLineEdit()

        device_debt_label = QLabel("Device Debt:")
        self.device_debt_input = QLineEdit()

        snack_debt_label = QLabel("Snack Debt:")
        self.snack_debt_input = QLineEdit()

        debt_time_label = QLabel("Debt Time:")
        self.debt_time_input = QLineEdit()

        debt_date_label = QLabel("Debt Date:")
        self.debt_date_input = QLineEdit()

        input_groupbox = QGroupBox("Inputs")
        input_layout = QGridLayout(input_groupbox)
        input_layout.addWidget(first_name_label, 0, 0)
        input_layout.addWidget(self.first_name_input, 0, 1)
        input_layout.addWidget(last_name_label, 0, 2)
        input_layout.addWidget(self.last_name_input, 0, 3)
        input_layout.addWidget(device_debt_label, 1, 0)
        input_layout.addWidget(self.device_debt_input, 1, 1)
        input_layout.addWidget(snack_debt_label, 1, 2)
        input_layout.addWidget(self.snack_debt_input, 1, 3)
        input_layout.addWidget(debt_time_label, 2, 0)
        input_layout.addWidget(self.debt_time_input, 2, 1)
        input_layout.addWidget(debt_date_label, 2, 2)
        input_layout.addWidget(self.debt_date_input, 2, 3)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_debtor)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_debtor)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_debtor)

        delete_all_button = QPushButton("Delete All")
        delete_all_button.clicked.connect(self.delete_all_debtors)

        current_time_button = QPushButton("Current Time")
        current_time_button.clicked.connect(self.current_time)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_inputs)

        button_groupbox = QGroupBox("Buttons")
        button_layout = QGridLayout(button_groupbox)
        button_layout.addWidget(add_button, 0, 0)
        button_layout.addWidget(edit_button, 0, 1)
        button_layout.addWidget(delete_button, 0, 2)
        button_layout.addWidget(delete_all_button, 0, 3)
        button_layout.addWidget(current_time_button, 0, 4)
        button_layout.addWidget(clear_button, 0, 5)

        main_layout = QVBoxLayout()
        main_layout.addWidget(debtor_table_groupbox)
        main_layout.addWidget(input_groupbox)
        main_layout.addWidget(button_groupbox)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def select_debtor(self, item):
        row = item.row()
        debtor_id = self.debtor_table.item(row, 0).text()
        first_name = self.debtor_table.item(row, 1).text()
        last_name = self.debtor_table.item(row, 2).text()
        device_debt = self.debtor_table.item(row, 3).text()
        snack_debt = self.debtor_table.item(row, 4).text()
        time = self.debtor_table.item(row, 5).text()
        date = self.debtor_table.item(row, 6).text()

        self.first_name_input.setText(first_name)
        self.last_name_input.setText(last_name)
        self.device_debt_input.setText(device_debt)
        self.snack_debt_input.setText(snack_debt)
        self.debt_time_input.setText(time)
        self.debt_date_input.setText(date)

    def update_table(self):
        self.debtor_table.setRowCount(0)
        debtors = self.debtor_list_db.get_debtors()
        for row, debtor in enumerate(debtors):
            self.debtor_table.insertRow(row)
            for col, value in enumerate(debtor):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.debtor_table.setItem(row, col, item)

    def add_debtor(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        device_debt_text = self.device_debt_input.text()
        device_debt = int(device_debt_text) if device_debt_text else 0
        snack_debt_text = self.snack_debt_input.text()
        snack_debt = int(self.snack_debt_input.text()) if snack_debt_text else 0
        time = self.debt_time_input.text()
        date = self.debt_date_input.text()
        self.debtor_list_db.add_debtor(
            first_name, last_name, device_debt, snack_debt, time, date
        )
        self.update_table()
        self.clear_inputs()

    def edit_debtor(self):
        selected_row = self.debtor_table.currentRow()
        if selected_row >= 0:
            debtor_id = int(self.debtor_table.item(selected_row, 0).text())
            first_name = self.first_name_input.text()
            last_name = self.last_name_input.text()
            device_debt_text = self.device_debt_input.text()
            device_debt = int(device_debt_text) if device_debt_text else 0
            snack_debt_text = self.snack_debt_input.text()
            snack_debt = int(self.snack_debt_input.text()) if snack_debt_text else 0
            time = self.debt_time_input.text()
            date = self.debt_date_input.text()
            self.debtor_list_db.edit_debtor(
                debtor_id, first_name, last_name, device_debt, snack_debt, time, date
            )
            self.update_table()
            self.clear_inputs()

    def delete_debtor(self):
        selected_row = self.debtor_table.currentRow()
        if selected_row >= 0:
            debtor_id = int(self.debtor_table.item(selected_row, 0).text())
            self.debtor_list_db.delete_debtor(debtor_id)
            self.update_table()
            self.clear_inputs()

    def delete_all_debtors(self):
        self.debtor_list_db.delete_all_debtors()
        self.update_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.device_debt_input.clear()
        self.snack_debt_input.clear()
        self.debt_time_input.clear()
        self.debt_date_input.clear()

        self.debtor_table.clearSelection()

    def current_time(self):
        curr_time = str(QTime.currentTime().toString(Qt.DefaultLocaleLongDate))
        curr_date = str(jdatetime.date.today())

        self.debt_time_input.setText(curr_time)
        self.debt_date_input.setText(curr_date)


class PaymentMethodWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.payment_method_db = PaymentMethodDB()

        self.init_ui()
        self.populate_table()
        self.calculate_totals()

    def init_ui(self):
        self.setWindowTitle("Payment Method")
        self.setWindowIcon(QIcon("payment-method-window.ico"))

        self.payment_method_table = QTableWidget()
        self.payment_method_table.setColumnCount(5)
        self.payment_method_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.payment_method_table.setHorizontalHeaderLabels(
            ["Cash", "Card", "Total", "Payment Time", "Payment Date"]
        )

        payment_method_table_groupbox = QGroupBox("Payment History")
        payment_method_table_layout = QFormLayout(payment_method_table_groupbox)
        payment_method_table_layout.addRow(self.payment_method_table)

        cash_label = QLabel("Cash:")
        card_label = QLabel("Card:")
        payment_time_label = QLabel("Payment Time:")
        payment_date_label = QLabel("Payment Date:")

        self.cash_input = QLineEdit()
        self.card_input = QLineEdit()
        self.time_input = QLineEdit()
        self.date_input = QLineEdit()

        input_groupbox = QGroupBox("Payment Input")
        input_layout = QHBoxLayout(input_groupbox)
        input_layout.addWidget(cash_label)
        input_layout.addWidget(self.cash_input)
        input_layout.addWidget(card_label)
        input_layout.addWidget(self.card_input)
        input_layout.addWidget(payment_time_label)
        input_layout.addWidget(self.time_input)
        input_layout.addWidget(payment_date_label)
        input_layout.addWidget(self.date_input)

        total_cash_label = QLabel("Cash Total:")
        total_card_label = QLabel("Card Total:")
        total_total_label = QLabel("Total Total:")

        self.cash_total_label = QLineEdit()
        self.card_total_label = QLineEdit()
        self.total_total_label = QLineEdit()

        self.cash_total_label.setReadOnly(True)
        self.card_total_label.setReadOnly(True)
        self.total_total_label.setReadOnly(True)

        totals_groupbox = QGroupBox("Totals")
        totals_layout = QHBoxLayout(totals_groupbox)
        totals_layout.addWidget(total_cash_label)
        totals_layout.addWidget(self.cash_total_label)
        totals_layout.addWidget(total_card_label)
        totals_layout.addWidget(self.card_total_label)
        totals_layout.addWidget(total_total_label)
        totals_layout.addWidget(self.total_total_label)

        add_button = QPushButton("Add")
        delete_button = QPushButton("Delete")
        delete_all_button = QPushButton("Delete All")
        current_time_button = QPushButton("Current Time")
        clear_button = QPushButton("Clear")

        add_button.clicked.connect(self.add_payment)
        delete_button.clicked.connect(self.delete_payment)
        delete_all_button.clicked.connect(self.delete_all_payments)
        current_time_button.clicked.connect(self.current_time)
        clear_button.clicked.connect(self.clear_button)

        button_groupbox = QGroupBox()
        button_layout = QHBoxLayout(button_groupbox)
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(delete_all_button)
        button_layout.addWidget(current_time_button)
        button_layout.addWidget(clear_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(payment_method_table_groupbox)
        main_layout.addWidget(input_groupbox)
        main_layout.addWidget(totals_groupbox)
        main_layout.addWidget(button_groupbox)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def add_payment(self):
        cash = self.cash_input.text()
        card = self.card_input.text()
        time = self.time_input.text()
        date = self.date_input.text()

        if cash == "" or card == "" or not cash.isdigit() or not card.isdigit():
            QMessageBox.warning(self, "Error", "Invalid input for Cash or Card.")
            return

        total = int(cash) + int(card)
        self.payment_method_db.add_payment(cash, card, total, time, date)
        self.populate_table()
        self.calculate_totals()

        self.clear_button()

    def delete_payment(self):
        selected_row = self.payment_method_table.currentRow()
        if selected_row >= 0:
            cash_item = self.payment_method_table.item(selected_row, 0)
            card_item = self.payment_method_table.item(selected_row, 1)
            self.payment_method_db.delete_payment(cash_item.text(), card_item.text())
            self.payment_method_table.removeRow(selected_row)
            self.calculate_totals()

    def delete_all_payments(self):
        self.payment_method_db.delete_all_payments()
        self.payment_method_table.setRowCount(0)
        self.calculate_totals()

    def populate_table(self):
        self.payment_method_table.clearContents()

        payments = self.payment_method_db.get_payments()
        self.payment_method_table.setRowCount(len(payments))

        for row, payment in enumerate(payments):
            cash_item = QTableWidgetItem(str(payment[0]))
            cash_item.setTextAlignment(Qt.AlignCenter)
            card_item = QTableWidgetItem(str(payment[1]))
            card_item.setTextAlignment(Qt.AlignCenter)
            total_item = QTableWidgetItem(str(payment[2]))
            total_item.setTextAlignment(Qt.AlignCenter)
            time_item = QTableWidgetItem(payment[3])
            time_item.setTextAlignment(Qt.AlignCenter)
            date_item = QTableWidgetItem(payment[4])
            date_item.setTextAlignment(Qt.AlignCenter)

            self.payment_method_table.setItem(row, 0, cash_item)
            self.payment_method_table.setItem(row, 1, card_item)
            self.payment_method_table.setItem(row, 2, total_item)
            self.payment_method_table.setItem(row, 3, time_item)
            self.payment_method_table.setItem(row, 4, date_item)

    def calculate_totals(self):
        cash_total = 0
        card_total = 0
        total_total = 0

        for row in range(self.payment_method_table.rowCount()):
            cash_item = self.payment_method_table.item(row, 0)
            card_item = self.payment_method_table.item(row, 1)
            total_item = self.payment_method_table.item(row, 2)

            if cash_item is not None and cash_item.text() != "":
                cash_total += int(cash_item.text())
            if card_item is not None and card_item.text() != "":
                card_total += int(card_item.text())
            if total_item is not None and total_item.text() != "":
                total_total += int(total_item.text())

        self.cash_total_label.setText(str(cash_total))
        self.card_total_label.setText(str(card_total))
        self.total_total_label.setText(str(total_total))

    def current_time(self):
        curr_time = str(QTime.currentTime().toString(Qt.DefaultLocaleLongDate))
        curr_date = str(jdatetime.date.today())

        self.time_input.setText(curr_time)
        self.date_input.setText(curr_date)

    def clear_button(self):
        self.cash_input.clear()
        self.card_input.clear()
        self.time_input.clear()
        self.date_input.clear()

        self.payment_method_table.clearSelection()


class PlayNetWindowManual(QMainWindow):
    def __init__(self):
        super().__init__()

        self.manual_text = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.5;
                }
                
                h1 {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                
                h2 {
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }
                
                h3 {
                    font-size: 12px;
                    font-weight: bold;
                    margin-bottom: 6px;
                }
                
                p {
                    margin-bottom: 4px;
                }
            </style>
        </head>
        <body>
            <h1>Manual for PlayNet App</h1>
            <h2>1. Introduction</h2>
            <p>PlayNet is an application designed to manage invoices and track time for devices in a gaming center. This manual provides an overview of the app's features and instructions on how to use them effectively.</p>
            
            <h2>2. Getting Started</h2>
            <p>To start using the PlayNet app, follow these steps:</p>
            <ul>
                <li>Install the PlayNet app on your computer.</li>
                <li>Launch the PlayNet app by double-clicking the application icon.</li>
                <li>The main window of the app will appear on your screen.</li>
            </ul>
            
            <h2>3. Main Window</h2>
            <p>The main window of the PlayNet app is the central interface for accessing various features. It consists of a menu bar, a toolbar, and a tabbed layout.</p>
            
            <h3>3.1 Menu Bar</h3>
            <p>The menu bar is located at the top of the window and provides access to different options and actions. It contains the following menus:</p>
            <ul>
                <li>Help: This menu provides assistance and information about the app.</li>
                <li>About: Displays information about the app and its version.</li>
                <li>Manual: Opens this user manual.</li>
            </ul>
            
            <h3>3.2 Toolbar</h3>
            <p>The toolbar is located below the menu bar and contains buttons for quick access to frequently used features. The toolbar buttons are organized as follows:</p>
            <ul>
                <li>Invoice Window: Opens the invoice window for managing invoices.</li>
                <li>Daily Invoice Window: Opens the daily invoice window for viewing daily invoices.</li>
                <li>Debtor List: Opens the debtor list window to track outstanding payments.</li>
                <li>Payment Method: Opens the payment method window to manage different payment methods.</li>
            </ul>
            
            <h2>4. Tab Layout</h2>
            <p>The tab layout is located in the main area of the window and allows you to switch between different sections of the app. The PlayNet app consists of two tabs: "System A" and "Separate Invoice."</p>
            
            <h3>4.1 System A Tab</h3>
            <p>The "System A" tab provides functionality for managing devices, snacks, and generating invoices. It includes the following sections:</p>
            
            <h4>4.1.1 Device Section</h4>
            <p>The device section allows you to monitor and control device-related activities. It includes the following elements:</p>
            <ul>
                <li>Timer: Displays the current time.</li>
                <li>Start Time: Shows the start time of the timer.</li>
                <li>Stop Time: Shows the stop time of the timer.</li>
                <li>Start Timer Button: Starts the timer for a device.</li>
                <li>Stop Timer Button: Stops the timer for a device.</li>
                <li>Reset Timer Button: Resets the timer for a device.</li>
            </ul>
            
            <h4>4.1.2 Snack Section</h4>
            <p>The snack section enables you to manage snacks available at the gaming center. It includes the following elements:</p>
            <ul>
                <li>Name: Allows you to enter the name of a snack.</li>
                <li>Price: Allows you to enter the price of a snack.</li>
                <li>List: Displays a table with the list of snacks.</li>
                <li>Add Snack Button: Adds a snack to the snack list.</li>
                <li>Reset List Button: Resets the snack list.</li>
            </ul>
            
            <h4>4.1.3 Invoice Section</h4>
            <p>The invoice section allows you to calculate and manage invoices for a device. It includes the following elements:</p>
            <ul>
                <li>Device: Displays the name of the device.</li>
                <li>Hourly Rate: Allows you to enter the hourly rate for the device.</li>
                <li>Snack Invoice: Displays the total invoice amount for snacks.</li>
                <li>Device Invoice: Displays the total invoice amount for device usage.</li>
                <li>Total Invoice: Displays the overall total invoice amount.</li>
                <li>Invoice Time: Displays the time of the invoice.</li>
                <li>Invoice Date: Displays the date of the invoice.</li>
                <li>Calculate Invoice Button: Calculates the invoice for a device.</li>
                <li>Pay Invoice Button: Marks the invoice as paid.</li>
                <li>Reset Invoice Button: Resets the invoice details.</li>
            </ul>
            
            <h3>4.2 Separate Invoice Tab</h3>
            <p>The "Separate Invoice" tab provides functionality for managing device and snack invoices separately. It includes two sections:</p>
            
            <h4>4.2.1 Device Section</h4>
            <p>The device section allows you to manage device-related invoices separately. It includes the following elements:</p>
            <ul>
                <li>Invoice: Displays the invoice details for a device.</li>
                <li>Device: Displays the name of the device.</li>
                <li>Hourly Rate: Allows you to enter the hourly rate for the device.</li>
                <li>Start Time: Shows the start time of the device usage.</li>
                <li>Stop Time: Shows the stop time of the device usage.</li>
                <li>Total Time: Displays the total usage time for the device.</li>
                <li>Device Invoice: Displays the invoice amount for device usage.</li>
            </ul>
            
            <h4>4.2.2 Snack Section</h4>
            <p>The snack section allows you to manage snack-related invoices separately. It includes the following elements:</p>
            <ul>
                <li>Invoice: Displays the invoice details for snacks.</li>
                <li>Snack Name: Allows you to select a snack from the list.</li>
                <li>Quantity: Allows you to enter the quantity of the selected snack.</li>
                <li>Price: Displays the price of the selected snack.</li>
                <li>Total: Displays the total amount for the selected snack.</li>
                <li>Add Snack Button: Adds the selected snack to the invoice.</li>
                <li>Reset Invoice Button: Resets the snack invoice details.</li>
            </ul>
            
            <h2>5. Managing Invoices</h2>
            <h3>5.1 Creating an Invoice</h3>
            <p>To create an invoice in the PlayNet app, follow these steps:</p>
            <ol>
                <li>Navigate to the desired tab (System A or Separate Invoice) based on your preference.</li>
                <li>Enter the required information for devices and snacks.</li>
                <li>Click on the "Calculate Invoice" button to calculate the invoice amount.</li>
                <li>Review the invoice details, including device invoice and snack invoice.</li>
                <li>Click on the "Pay Invoice" button to mark the invoice as paid.</li>
            </ol>
            
            <h3>5.2 Managing Payments</h3>
            <p>To manage payments and track outstanding invoices, use the Debtor List window. Here's how:</p>
            <ol>
                <li>Open the Debtor List window by clicking on the corresponding button in the toolbar.</li>
                <li>The Debtor List window displays a table with the list of debtors and their outstanding payment amounts.</li>
                <li>You can sort the table by clicking on the column headers.</li>
                <li>To mark an invoice as paid, select the debtor and click on the "Mark as Paid" button.</li>
                <li>To delete a debtor from the list, select the debtor and click on the "Delete Debtor" button.</li>
            </ol>
            
            <h2>6. Additional Features</h2>
            
            <h3>6.1 Payment Methods</h3>
            <p>The Payment Method window allows you to manage different payment methods. Here's how to use it:</p>
            <ol>
                <li>Open the Payment Method window by clicking on the corresponding button in the toolbar.</li>
                <li>The Payment Method window displays a list of existing payment methods.</li>
                <li>To add a new payment method, click on the "Add Payment Method" button and enter the details.</li>
                <li>To edit or delete a payment method, select it from the list and click on the corresponding button.</li>
            </ol>
            
            <h2>7. Help and Support</h2>
            
            <p>If you need any assistance or have questions about using the PlayNet app, refer to Contact in help Menue.</p>
            
        </body>
        </html>
        """

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PlayNet Window Manual")
        self.setGeometry(800, 200, 800, 800)
        self.setWindowIcon(QIcon("manual-window.ico"))

        text_browser = QTextBrowser()
        text_browser.setHtml(self.manual_text)

        self.setCentralWidget(text_browser)


def main():
    elevate.elevate()
    program_status = ProgramStatus()
    app = QApplication([])
    app.setStyle("Fusion")

    if not program_status.is_running():
        program_status.start_program()

        main_window = MainWindow()
        app.setApplicationVersion(main_window.app_version)

        main_window.showNormal()
        main_window.activateWindow()

        app.exec_()

    else:
        message = QWidget()
        QMessageBox.warning(message, "Error", "The program is already running.")


if __name__ == "__main__":
    main()
