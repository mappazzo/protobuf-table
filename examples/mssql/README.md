# MSSQL Timeseries Data Extractor

A simple Python script for extracting timeseries data from Microsoft SQL Server databases. This tool provides an easy-to-use interface for connecting to MSSQL databases, querying timeseries data, and exporting results to both CSV and compressed protobuf formats.

## Features

- **Simple Configuration**: JSON-based configuration for database connections
- **Flexible Queries**: Extract data with custom time ranges, tables, and columns
- **Error Handling**: Comprehensive error handling and logging
- **Multiple Export Formats**: CSV export and compressed protobuf-table format
- **Data Compression**: Efficient binary serialization with timestamp delta encoding
- **Pandas Integration**: Returns data as pandas DataFrames for easy analysis
- **Type Safety**: Uses Python type hints for better code reliability

## Requirements

- Python 3.7+
- Microsoft SQL Server ODBC Driver
- Required Python packages (see requirements.txt)

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MSSQL ODBC Driver:**
   - **Windows**: Download and install "ODBC Driver 17 for SQL Server" from Microsoft
   - **Linux**: Follow Microsoft's instructions for your distribution
   - **macOS**: Use Homebrew: `brew install msodbcsql17`

4. **Create configuration file:**
   ```bash
   cp config.json.template config.json
   ```
   Then edit `config.json` with your database details.

## Configuration

Edit the `config.json` file with your database connection details:

```json
{
  "database": {
    "server": "your_server_name_or_ip",
    "database": "your_database_name", 
    "username": "your_username",
    "password": "your_password",
    "driver": "ODBC Driver 17 for SQL Server"
  },
  "query": {
    "table": "your_timeseries_table_name",
    "timestamp_column": "timestamp",
    "value_columns": ["value1", "value2", "temperature", "pressure"],
    "default_hours_back": 24
  }
}
```

### Configuration Parameters

**Database Section:**
- `server`: SQL Server hostname or IP address
- `database`: Database name
- `username`: Database username
- `password`: Database password
- `driver`: ODBC driver name (usually "ODBC Driver 17 for SQL Server")

**Query Section:**
- `table`: Default table name for timeseries data
- `timestamp_column`: Name of the timestamp/datetime column
- `value_columns`: List of data columns to extract
- `default_hours_back`: Default time range in hours (when no time range specified)

## Usage

### Basic Usage

Run the main script to extract the last 24 hours of data:

```bash
python extract_timeseries.py
```

### Programmatic Usage

```python
from extract_timeseries import MSSQLTimeseriesExtractor
from datetime import datetime, timedelta

# Initialize extractor
extractor = MSSQLTimeseriesExtractor()

# Connect to database
if extractor.connect():
    # Extract last 24 hours (default)
    df = extractor.extract_timeseries_data()
    
    # Extract custom time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    df = extractor.extract_timeseries_data(start_time=start_time, end_time=end_time)
    
    # Extract specific columns
    df = extractor.extract_timeseries_data(
        value_columns=['temperature', 'pressure'],
        table_name='sensor_readings'
    )
    
    # Save to CSV
    csv_filename = extractor.save_to_csv(df, 'my_data.csv')
    
    # Save to compressed protobuf format
    pb_filename = extractor.save_to_protobuf(df, 'my_data.pb')
    
    # Always disconnect when done
    extractor.disconnect()
```

### Advanced Examples

See `example_usage.py` for comprehensive examples including:
- Basic data extraction
- Custom time ranges
- Specific column selection
- Data analysis and statistics

Run the examples:
```bash
python example_usage.py
```

## API Reference

### MSSQLTimeseriesExtractor Class

#### Methods

**`__init__(config_file='config.json')`**
- Initialize the extractor with configuration file

**`connect() -> bool`**
- Establish database connection
- Returns: True if successful, False otherwise

**`disconnect()`**
- Close database connection

**`extract_timeseries_data(start_time=None, end_time=None, table_name=None, timestamp_column=None, value_columns=None) -> pd.DataFrame`**
- Extract timeseries data from database
- Parameters:
  - `start_time`: Start datetime (optional)
  - `end_time`: End datetime (optional)
  - `table_name`: Table name (optional, uses config default)
  - `timestamp_column`: Timestamp column name (optional, uses config default)
  - `value_columns`: List of value columns (optional, uses config default)
- Returns: pandas DataFrame with extracted data

**`save_to_csv(df, filename=None) -> str`**
- Save DataFrame to CSV file
- Parameters:
  - `df`: pandas DataFrame to save
  - `filename`: Output filename (optional, auto-generated if not provided)
- Returns: Filename of saved file

**`save_to_protobuf(df, filename=None) -> str`**
- Save DataFrame to protobuf-table format for efficient storage
- Uses pb_table library for binary compression with timestamp delta encoding
- Parameters:
  - `df`: pandas DataFrame to save
  - `filename`: Output filename (optional, auto-generated if not provided)
- Returns: Filename of saved protobuf file
- Note: Timestamps are converted to Unix timestamps and compressed using sequence transforms

## Database Schema Requirements

Your timeseries table should have:
- A timestamp/datetime column (any name, specified in config)
- One or more numeric value columns
- Proper indexing on the timestamp column for performance

Example table structure:
```sql
CREATE TABLE timeseries_data (
    timestamp DATETIME2 NOT NULL,
    temperature FLOAT,
    pressure FLOAT,
    humidity FLOAT,
    INDEX IX_timestamp (timestamp)
);
```

## Error Handling

The script includes comprehensive error handling for:
- Database connection failures
- Invalid configuration files
- SQL query errors
- Missing tables or columns
- Network timeouts

All errors are logged with timestamps and detailed messages.

## Output Files

- **CSV files**: Timestamped data exports (e.g., `timeseries_data_20231215_143022.csv`)
- **Protobuf files**: Compressed binary data exports (e.g., `timeseries_data_20231215_143022.pb`)
- **Log messages**: Console output with timestamps and log levels

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify server name, database name, and credentials
   - Check if SQL Server allows remote connections
   - Ensure ODBC driver is installed correctly

2. **Driver Not Found**
   - Install "ODBC Driver 17 for SQL Server"
   - Update driver name in config.json if using different version

3. **Table/Column Not Found**
   - Verify table name and column names in config.json
   - Check database permissions for the user account

4. **No Data Returned**
   - Check if data exists in the specified time range
   - Verify timestamp column format and timezone
   - Review WHERE clause conditions

### Debug Mode

Enable debug logging by modifying the logging level in the script:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## License

This project is provided as-is for educational and practical use.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.
