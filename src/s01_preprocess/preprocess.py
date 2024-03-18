import json
from os import environ
import pandas as pd



class Preprocess():
    def __init__(self, drive, exp_config):        
        self.drive = drive
        self.exp_config = exp_config

    def experiments_summary(self):
        # Read file
        df = self.read_file_to_df()

        # Transform dates
        df['ExperimentDate'] = df.ExperimentDate.str[:10]
        df['ExperimentDate'] = pd.to_datetime(df['ExperimentDate'])

        # Filter valid samples and fix data
        df = df[df.ExperimentDate >= pd.to_datetime(self.exp_config.get('training').get('first_date'))]
        df = df[df.InputType == 'Pathogen']
        df['Concentration'] = df['Concentration'].fillna('None')
        df['InputName'] = df.InputName.str.lower()

        # Group by experiment type
        summary = df.groupby(['InputName', 'Concentration'])['InputName'].size().reset_index(name='Count')
        summary['InputNameTotal'] = summary.groupby('InputName')['Count'].transform('sum')
        
        # Write file
        return self.write_df_to_file(summary)

    def read_file_to_df(self):
        # Read experiment config
        folder_id = self.exp_config.get('data').get('source').get('folder_id')
        filename = self.exp_config.get('data').get('source').get('filename')

        # Read file from Google Drive
        file = self.drive.read_file(folder_id, filename)
        
        # Read file into pandas df
        if filename.split('.')[1] == 'xlsx':
            df = pd.read_excel(file, engine='openpyxl')
        elif filename.split('.')[1] == 'csv':
            df = pd.read_csv(file)
        else:
            print("Unsupported file type")
            return None
        
        return df

    def write_df_to_file(self, df):
        # Get output config
        folder_id = self.exp_config.get('data').get('output').get('folder_id')
        filename = self.exp_config.get('data').get('output').get('filename')

        # Write file to Google Drive
        return self.drive.write_file(df, folder_id, filename)

    def preprocess(self, file_path_read, file_path_write):
        pass


if __name__ == '__main__':
    pass