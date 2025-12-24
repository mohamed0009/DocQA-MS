"""
Generate exactly 2GB of synthetic medical data
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# Calculate how many more patients we need
current_file = Path('datasets/synthetic/training_data.csv')
target_size_gb = 2.0
target_size_bytes = target_size_gb * 1024 * 1024 * 1024

if current_file.exists():
    current_size = current_file.stat().st_size
    current_size_gb = current_size / (1024**3)
    
    print("="*70)
    print("2GB DATASET GENERATOR")
    print("="*70)
    print(f"\nCurrent file size: {current_size_gb:.2f} GB ({current_size:,} bytes)")
    print(f"Target file size: {target_size_gb:.2f} GB ({target_size_bytes:,} bytes)")
    
    if current_size >= target_size_bytes:
        print(f"\n✅ File already meets or exceeds 2GB target!")
        print(f"Current size: {current_size_gb:.2f} GB")
    else:
        needed_bytes = target_size_bytes - current_size
        needed_gb = needed_bytes / (1024**3)
        
        print(f"\nNeed to add: {needed_gb:.2f} GB ({needed_bytes:,} bytes)")
        
        # Load existing data to get structure
        print("\nLoading existing data...")
        df_existing = pd.read_csv(current_file, nrows=1000)
        
        # Calculate average bytes per row
        avg_bytes_per_row = current_size / 500000  # Assuming 500k rows
        additional_rows_needed = int(needed_bytes / avg_bytes_per_row)
        
        print(f"Average bytes per row: {avg_bytes_per_row:.2f}")
        print(f"Additional rows needed: {additional_rows_needed:,}")
        
        # Generate additional data
        print(f"\nGenerating {additional_rows_needed:,} additional patients...")
        
        from generate_synthetic_data import generate_patient_batch
        
        batch_size = 5000
        num_batches = (additional_rows_needed // batch_size) + 1
        
        print(f"Batch size: {batch_size:,}")
        print(f"Number of batches: {num_batches}")
        
        all_batches = []
        for i in range(num_batches):
            if i % 10 == 0:
                print(f"Processing batch {i}/{num_batches}...")
            
            batch = generate_patient_batch(
                start_id=500000 + (i * batch_size),
                batch_size=min(batch_size, additional_rows_needed - (i * batch_size))
            )
            all_batches.append(batch)
        
        # Combine new data
        print("\nCombining new data...")
        df_new = pd.concat(all_batches, ignore_index=True)
        
        # Append to existing file
        print("Appending to existing file...")
        df_new.to_csv(current_file, mode='a', header=False, index=False)
        
        # Check final size
        final_size = current_file.stat().st_size
        final_size_gb = final_size / (1024**3)
        
        print("\n" + "="*70)
        print("GENERATION COMPLETE!")
        print("="*70)
        print(f"Final file size: {final_size_gb:.2f} GB ({final_size:,} bytes)")
        print(f"Total patients: {500000 + len(df_new):,}")
        print(f"Data saved to: {current_file}")
        
        if final_size_gb >= 2.0:
            print("\n✅ Successfully reached 2GB target!")
        else:
            print(f"\n⚠️  Still need {2.0 - final_size_gb:.2f} GB more")
else:
    print("Error: training_data.csv not found!")
    print("Please run generate_4gb_dataset.py first")
