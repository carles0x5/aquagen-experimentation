import os
import json
import argparse
from src.utils.google_drive import GoogleDrive
from src.input_summary.preprocess import Preprocess

EXPERIMENT_CONFIG_PATH = os.getenv('EXPERIMENT_CONFIG_PATH')

def run(output):
    # Configuration parameters
    with open(EXPERIMENT_CONFIG_PATH) as json_file:
        exp_config = json.load(json_file)

    # Initialize Google Drive and Preprocess
    gdw = GoogleDrive()
    pp = Preprocess(gdw, exp_config)

    # Execute main process
    if output == 'input_summary':
        done = pp.experiments_summary()
        if done:
            print('Experiment summary uploaded to Google Drive')
        else:
            print('Failed to upload experiment summary to Google Drive')
    else:
        pass

if __name__ == '__main__':    
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, choices=['input_summary', 'model_training'], required=True,
                        help='The type of execution being run (input summary / model training).')
    args = parser.parse_args()

    # Execute the main function with the parsed arguments
    run(args.output)
    