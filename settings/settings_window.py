from PyQt6.QtCore import pyqtSignal
from .user_config import UserConfig
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QIntValidator,
)


class SettingDialog(QDialog):
    saved = pyqtSignal()
    default_restored = pyqtSignal()

    def __init__(self, user_config: UserConfig):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form Fields
        form = QFormLayout()
        layout.addLayout(form)

        self.calendar_name_txt = QLineEdit(user_config.calendar_name)
        form.addRow("Calendar Name:", self.calendar_name_txt)

        self.event_name_txt = QLineEdit(user_config.event_name)
        form.addRow("Event Name:", self.event_name_txt)

        # https://google-calendar-simple-api.readthedocs.io/en/latest/colors.html#event-colors
        self.color_id_cbx = QComboBox()
        self.color_id_cbx.addItem("Lavender", 1)
        self.color_id_cbx.addItem("Sage", 2)
        self.color_id_cbx.addItem("Grape", 3)
        self.color_id_cbx.addItem("Flamingo", 4)
        self.color_id_cbx.addItem("Banana", 5)
        self.color_id_cbx.addItem("Tangerine", 6)
        self.color_id_cbx.addItem("Peacock", 7)
        self.color_id_cbx.addItem("Graphite", 8)
        self.color_id_cbx.addItem("Blueberry", 9)
        self.color_id_cbx.addItem("Basil", 10)
        self.color_id_cbx.addItem("Tomato", 11)
        self.color_id_cbx.setCurrentIndex(user_config.event_color_id)
        form.addRow("Color:", self.color_id_cbx)

        self.min_time_txt = QLineEdit(str(user_config.min_event_time))
        self.min_time_txt.setValidator(QIntValidator())
        form.addRow("Min time (seconds):", self.min_time_txt)

        self.client_secret_txt = QLineEdit(user_config.client_secret)
        form.addRow("Client Secret:", self.client_secret_txt)

        # Buttons
        submit_button_layout = QHBoxLayout()
        layout.addLayout(submit_button_layout)

        restoreBtn = QPushButton("Restore Default")
        restoreBtn.clicked.connect(self.handle_restore_default)
        submit_button_layout.addWidget(restoreBtn)
        submit_button_layout.addStretch()

        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.close)
        submit_button_layout.addWidget(cancelBtn)

        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.handle_save)
        saveBtn.setDefault(True)
        submit_button_layout.addWidget(saveBtn)

    def handle_save(self) -> None:
        self.saved.emit()
        self.close()

    def handle_restore_default(self) -> None:
        self.default_restored.emit()
        self.close()
