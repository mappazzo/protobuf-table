#!/usr/bin/env python3
"""
Simple Python script to extract timeseries data from MSSQL database.
Enhanced with protobuf-table compression for efficient data serialization.
"""

import pyodbc
import pandas as pd
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# Add parent directory to path to import pb_table
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'python'))
import pb_table

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MSSQLTimeseriesExtractor:
    """Class to handle MSSQL database connections and timeseries data extraction."""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the extractor with database configuration."""
        self.connection = None
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load database configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using default configuration.")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration template."""
        return {
            "database": {
                "server": "localhost",
                "database": "your_database_name",
                "username": "your_username",
                "password": "your_password",
                "driver": "ODBC Driver 17 for SQL Server"
            },
            "query": {
                "table": "your_timeseries_table",
                "timestamp_column": "timestamp",
                "value_columns": ["value"],
                "default_hours_back": 24
            }
        }
    
    def connect(self) -> bool:
        """Establish connection to MSSQL database."""
        try:
            db_config = self.config['database']
            connection_string = (
                f"DRIVER={{{db_config['driver']}}};"
                f"SERVER={db_config['server']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                "Trusted_Connection=no;"
            )
            
            self.connection = pyodbc.connect(connection_string)
            logger.info("Successfully connected to MSSQL database")
            return True
            
        except pyodbc.Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def extract_timeseries_data(self, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None,
                               table_name: Optional[str] = None,
                               timestamp_column: Optional[str] = None,
                               value_columns: Optional[list] = None) -> pd.DataFrame:
        """
        Extract timeseries data from the database.
        
        Args:
            start_time: Start datetime for data extraction
            end_time: End datetime for data extraction
            table_name: Name of the table to query
            timestamp_column: Name of the timestamp column
            value_columns: List of value columns to extract
            
        Returns:
            pandas.DataFrame: Extracted timeseries data
        """
        if not self.connection:
            raise ConnectionError("No database connection. Call connect() first.")
        
        # Use config defaults if parameters not provided
        query_config = self.config['query']
        table_name = table_name or query_config['table']
        timestamp_column = timestamp_column or query_config['timestamp_column']
        value_columns = value_columns or query_config['value_columns']
        
        # Set default time range if not provided
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            hours_back = query_config.get('default_hours_back', 24)
            start_time = end_time - timedelta(hours=hours_back)
        
        # Build SQL query
        columns = [timestamp_column] + value_columns
        columns_str = ', '.join(columns)
        
        query = f"""
        SELECT {columns_str}
        FROM {table_name}
        WHERE {timestamp_column} >= ? AND {timestamp_column} <= ?
        ORDER BY {timestamp_column}
        """
        
        try:
            logger.info(f"Executing query for data between {start_time} and {end_time}")
            df = pd.read_sql(query, self.connection, params=[start_time, end_time])
            
            # Convert timestamp column to datetime if it's not already
            if timestamp_column in df.columns:
                df[timestamp_column] = pd.to_datetime(df[timestamp_column])
            
            logger.info(f"Successfully extracted {len(df)} rows of timeseries data")
            return df
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None):
        """Save DataFrame to CSV file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timeseries_data_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        return filename
    
    def save_to_protobuf(self, df: pd.DataFrame, filename: str = None):
        """
        Save DataFrame to protobuf-table format for efficient storage.
        Demonstrates usage of pb_table library for data compression.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timeseries_data_{timestamp}.pb"
        
        try:
            # Convert DataFrame to pb_table format
            table_data = {
                'header': [],
                'data': []
            }
            
            # Create header with type inference and compression transforms
            for col in df.columns:
                dtype = df[col].dtype
                if pd.api.types.is_datetime64_any_dtype(dtype):
                    # Convert datetime to Unix timestamp (seconds) for compression
                    pb_type = 'int'
                    # Add sequence transform for timestamp compression
                    table_data['header'].append({
                        'name': col,
                        'type': pb_type,
                        'transform': {
                            'sequence': True  # Delta encoding for timestamps
                        }
                    })
                elif pd.api.types.is_integer_dtype(dtype):
                    pb_type = 'int'
                    table_data['header'].append({
                        'name': col,
                        'type': pb_type
                    })
                elif pd.api.types.is_float_dtype(dtype):
                    pb_type = 'float'
                    table_data['header'].append({
                        'name': col,
                        'type': pb_type
                    })
                elif pd.api.types.is_bool_dtype(dtype):
                    pb_type = 'bool'
                    table_data['header'].append({
                        'name': col,
                        'type': pb_type
                    })
                else:
                    pb_type = 'string'
                    table_data['header'].append({
                        'name': col,
                        'type': pb_type
                    })
            
            # Convert data to array format
            for _, row in df.iterrows():
                row_data = []
                for col in df.columns:
                    value = row[col]
                    # Convert datetime to Unix timestamp (seconds since epoch)
                    if pd.api.types.is_datetime64_any_dtype(df[col].dtype):
                        if pd.notna(value):
                            # Convert to Unix timestamp (seconds)
                            value = int(value.timestamp())
                        else:
                            value = 0
                    # Handle NaN values
                    elif pd.isna(value):
                        value = 0 if df[col].dtype in ['int64', 'float64'] else ""
                    
                    row_data.append(value)
                table_data['data'].append(row_data)
            
            # Use pb_table to encode the data
            encoded_buffer = pb_table.encode_table(table_data)
            
            # Save to file
            with open(filename, 'wb') as f:
                f.write(encoded_buffer)
            
            # Calculate compression stats
            csv_size = len(df.to_csv(index=False).encode('utf-8'))
            pb_size = len(encoded_buffer)
            compression_ratio = csv_size / pb_size if pb_size > 0 else 1
            
            logger.info(f"Data saved to {filename}")
            logger.info(f"Compression: CSV {csv_size} bytes → Protobuf {pb_size} bytes (ratio: {compression_ratio:.2f}x)")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving protobuf data: {e}")
            raise
    

def main():
    """Main function to demonstrate usage."""
    extractor = MSSQLTimeseriesExtractor()
    
    try:
        # Connect to database
        if not extractor.connect():
            logger.error("Failed to connect to database. Please check your configuration.")
            return
        
        # Extract data for the last 24 hours
        df = extractor.extract_timeseries_data()
        
        if not df.empty:
            print(f"\nExtracted {len(df)} rows of data:")
            print(df.head())
            print(f"\nData shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Save to CSV (traditional format)
            csv_filename = extractor.save_to_csv(df)
            print(f"\nCSV data saved to: {csv_filename}")
            
            # Save to protobuf-table format (compressed)
            pb_filename = extractor.save_to_protobuf(df)
            print(f"Protobuf data saved to: {pb_filename}")
            
        else:
            print("No data found for the specified time range.")
    
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    
    finally:
        extractor.disconnect()

if __name__ == "__main__":
    main()
