import numpy as np
import pandas as pd
import argparse
import glob

"""
This script is used to process one or more files specified by the user.

Usage:

    python script.py <inputs>

Arguments:

    <inputs>: One or more inputs, where each input can be either a filename 
              (e.g., 'file1.txt') or a range of file numbers (e.g., '3:5').

Example Usages:

    1. Single File: To process a single file, you can directly pass the filename.
       Example: python script.py file1.txt

    2. Multiple Files: If you have multiple files, you can list them all as arguments.
       Example: python script.py file1.txt file2.txt file3.txt

    3. File Range: If you want to specify a range of file numbers to process, you can pass a range.
       The script interprets this as "process files from start to end".
       Example: python script.py 3-5

    4. Combination: You can combine these approaches in any way you like.
       Example: python script.py file1.txt 3-5 file6.txt

Notes:

    - In the 'File Range' usage, the script expects files to be named in the format 'file#.txt' 
      where '#' is the file number. Please adjust based on your actual filenames.

    - Make sure the files you're trying to process exist and are accessible from the 
      directory where you're running the script.

"""
def process_files(filenames):
    list_of_data_frames = list()
    list_of_stiffness = list()
    list_of_phase = list()
    list_of_frequency = list()
    list_of_amplitude = list()
    for filename in filenames:
        # Open the file and extract column names
        with open(filename, 'r') as file:
            lines = file.readlines()
            col_line = [line for line in lines if line.startswith('# columns:')][0] # just take the first line that start with "# columns:"
            col_names = col_line.replace('# columns:', '').replace('"', '').split()
            # Extract stiffness valuesw
            stiffness_lines = [line for line in lines if '_stiffness:' in line]
            stiffness_values = {line.split(' ')[1].split(':')[0].split('_')[0]: float(line.split(':')[1].strip()[0]) for line in stiffness_lines}
            # Extract the amplitude
            amplitude_line = [line for line in lines if line.startswith('# settings.segment.0.amplitude')][0]
            amplitude = float(amplitude_line.split(sep = ' ')[2])
            # Extract the frequency
            freq_line = [line for line in lines if line.startswith('# settings.segment.0.frequency')][0]
            frequency = float(freq_line.split(sep = ' ')[2])
            # Extract the initial phase
            phase_line = [line for line in lines if line.startswith('# settings.segment.0.start-phase')][0]
            phase = float(phase_line.split(sep = ' ')[2])
        # Read the data into a DataFrame
        df = pd.read_csv(filename, comment='#', delim_whitespace=True, header=None)

        # Assign the column names
        df.columns = col_names
        # add them to a list to return
        list_of_data_frames.append(df)
        list_of_stiffness.append(stiffness_values)
        list_of_frequency.append(frequency)
        list_of_amplitude.append(amplitude)
        list_of_phase.append(phase)
    return list_of_stiffness,list_of_amplitude,list_of_frequency,list_of_phase,list_of_data_frames

def  get_data_frames_from_list_of_names(inputs):
    # Process each input
    for input_str in inputs:
        # Check if the input is a range
        if ':' in input_str:
            start, end = map(int, input_str.split(':'))
            # Assume files are named file1.txt, file2.txt, etc.
            filenames = [f'file{i}.txt' for i in range(start, end+1)]
        else:
            # Use glob to handle wildcards
            filenames = glob.glob(input_str)
        list_of_data_frames = process_files(filenames)
        return list_of_data_frames
