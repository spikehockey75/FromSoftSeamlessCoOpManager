"""
ME3 update dialog — downloads and installs the latest ME3 version.
"""

import threading
import queue as _queue
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QProgressBar, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from app.core.me3_service import download_and_install_me3
from app.config.config_manager import ConfigManager


class ME3UpdateDialog(QDialog):
    """Dialog to update ME3 to the latest version."""

    def __init__(self, config: ConfigManager, latest_ver: str, parent=None):
        super().__init__(parent)
        self._config = config
        self._latest_ver = latest_ver
        self._pending: _queue.SimpleQueue = _queue.SimpleQueue()

        self.setWindowTitle("Update Mod Engine 3")
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumWidth(480)
        self.setMinimumHeight(240)
        self._build()

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_timer.start(100)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Icon + title row
        title_row = QHBoxLayout()
        icon_lbl = QLabel("\uE895")  # Download icon
        icon_lbl.setFont(QFont("Segoe MDL2 Assets", 24))
        icon_lbl.setStyleSheet("color:#e0e0ec;")
        title_row.addWidget(icon_lbl)

        title = QLabel("ME3 Update Available")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#e0e0ec;")
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # Description
        desc = QLabel(
            f"A new version of Mod Engine 3 ({self._latest_ver}) is available.\n\n"
            "Click Update to download and install it automatically."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size:12px;color:#a0a0c0;line-height:1.5;")
        layout.addWidget(desc)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#2a2a4a;")
        layout.addWidget(sep)

        # Status label
        self._status_lbl = QLabel("Ready to update")
        self._status_lbl.setStyleSheet("font-size:11px;color:#8888aa;")
        layout.addWidget(self._status_lbl)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(6)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._cancel_btn = QPushButton("Not Now")
        self._cancel_btn.setObjectName("sidebar_mgmt_btn")
        self._cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._cancel_btn)

        self._update_btn = QPushButton("  Update ME3")
        self._update_btn.setObjectName("btn_accent")
        self._update_btn.setFixedHeight(36)
        self._update_btn.setFixedWidth(160)
        self._update_btn.clicked.connect(self._on_update)
        btn_row.addWidget(self._update_btn)

        layout.addLayout(btn_row)

    def _on_update(self):
        self._update_btn.setEnabled(False)
        self._cancel_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._status_lbl.setText("Starting download...")

        pending = self._pending

        def _work():
            def _cb(msg, pct):
                pending.put(("progress", pct, msg))
            result = download_and_install_me3(progress_callback=_cb)
            pending.put(("done", result))

        threading.Thread(target=_work, daemon=True).start()

    def _poll(self):
        try:
            while True:
                item = self._pending.get_nowait()
                tag = item[0]
                if tag == "progress":
                    _, pct, msg = item
                    self._progress.setValue(pct)
                    self._status_lbl.setText(msg)
                elif tag == "done":
                    _, result = item
                    self._on_done(result)
        except _queue.Empty:
            pass

    def _on_done(self, result: dict):
        self._poll_timer.stop()
        if result.get("success"):
            self._progress.setValue(100)
            self._status_lbl.setText("ME3 updated successfully!")
            self._status_lbl.setStyleSheet("font-size:11px;color:#4ecca3;font-weight:600;")
            if result.get("path"):
                self._config.set_me3_path(result["path"])
            QTimer.singleShot(800, self.accept)
        else:
            self._progress.setVisible(False)
            self._status_lbl.setText(f"Update failed: {result.get('message', 'Unknown error')}")
            self._status_lbl.setStyleSheet("font-size:11px;color:#e74c3c;")
            self._update_btn.setEnabled(True)
            self._cancel_btn.setEnabled(True)
            self._update_btn.setText("  Retry")
