#!/usr/bin/env python3
"""
Example usage of the MSSQL Timeseries Extractor.
This script demonstrates various ways to extract timeseries data.
"""

from extract_timeseries import MSSQLTimeseriesExtractor
from datetime import datetime, timedelta
import pandas as pd

def example_basic_usage():
    """Basic usage example - extract last 24 hours of data."""
    print("=== Basic Usage Example ===")
    
    extractor = MSSQLTimeseriesExtractor()
    
    try:
        if extractor.connect():
            # Extract data for the last 24 hours (default)
            df = extractor.extract_timeseries_data()
            
            if not df.empty:
                print(f"Extracted {len(df)} rows")
                print("First 5 rows:")
                print(df.head())
                
                # Save to CSV
                filename = extractor.save_to_csv(df)
                print(f"Data saved to: {filename}")
            else:
                print("No data found")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.disconnect()

def example_custom_time_range():
    """Example with custom time range."""
    print("\n=== Custom Time Range Example ===")
    
    extractor = MSSQLTimeseriesExtractor()
    
    try:
        if extractor.connect():
            # Define custom time range - last 7 days
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            
            df = extractor.extract_timeseries_data(
                start_time=start_time,
                end_time=end_time
            )
            
            if not df.empty:
                print(f"Extracted {len(df)} rows from {start_time} to {end_time}")
                print("Data summary:")
                print(df.describe())
                
                # Save with custom filename
                filename = f"weekly_data_{start_time.strftime('%Y%m%d')}_to_{end_time.strftime('%Y%m%d')}.csv"
                extractor.save_to_csv(df, filename)
                print(f"Data saved to: {filename}")
            else:
                print("No data found for the specified time range")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.disconnect()

def example_specific_columns():
    """Example extracting specific columns."""
    print("\n=== Specific Columns Example ===")
    
    extractor = MSSQLTimeseriesExtractor()
    
    try:
        if extractor.connect():
            # Extract only specific columns
            df = extractor.extract_timeseries_data(
                value_columns=['temperature', 'pressure'],  # Only these columns
                table_name='sensor_data'  # Specific table
            )
            
            if not df.empty:
                print(f"Extracted {len(df)} rows with specific columns")
                print("Columns:", list(df.columns))
                print(df.head())
                
                # Basic statistics
                if 'temperature' in df.columns:
                    print(f"\nTemperature stats:")
                    print(f"  Min: {df['temperature'].min()}")
                    print(f"  Max: {df['temperature'].max()}")
                    print(f"  Mean: {df['temperature'].mean():.2f}")
                
            else:
                print("No data found")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.disconnect()

def example_data_analysis():
    """Example with basic data analysis."""
    print("\n=== Data Analysis Example ===")
    
    extractor = MSSQLTimeseriesExtractor()
    
    try:
        if extractor.connect():
            df = extractor.extract_timeseries_data()
            
            if not df.empty:
                print(f"Dataset info:")
                print(f"  Shape: {df.shape}")
                print(f"  Date range: {df.iloc[:, 0].min()} to {df.iloc[:, 0].max()}")
                
                # Check for missing values
                missing_values = df.isnull().sum()
                if missing_values.any():
                    print(f"  Missing values:")
                    for col, count in missing_values.items():
                        if count > 0:
                            print(f"    {col}: {count}")
                else:
                    print("  No missing values found")
                
                # Basic statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    print(f"\nNumeric columns statistics:")
                    print(df[numeric_cols].describe())
                
                # Save processed data
                filename = extractor.save_to_csv(df, "analyzed_data.csv")
                print(f"\nData saved to: {filename}")
                
            else:
                print("No data found")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        extractor.disconnect()

if __name__ == "__main__":
    print("MSSQL Timeseries Extractor - Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_custom_time_range()
    example_specific_columns()
    example_data_analysis()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
