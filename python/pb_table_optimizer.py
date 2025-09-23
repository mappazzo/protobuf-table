#!/usr/bin/env python3
"""
Protobuf-Table Compression Optimizer

Analyzes JSON data and finds optimal transform/sequence settings for pb_table compression.
Tests different combinations of transforms and sequencing to maximize compression ratio.

Usage:
    python pb_table_optimizer.py testdata/complex_test_suite.json
    python pb_table_optimizer.py data.json --verbose
    python pb_table_optimizer.py data.json --output-config config.json
"""

import sys
import os
import json
import argparse
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import itertools

# Add current directory to path to import pb_table
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pb_table import encode_table, decode_table, ProtobufTableError
except ImportError as e:
    print(f"Error importing pb_table: {e}")
    print("Make sure pb_table.py is in the current directory")
    sys.exit(1)

@dataclass
class CompressionResult:
    """Results from a pb_table compression test."""
    config_name: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    size_reduction_percent: float
    space_saved: int
    compression_time: float
    transforms_used: Dict[str, Dict[str, Any]]
    data_integrity: bool
    error_message: Optional[str] = None

class PbTableOptimizer:
    """Optimizer for pb_table compression using transforms and sequencing."""
    
    def __init__(self):
        self.verbose = False
    
    def analyze_json_file(self, json_file_path: str, verbose: bool = False) -> List[CompressionResult]:
        """
        Analyze a JSON file and find optimal pb_table compression settings.
        
        Args:
            json_file_path: Path to JSON file containing table data
            verbose: Whether to print detailed progress information
            
        Returns:
            List of CompressionResult objects sorted by compression ratio (best first)
        """
        self.verbose = verbose
        
        # Load JSON data
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
                data = json.loads(json_data)
        except Exception as e:
            raise ValueError(f"Failed to load JSON file: {e}")
        
        # Extract table data
        if 'test_table' in data:
            table_data = data['test_table']
        elif 'header' in data and 'data' in data:
            table_data = data
        else:
            raise ValueError("JSON must contain 'test_table' or be a valid table format with 'header' and 'data'")
        
        original_size = len(json_data.encode('utf-8'))
        
        if self.verbose:
            print(f"Analyzing table with {len(table_data['data'])} rows and {len(table_data['header'])} fields")
            print(f"Original JSON size: {original_size:,} bytes")
            print()
        
        # Test baseline (no transforms)
        results = []
        baseline_result = self._test_compression(table_data, original_size, "baseline", {})
        results.append(baseline_result)
        
        if self.verbose:
            self._print_result(baseline_result)
        
        # Analyze data characteristics and generate transform configurations
        transform_configs = self._generate_transform_configs(table_data)
        
        # Test each configuration
        for config_name, transforms in transform_configs.items():
            if self.verbose:
                print(f"Testing configuration: {config_name}")
            
            result = self._test_compression(table_data, original_size, config_name, transforms)
            results.append(result)
            
            if self.verbose:
                self._print_result(result)
        
        # Sort by compression ratio (best first)
        results.sort(key=lambda x: x.compression_ratio if x.compression_ratio > 0 else 0, reverse=True)
        
        return results
    
    def _test_compression(self, table_data: Dict[str, Any], original_size: int, 
                         config_name: str, transforms: Dict[str, Dict[str, Any]]) -> CompressionResult:
        """Test compression with specific transform configuration."""
        try:
            # Apply transforms to table configuration
            test_table = self._apply_transforms(table_data, transforms)
            
            # Compress
            start_time = time.time()
            compressed_data = encode_table(test_table)
            compression_time = time.time() - start_time
            
            # Verify data integrity
            try:
                decoded_data = decode_table(compressed_data)
                data_integrity = self._verify_data_integrity(table_data, decoded_data)
            except Exception:
                data_integrity = False
            
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
            size_reduction_percent = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0
            
            return CompressionResult(
                config_name=config_name,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                size_reduction_percent=size_reduction_percent,
                space_saved=original_size - compressed_size,
                compression_time=compression_time,
                transforms_used=transforms,
                data_integrity=data_integrity
            )
            
        except Exception as e:
            return CompressionResult(
                config_name=config_name,
                original_size=original_size,
                compressed_size=0,
                compression_ratio=0.0,
                size_reduction_percent=0.0,
                space_saved=0,
                compression_time=0.0,
                transforms_used=transforms,
                data_integrity=False,
                error_message=str(e)
            )
    
    def _apply_transforms(self, table_data: Dict[str, Any], transforms: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Apply transform configurations to table header."""
        result = {
            'header': [],
            'data': table_data['data']
        }
        
        # Copy metadata if present
        if 'meta' in table_data:
            result['meta'] = table_data['meta']
        
        # Apply transforms to header fields
        for field in table_data['header']:
            field_copy = dict(field)
            field_name = field['name']
            
            if field_name in transforms:
                field_copy['transform'] = transforms[field_name]
            
            result['header'].append(field_copy)
        
        return result
    
    def _generate_transform_configs(self, table_data: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Generate different transform configurations to test."""
        configs = {}
        
        # Analyze each numeric field
        numeric_fields = []
        for i, field in enumerate(table_data['header']):
            if field['type'] in ['int', 'uint', 'float']:
                field_stats = self._analyze_field_data(table_data['data'], i, field['type'])
                numeric_fields.append((field['name'], field['type'], field_stats))
        
        if not numeric_fields:
            return configs
        
        # Generate configurations for individual fields
        for field_name, field_type, stats in numeric_fields:
            # Test different transform options for this field
            field_configs = self._generate_field_transforms(field_name, field_type, stats)
            
            for config_name, transform in field_configs.items():
                configs[f"{field_name}_{config_name}"] = {field_name: transform}
        
        # Generate combination configurations
        if len(numeric_fields) > 1:
            # Test all fields with basic transforms
            all_basic = {}
            for field_name, field_type, stats in numeric_fields:
                if field_type in ['int', 'uint']:
                    # Use basic offset transform
                    if stats['min'] != 0:
                        all_basic[field_name] = {
                            'offset': stats['min'],
                            'multip': 1,
                            'decimals': 0,
                            'sequence': False
                        }
            
            if all_basic:
                configs['all_basic_transforms'] = all_basic
            
            # Test sequence transforms on fields that might benefit
            sequence_candidates = []
            for field_name, field_type, stats in numeric_fields:
                if field_type in ['int', 'uint'] and self._is_sequence_candidate(stats):
                    sequence_candidates.append((field_name, field_type, stats))
            
            if sequence_candidates:
                sequence_config = {}
                for field_name, field_type, stats in sequence_candidates:
                    sequence_config[field_name] = {
                        'offset': 0,
                        'multip': 1,
                        'decimals': 0,
                        'sequence': True
                    }
                configs['sequence_transforms'] = sequence_config
        
        return configs
    
    def _generate_field_transforms(self, field_name: str, field_type: str, stats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Generate transform options for a specific field."""
        transforms = {}
        
        if field_type in ['int', 'uint']:
            # Basic offset transform
            if stats['min'] != 0:
                transforms['offset'] = {
                    'offset': stats['min'],
                    'multip': 1,
                    'decimals': 0,
                    'sequence': False
                }
            
            # Sequence transform (if data looks sequential)
            if self._is_sequence_candidate(stats):
                transforms['sequence'] = {
                    'offset': 0,
                    'multip': 1,
                    'decimals': 0,
                    'sequence': True
                }
        
        elif field_type == 'float':
            # Float with decimal precision
            decimal_places = self._estimate_decimal_places(stats['values'])
            if decimal_places > 0 and decimal_places <= 6:
                transforms['decimal'] = {
                    'offset': 0,
                    'multip': 1,
                    'decimals': decimal_places,
                    'sequence': False
                }
                
                # Also try with offset
                if stats['min'] != 0:
                    transforms['decimal_offset'] = {
                        'offset': stats['min'],
                        'multip': 1,
                        'decimals': decimal_places,
                        'sequence': False
                    }
        
        return transforms
    
    def _analyze_field_data(self, data: List[List[Any]], field_index: int, field_type: str) -> Dict[str, Any]:
        """Analyze characteristics of a specific field's data."""
        values = []
        for row in data:
            if field_index < len(row) and row[field_index] is not None:
                try:
                    if field_type == 'float':
                        values.append(float(row[field_index]))
                    else:
                        values.append(int(row[field_index]))
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return {'min': 0, 'max': 0, 'range': 0, 'values': []}
        
        stats = {
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values),
            'values': values,
            'count': len(values)
        }
        
        # Calculate differences for sequence detection
        if len(values) > 1:
            diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
            stats['diffs'] = diffs
            stats['avg_diff'] = sum(diffs) / len(diffs)
            stats['diff_variance'] = sum((d - stats['avg_diff'])**2 for d in diffs) / len(diffs)
        
        return stats
    
    def _is_sequence_candidate(self, stats: Dict[str, Any]) -> bool:
        """Determine if a field is a good candidate for sequence transforms."""
        if 'diffs' not in stats or len(stats['diffs']) < 2:
            return False
        
        # Check if differences are relatively consistent
        avg_diff = stats['avg_diff']
        diff_variance = stats['diff_variance']
        
        # If average difference is small or variance is low relative to average, it's a good candidate
        if abs(avg_diff) < 10 or (avg_diff != 0 and diff_variance / (avg_diff ** 2) < 0.1):
            return True
        
        return False
    
    def _estimate_decimal_places(self, values: List[float]) -> int:
        """Estimate the number of decimal places used in float values."""
        decimal_places = 0
        for value in values[:10]:  # Sample first 10 values
            str_val = str(value)
            if '.' in str_val:
                decimal_part = str_val.split('.')[1]
                decimal_places = max(decimal_places, len(decimal_part.rstrip('0')))
        
        return min(decimal_places, 6)  # Cap at 6 decimal places
    
    def _verify_data_integrity(self, original: Dict[str, Any], decoded: Dict[str, Any]) -> bool:
        """Verify that decoded data matches original with float tolerance."""
        try:
            if len(original['data']) != len(decoded['data']):
                return False
            
            for i, (orig_row, dec_row) in enumerate(zip(original['data'], decoded['data'])):
                if len(orig_row) != len(dec_row):
                    return False
                
                for j, (orig_val, dec_val) in enumerate(zip(orig_row, dec_row)):
                    if isinstance(orig_val, float) and isinstance(dec_val, float):
                        if abs(orig_val - dec_val) > 1e-6:
                            return False
                    elif orig_val != dec_val:
                        return False
            
            return True
        except Exception:
            return False
    
    def _print_result(self, result: CompressionResult):
        """Print a formatted compression result."""
        if result.error_message:
            print(f"✗ {result.config_name}: {result.error_message}")
            return
        
        integrity_status = "✓" if result.data_integrity else "✗"
        print(f"{integrity_status} {result.config_name}:")
        print(f"  Compressed size: {result.compressed_size:,} bytes")
        print(f"  Compression ratio: {result.compression_ratio:.2f}:1")
        print(f"  Size reduction: {result.size_reduction_percent:.1f}%")
        print(f"  Space saved: {result.space_saved:,} bytes")
        print(f"  Compression time: {result.compression_time:.4f}s")
        if result.transforms_used:
            print(f"  Transforms: {result.transforms_used}")
        print()
    
    def print_summary(self, results: List[CompressionResult], json_file_path: str):
        """Print a summary of optimization results."""
        print("=" * 80)
        print(f"PB_TABLE COMPRESSION OPTIMIZATION SUMMARY: {Path(json_file_path).name}")
        print("=" * 80)
        
        if not results:
            print("No optimization results to display.")
            return
        
        # Find original size and baseline
        original_size = results[0].original_size
        baseline_result = next((r for r in results if r.config_name == 'baseline'), None)
        
        print(f"Original JSON size: {original_size:,} bytes")
        if baseline_result:
            print(f"Baseline compression: {baseline_result.compressed_size:,} bytes ({baseline_result.compression_ratio:.2f}:1)")
        print()
        
        # Print results table
        print(f"{'Configuration':<25} {'Size':<12} {'Ratio':<8} {'Reduction':<10} {'Improvement':<12} {'Integrity':<10}")
        print("-" * 80)
        
        for result in results:
            if result.error_message:
                print(f"{result.config_name:<25} {'ERROR':<12} {'-':<8} {'-':<10} {'-':<12} {'FAIL':<10}")
            else:
                integrity = "PASS" if result.data_integrity else "FAIL"
                
                # Calculate improvement over baseline
                improvement = ""
                if baseline_result and baseline_result.compressed_size > 0:
                    improvement_bytes = baseline_result.compressed_size - result.compressed_size
                    improvement_percent = (improvement_bytes / baseline_result.compressed_size) * 100
                    if improvement_bytes > 0:
                        improvement = f"+{improvement_percent:.1f}%"
                    elif improvement_bytes < 0:
                        improvement = f"{improvement_percent:.1f}%"
                    else:
                        improvement = "0%"
                
                print(f"{result.config_name:<25} {result.compressed_size:<12,} {result.compression_ratio:<8.2f} {result.size_reduction_percent:<10.1f}% {improvement:<12} {integrity:<10}")
        
        print()
        
        # Highlight best configuration
        best_result = None
        for result in results:
            if not result.error_message and result.data_integrity and result.config_name != 'baseline':
                best_result = result
                break
        
        if best_result:
            print(f"🏆 Best configuration: {best_result.config_name}")
            print(f"   Achieves {best_result.compression_ratio:.2f}:1 compression ratio")
            print(f"   Saves {best_result.space_saved:,} bytes ({best_result.size_reduction_percent:.1f}% reduction)")
            
            if baseline_result:
                improvement_bytes = baseline_result.compressed_size - best_result.compressed_size
                improvement_percent = (improvement_bytes / baseline_result.compressed_size) * 100
                if improvement_bytes > 0:
                    print(f"   {improvement_percent:.1f}% better than baseline ({improvement_bytes:,} bytes saved)")
            
            print(f"   Recommended transforms: {best_result.transforms_used}")
        else:
            print("⚠️  No configuration improved upon baseline compression")
    
    def save_config(self, best_result: CompressionResult, output_path: str):
        """Save the best configuration to a JSON file."""
        config = {
            'compression_config': {
                'method': 'pb_table',
                'configuration': best_result.config_name,
                'transforms': best_result.transforms_used,
                'performance': {
                    'compression_ratio': best_result.compression_ratio,
                    'size_reduction_percent': best_result.size_reduction_percent,
                    'compressed_size': best_result.compressed_size
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"Configuration saved to: {output_path}")

def main():
    """Main entry point for the pb_table optimizer."""
    parser = argparse.ArgumentParser(
        description="Optimize pb_table compression using transforms and sequencing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pb_table_optimizer.py testdata/complex_test_suite.json
  python pb_table_optimizer.py data.json --verbose
  python pb_table_optimizer.py data.json --output-config optimal_config.json
        """
    )
    
    parser.add_argument('json_file', help='Path to JSON file containing table data')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed progress and individual test results')
    parser.add_argument('--output-config', '-o', 
                       help='Save optimal configuration to specified JSON file')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.json_file):
        print(f"Error: File '{args.json_file}' not found.")
        sys.exit(1)
    
    # Run optimization
    optimizer = PbTableOptimizer()
    
    try:
        print(f"Optimizing pb_table compression for: {args.json_file}")
        print()
        
        results = optimizer.analyze_json_file(args.json_file, args.verbose)
        
        if not args.verbose:
            print()
        
        optimizer.print_summary(results, args.json_file)
        
        # Save configuration if requested
        if args.output_config:
            best_result = None
            for result in results:
                if not result.error_message and result.data_integrity:
                    best_result = result
                    break
            
            if best_result:
                optimizer.save_config(best_result, args.output_config)
            else:
                print("Warning: No valid configuration found to save")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
