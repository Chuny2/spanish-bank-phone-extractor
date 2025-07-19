# Spanish Bank Phone Extractor

A modern Python application for extracting phone numbers from Spanish bank IBAN data. Features both GUI and CLI interfaces with support for large datasets and asynchronous processing.

## Features

- **Modern PyQt6 GUI**: Clean, responsive interface with dark theme
- **Asynchronous Processing**: Handles large datasets without freezing the UI
- **Multiple File Formats**: Supports Excel (.xlsx, .xls), CSV, and text files
- **Spanish Bank Registry**: Complete database of Spanish banks with search functionality
- **Progress Tracking**: Real-time progress bars for large file operations
- **Export Results**: Export extracted phone numbers to Excel or text files
- **Thread-Safe**: Proper async processing with cancellation support

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt6
- openpyxl

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyQt6>=6.4.0 openpyxl>=3.1.0
```

## Usage

### GUI Application
```bash
python main.py
```

### Features
1. **Select Bank**: Choose from major Spanish banks or search the complete registry
2. **Load Data**: Import Excel, CSV, or text files with IBAN data
3. **Extract Phone Numbers**: Automatically extract and validate Spanish phone numbers
4. **Export Results**: Save results to Excel or text format

### Supported Phone Number Formats
- International format: `+34 123456789`
- Spanish mobile: `612345678`, `712345678`
- Formatted numbers: `612 345 67 89`

### Supported IBAN Formats
- Spanish IBAN: `ES91 0049 0001 2345 6789 0123`
- Various spacing formats supported

## Project Structure

```
Phone_Bank_extractor/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── lista-psri-es.csv              # Spanish bank registry data
└── src/
    └── spanish_bank_extractor/
        ├── __init__.py             # Package initialization
        ├── core/
        │   ├── extractor.py        # Phone number extraction logic
        │   └── bank_registry.py    # Bank data management
        └── gui/
            └── app.py              # PyQt6 GUI implementation
```

## Performance Features

- **Asynchronous File Loading**: Large files load without blocking the UI
- **Chunked Processing**: Memory-efficient processing of large datasets
- **Progress Feedback**: Real-time progress updates during operations
- **Cancellation Support**: Cancel long-running operations
- **Optimized UI**: Responsive interface with minimal overhead

## Development

### Running Tests
The application includes comprehensive async processing tests. To run performance tests:

```bash
# Create a test environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application
python main.py
```

### Code Quality
- Clean, well-documented code
- Type hints throughout
- Comprehensive error handling
- Thread-safe operations

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
