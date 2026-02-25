"""Dialog prompting the user to set a co-op password before launch."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QLineEdit)
from PySide6.QtCore import Qt


class CoopPasswordDialog(QDialog):
    def __init__(self, game_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Co-op Password")
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumWidth(400)
        self.password = ""
        self._build(game_name)

    def _build(self, game_name: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Co-op Password Required")
        title.setStyleSheet("font-size:14px;font-weight:700;color:#e0e0ec;")
        layout.addWidget(title)

        msg = QLabel(
            f"{game_name} requires a co-op password to connect with other players.\n"
            "Set a password that your friends will also use."
        )
        msg.setWordWrap(True)
        msg.setStyleSheet("color:#8888aa;font-size:12px;line-height:1.5;")
        layout.addWidget(msg)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter co-op password")
        self._input.setFixedHeight(34)
        self._input.returnPressed.connect(self._on_save_launch)
        layout.addWidget(self._input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("sidebar_mgmt_btn")
        btn_cancel.setFixedWidth(90)
        btn_cancel.clicked.connect(self.reject)

        self._btn_save = QPushButton("Save && Launch")
        self._btn_save.setObjectName("btn_accent")
        self._btn_save.setFixedWidth(130)
        self._btn_save.clicked.connect(self._on_save_launch)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_save)
        layout.addLayout(btn_row)

        self._input.setFocus()

    def _on_save_launch(self):
        text = self._input.text().strip()
        if not text:
            self._input.setStyleSheet("border:1px solid #e74c3c;")
            return
        self.password = text
        self.accept()
