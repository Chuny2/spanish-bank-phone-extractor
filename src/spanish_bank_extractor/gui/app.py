#!/usr/bin/env python3
"""
Spanish Bank Phone Number Extractor - Modern PyQt6 GUI

This is the main GUI entrypoint for the application.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QLabel, QFileDialog,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QProgressBar, QSplitter, QFrame, QScrollArea,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap

from ..core.extractor import SpanishBankExtractor
from ..core.bank_registry import BankRegistry


class ModernButton(QPushButton):
    """Custom modern button with styling."""
    
    def __init__(self, text: str, primary: bool = False):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f3f2f1;
                    color: #323130;
                    border: 1px solid #d2d0ce;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #edebe9;
                    border-color: #c7c6c4;
                }
                QPushButton:pressed {
                    background-color: #e1dfdd;
                }
                QPushButton:disabled {
                    background-color: #f3f2f1;
                    color: #a19f9d;
                    border-color: #edebe9;
                }
            """)


class SpanishBankGUI(QMainWindow):
    """Main GUI window for Spanish Bank Phone Extractor."""
    
    def __init__(self):
        super().__init__()
        self.extractor = SpanishBankExtractor()
        self.init_ui()
        self.setup_styles()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Spanish Bank Phone Extractor")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        # Status bar will be created automatically when needed
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Segoe UI", 10))
        
        # Add tabs
        self.tab_widget.addTab(self.create_extraction_tab(), "Phone Extraction")
        self.tab_widget.addTab(self.create_bank_info_tab(), "Bank Information")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_header(self) -> QWidget:
        """Create the header section."""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("Spanish Bank Phone Number Extractor")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setProperty("class", "title")
        title_label.setStyleSheet("margin-bottom: 8px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Extract phone numbers from Spanish bank IBAN data")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setProperty("class", "subtitle")
        subtitle_label.setStyleSheet("margin-bottom: 16px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        return header_widget
    
    def create_extraction_tab(self) -> QWidget:
        """Create the phone extraction tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Bank selection section
        bank_section = self.create_bank_selection_section()
        layout.addWidget(bank_section)
        
        # Input section
        input_section = self.create_input_section()
        layout.addWidget(input_section)
        
        # Results section
        self.results_section = self.create_results_section()
        layout.addWidget(self.results_section)
        
        return tab_widget
    
    def create_bank_selection_section(self) -> QWidget:
        """Create the bank selection section."""
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)
        layout.setSpacing(12)
        
        # Bank selection controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        # Major banks dropdown
        self.bank_combo = QComboBox()
        self.bank_combo.setMinimumHeight(40)
        self.bank_combo.setMinimumWidth(300)
        self.bank_combo.setFont(QFont("Segoe UI", 10))
        
        # Populate major banks
        major_banks = self.extractor.get_major_banks()
        self.bank_combo.addItem("Select a bank...", None)
        for iban_prefix, display_name in major_banks:
            self.bank_combo.addItem(display_name, iban_prefix)
        
        # Search banks button
        self.search_button = ModernButton("Search All Banks", primary=False)
        self.search_button.clicked.connect(self.show_bank_search_dialog)
        
        controls_layout.addWidget(QLabel("Bank:"))
        controls_layout.addWidget(self.bank_combo)
        controls_layout.addWidget(self.search_button)
        controls_layout.addStretch()
        
        # Selected bank info
        self.bank_info_label = QLabel()
        self.bank_info_label.setFont(QFont("Segoe UI", 10))
        self.bank_info_label.setProperty("class", "info")
        self.bank_info_label.setVisible(False)
        
        # Connect signals
        self.bank_combo.currentIndexChanged.connect(self.on_bank_selected)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.bank_info_label)
        
        return section_widget
    
    def create_input_section(self) -> QWidget:
        """Create the input section."""
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)
        layout.setSpacing(12)
        
        # Input controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        # File input button
        self.file_button = ModernButton("Load File", primary=True)
        self.file_button.clicked.connect(self.load_file)
        
        # Clear button
        self.clear_button = ModernButton("Clear", primary=False)
        self.clear_button.clicked.connect(self.clear_input)
        
        controls_layout.addWidget(self.file_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()
        
        # Input text area
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont("Consolas", 10))
        self.input_text.setStyleSheet("line-height: 1.4; padding: 12px;")
        self.input_text.setPlaceholderText("Paste your data with Spanish IBANs and phone numbers here...")
        
        # Process button
        self.process_button = ModernButton("Extract Phone Numbers", primary=True)
        self.process_button.clicked.connect(self.process_input)
        self.process_button.setEnabled(False)
        
        # Progress bar for large files
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: #2d2d30;
                color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
        """)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.input_text)
        layout.addWidget(self.process_button)
        
        return section_widget
    
    def create_results_section(self) -> QWidget:
        """Create the results section."""
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)
        layout.setSpacing(12)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Line", "Text", "Phone Numbers"])
        header = self.results_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Results controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        # Export button
        self.export_button = ModernButton("Export Results", primary=False)
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        
        # Clear results button
        self.clear_results_button = ModernButton("Clear Results", primary=False)
        self.clear_results_button.clicked.connect(self.clear_results)
        self.clear_results_button.setEnabled(False)
        
        # Results summary
        self.results_summary = QLabel()
        self.results_summary.setFont(QFont("Segoe UI", 10))
        self.results_summary.setProperty("class", "info")
        
        controls_layout.addWidget(self.export_button)
        controls_layout.addWidget(self.clear_results_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.results_summary)
        
        layout.addWidget(self.results_table)
        layout.addLayout(controls_layout)
        
        return section_widget
    
    def create_bank_info_tab(self) -> QWidget:
        """Create the bank information tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Spanish Bank Registry")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setProperty("class", "title")
        title_label.setStyleSheet("margin-bottom: 16px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Instructions
        instructions_label = QLabel("Double-click a bank to select it")
        instructions_label.setFont(QFont("Segoe UI", 10))
        instructions_label.setProperty("class", "subtitle")
        instructions_label.setStyleSheet("margin-bottom: 16px; color: #605e5c;")
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        self.bank_search_input = QTextEdit()
        self.bank_search_input.setMaximumHeight(60)
        self.bank_search_input.setFont(QFont("Segoe UI", 10))
        self.bank_search_input.setPlaceholderText("Search banks by name...")
        
        self.search_banks_button = ModernButton("Search", primary=True)
        self.search_banks_button.clicked.connect(self.search_banks)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.bank_search_input)
        search_layout.addWidget(self.search_banks_button)
        
        # Banks table
        self.banks_table = QTableWidget()
        self.banks_table.setObjectName("banks_table")
        self.banks_table.setColumnCount(4)
        self.banks_table.setHorizontalHeaderLabels(["Entity Code", "Bank Name", "IBAN Prefix", "Address"])
        bank_header = self.banks_table.horizontalHeader()
        if bank_header:
            bank_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            bank_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            bank_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            bank_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Enable double-click to select bank
        self.banks_table.itemDoubleClicked.connect(self.on_bank_table_double_clicked)
        
        # Load all banks button
        self.load_all_banks_button = ModernButton("Load All Banks", primary=True)
        self.load_all_banks_button.clicked.connect(self.load_all_banks)
        
        layout.addWidget(title_label)
        layout.addWidget(instructions_label)
        layout.addLayout(search_layout)
        layout.addWidget(self.banks_table)
        layout.addWidget(self.load_all_banks_button)
        
        return tab_widget
    
    def setup_styles(self):
        """Setup application-wide styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #ffffff;
                min-width: 800px;
                min-height: 600px;
            }
            
            QWidget {
                color: #ffffff;
                background-color: #1e1e1e;
            }
            
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2d2d30;
                margin-top: -1px;
            }
            
            QTabBar::tab {
                background-color: #3e3e42;
                border: 1px solid #404040;
                border-bottom: none;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                color: #cccccc;
            }
            
            QTabBar::tab:selected {
                background-color: #2d2d30;
                border-bottom: 1px solid #2d2d30;
                font-weight: 600;
                color: #ffffff;
            }
            
            QTabBar::tab:hover {
                background-color: #505050;
                color: #ffffff;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            QTextEdit, QLineEdit {
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
                background-color: #2d2d30;
                color: #ffffff;
                selection-background-color: #0078d4;
                selection-color: white;
                min-height: 100px;
            }
            
            QTextEdit:focus, QLineEdit:focus {
                border-color: #0078d4;
                outline: none;
                color: #ffffff;
            }
            
            QComboBox {
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #2d2d30;
                color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox:focus {
                border-color: #0078d4;
                color: #ffffff;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cccccc;
                margin-right: 8px;
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid #404040;
                background-color: #2d2d30;
                color: #ffffff;
                selection-background-color: #0078d4;
                selection-color: white;
                border-radius: 4px;
            }
            
            QComboBox QAbstractItemView::item {
                color: #ffffff;
                padding: 8px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: white;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #505050;
                color: #ffffff;
            }
            
            QTableWidget {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2d2d30;
                color: #ffffff;
                gridline-color: #404040;
                alternate-background-color: #252526;
                min-height: 200px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
                color: #ffffff;
                background-color: transparent;
            }
            
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            
            QTableWidget::item:alternate {
                background-color: #252526;
                color: #ffffff;
            }
            
            /* Make bank table rows look clickable */
            QTableWidget#banks_table::item:hover {
                background-color: #3e3e42;
                color: #ffffff;
            }
            
            QTableWidget#banks_table::item:selected {
                background-color: #0078d4;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #3e3e42;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #404040;
                font-weight: 600;
                color: #ffffff;
            }
            
            QScrollBar:vertical {
                background-color: #3e3e42;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #505050;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
            
            QScrollBar:horizontal {
                background-color: #3e3e42;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #505050;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #707070;
            }
            
            /* Ensure all text elements have proper colors */
            QLabel, QTextEdit, QLineEdit, QComboBox, QTableWidget, QHeaderView {
                color: #ffffff;
            }
            
            /* Specific styling for different text elements */
            QLabel[class="title"] {
                color: #ffffff;
                font-weight: bold;
            }
            
            QLabel[class="subtitle"] {
                color: #cccccc;
            }
            
            QLabel[class="info"] {
                color: #cccccc;
                background-color: #3e3e42;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
        """)
    
    def on_bank_selected(self, index: int):
        """Handle bank selection."""
        if index > 0:
            iban_prefix = self.bank_combo.currentData()
            if iban_prefix:
                # Always use normalized prefix for extractor
                normalized_prefix = self.extractor.normalize_iban_prefix(iban_prefix)
                bank_info = self.extractor.get_bank_info(normalized_prefix)
                if bank_info:
                    self.bank_info_label.setText(
                        f"Selected: {bank_info['name']} ({bank_info['entity_code']})"
                    )
                    self.bank_info_label.setVisible(True)
                    self.process_button.setEnabled(True)
                    self.selected_bank_prefix = normalized_prefix  # Store for use in process_input
                else:
                    self.bank_info_label.setVisible(False)
                    self.process_button.setEnabled(False)
                    self.selected_bank_prefix = None
            else:
                self.bank_info_label.setVisible(False)
                self.process_button.setEnabled(False)
                self.selected_bank_prefix = None
        else:
            self.bank_info_label.setVisible(False)
            self.process_button.setEnabled(False)
            self.selected_bank_prefix = None
    
    def show_bank_search_dialog(self):
        """Show bank search dialog."""
        self.tab_widget.setCurrentIndex(1)
        self.load_all_banks()
    
    def load_file(self):
        """Load file into input text area."""
        # Create file dialog with optimized settings
        file_dialog = QFileDialog(self, "Select File", "")
        file_dialog.setNameFilter("Text Files (*.txt);;CSV Files (*.csv);;All Files (*)")
        
        # Disable preview and icon generation to improve performance
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setOption(QFileDialog.Option.DontResolveSymlinks, True)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            if file_path:
                try:
                    # Check file size before loading
                    file_size = os.path.getsize(file_path)
                    if file_size > 10485760:  # 10MB
                        reply = QMessageBox.question(
                            self, "Large File", 
                            f"File size is {file_size / 1024 / 1024:.1f}MB. This may take a while to load. Continue?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            return
                    
                    # Show loading cursor
                    self.setCursor(Qt.CursorShape.WaitCursor)
                    
                    # Read file with progress indication for large files
                    if file_size > 1024000:  # 1MB
                        # For large files, read in chunks with progress
                        content = ""
                        with open(file_path, 'r', encoding='utf-8-sig') as file:
                            chunk_size = 8192  # 8KB chunks
                            total_chunks = file_size // chunk_size + 1
                            chunk_count = 0
                            
                            while True:
                                chunk = file.read(chunk_size)
                                if not chunk:
                                    break
                                content += chunk
                                chunk_count += 1
                                
                                # Update progress every 100 chunks
                                if chunk_count % 100 == 0:
                                    QApplication.processEvents()  # Keep UI responsive
                    else:
                        # For smaller files, read all at once
                        with open(file_path, 'r', encoding='utf-8-sig') as file:
                            content = file.read()
                    
                    self.input_text.setPlainText(content)
                    
                except UnicodeDecodeError:
                    # Try with different encoding if UTF-8 fails
                    try:
                        with open(file_path, 'r', encoding='latin-1') as file:
                            content = file.read()
                        self.input_text.setPlainText(content)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not read file with any encoding: {e}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not read file: {e}")
                finally:
                    # Restore cursor
                    self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def clear_input(self):
        """Clear input text area."""
        self.input_text.clear()
    
    def process_input(self):
        """Process input text to extract phone numbers."""
        iban_prefix = getattr(self, 'selected_bank_prefix', None)
        if not iban_prefix:
            QMessageBox.warning(self, "Warning", "Please select a bank first.")
            return
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Please enter some text to process.")
            return
        # Show processing cursor for large files
        if len(text) > 10000:  # More than 10KB
            self.setCursor(Qt.CursorShape.WaitCursor)
        try:
            # Process the text using the extractor
            results = self.extractor.process_text(iban_prefix, text)
            self.display_results(results)
        finally:
            # Restore cursor
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def display_results(self, results):
        """Display results in the table."""
        # Block signals for better performance
        self.results_table.blockSignals(True)
        
        self.results_table.setRowCount(len(results))
        
        total_phones = 0
        for i, result in enumerate(results):
            # Line number
            line_item = QTableWidgetItem(str(result['line_number']))
            line_item.setFlags(line_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.results_table.setItem(i, 0, line_item)
            
            # Text
            text_item = QTableWidgetItem(result['text'])
            text_item.setFlags(text_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.results_table.setItem(i, 1, text_item)
            
            # Phone numbers
            phones_text = ', '.join(result['phone_numbers'])
            phones_item = QTableWidgetItem(phones_text)
            phones_item.setFlags(phones_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.results_table.setItem(i, 2, phones_item)
            
            total_phones += len(result['phone_numbers'])
        
        # Unblock signals
        self.results_table.blockSignals(False)
        
        # Update summary
        self.results_summary.setText(f"Found {len(results)} lines with {total_phones} phone numbers")
        
        # Enable buttons
        self.export_button.setEnabled(len(results) > 0)
        self.clear_results_button.setEnabled(len(results) > 0)
    
    def export_results(self):
        """Export results to a file."""
        # Create file dialog with optimized settings
        file_dialog = QFileDialog(self, "Save Results", "extracted_phones.txt")
        file_dialog.setNameFilter("Text Files (*.txt);;CSV Files (*.csv)")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        
        # Disable preview and icon generation to improve performance
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setOption(QFileDialog.Option.DontResolveSymlinks, True)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            if file_path:
                try:
                    # Show saving cursor
                    self.setCursor(Qt.CursorShape.WaitCursor)
                    
                    with open(file_path, 'w', encoding='utf-8') as file:
                        for row in range(self.results_table.rowCount()):
                            phone_item = self.results_table.item(row, 2)
                            if phone_item:
                                phones = phone_item.text()
                                # Split phone numbers and write each one on a separate line
                                phone_list = [phone.strip() for phone in phones.split(',')]
                                for phone in phone_list:
                                    if phone:  # Only write non-empty phone numbers
                                        file.write(f"{phone}\n")
                    
                    QMessageBox.information(self, "Success", f"Phone numbers exported to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not export results: {e}")
                finally:
                    # Restore cursor
                    self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def clear_results(self):
        """Clear results table."""
        self.results_table.setRowCount(0)
        self.results_summary.clear()
        self.export_button.setEnabled(False)
        self.clear_results_button.setEnabled(False)
    
    def search_banks(self):
        """Search banks by name."""
        search_term = self.bank_search_input.toPlainText().strip()
        if not search_term:
            self.load_all_banks()
            return
        
        matches = self.extractor.search_banks(search_term)
        self.display_banks(matches)
    
    def load_all_banks(self):
        """Load all banks into the table."""
        all_banks = self.extractor.get_all_banks()
        self.display_banks(all_banks)
    
    def on_bank_table_double_clicked(self, item):
        """Handle double-click on bank table item."""
        row = item.row()
        iban_prefix_item = self.banks_table.item(row, 2)  # IBAN Prefix column
        if iban_prefix_item:
            iban_prefix = iban_prefix_item.text()
            self.select_bank_from_table(iban_prefix)
    
    def select_bank_from_table(self, iban_prefix):
        """Select a bank from the table and switch to extraction tab."""
        # Find the bank in the dropdown and select it
        found = False
        for i in range(self.bank_combo.count()):
            if self.bank_combo.itemData(i) == iban_prefix:
                self.bank_combo.setCurrentIndex(i)
                found = True
                break
        
        # If found in dropdown, trigger the selection event manually
        if found:
            # Manually trigger the bank selection logic
            self.on_bank_selected(self.bank_combo.currentIndex())
        
        # Always manually set the bank selection state to ensure it works
        normalized_prefix = self.extractor.normalize_iban_prefix(iban_prefix)
        bank_info = self.extractor.get_bank_info(normalized_prefix)
        if bank_info:
            self.selected_bank_prefix = normalized_prefix
            self.bank_info_label.setText(
                f"Selected: {bank_info['name']} ({bank_info['entity_code']})"
            )
            self.bank_info_label.setVisible(True)
            self.process_button.setEnabled(True)
        
        # Switch to the extraction tab
        self.tab_widget.setCurrentIndex(0)
    
    def display_banks(self, banks):
        """Display banks in the table."""
        self.banks_table.setRowCount(len(banks))
        
        for i, bank_data in enumerate(banks):
            if len(bank_data) == 4:
                iban_prefix, name, entity_code, address = bank_data
            else:
                iban_prefix, name = bank_data
                entity_code = iban_prefix[2:] if len(iban_prefix) >= 6 else iban_prefix
                bank_info = self.extractor.get_bank_info(iban_prefix)
                address = bank_info['address'] if bank_info else ""
            
            # Entity code
            entity_item = QTableWidgetItem(entity_code)
            entity_item.setFlags(entity_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.banks_table.setItem(i, 0, entity_item)
            
            # Bank name
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.banks_table.setItem(i, 1, name_item)
            
            # IBAN prefix
            prefix_item = QTableWidgetItem(iban_prefix)
            prefix_item.setFlags(prefix_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.banks_table.setItem(i, 2, prefix_item)
            
            # Address
            address_item = QTableWidgetItem(address)
            address_item.setFlags(address_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.banks_table.setItem(i, 3, address_item)


def main():
    """Main function to run the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Spanish Bank Phone Extractor")
    app.setApplicationVersion("1.0")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Ensure proper color scheme handling
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d30"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#252526"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2d2d30"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#3e3e42"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#0078d4"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d4"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
    app.setPalette(palette)
    
    # Create and show the main window
    window = SpanishBankGUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 