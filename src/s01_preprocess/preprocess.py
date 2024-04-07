import json
from os import environ
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def formatted_colorbar(ax):
    """Adds a colorbar with a custom formatter to an existing heatmap axis."""
    cbar = ax.collections[0].colorbar  
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x:,d}"))

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
        df['Concentration'].fillna(-1, inplace=True)
        df['Concentration'] = df.Concentration.astype(int)
        df['InputName'] = df.InputName.str.lower()

        # Group by experiment type
        summary = df.groupby(['InputName', 'Concentration'])['InputName'].size().reset_index(name='Count')
        summary['InputNameTotal'] = summary.groupby('InputName')['Count'].transform('sum')

        # Create heatmap
        pivot_summary = summary.pivot(index='InputName', columns='Concentration', values='Count')
        pivot_summary.fillna(0, inplace=True)
        pivot_summary = pivot_summary.astype(int)
        fig, ax = plt.subplots(figsize=(len(pivot_summary.columns)/1.5, len(pivot_summary))) 
        sns.heatmap(pivot_summary, annot=True, fmt=".0f", cmap='YlGnBu', ax=ax) 
        plt.title("Experiment Summary Heatmap")

        # Upload heatmap to Google Drive
        done1 = self.write_image_to_drive(fig)
        
        # Write file
        done2 = self.write_df_to_file(summary)

        return done1 and done2

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
        filename = self.exp_config.get('data').get('output').get('filename') + '.xlsx'

        # Write file to Google Drive
        return self.drive.write_file(df, folder_id, filename)
    
    def write_image_to_drive(self, fig):
        # Get output config
        folder_id = self.exp_config.get('data').get('output').get('folder_id')
        filename = self.exp_config.get('data').get('output').get('filename') + '.jpg'
        
        # Upload image to Google Drive
        return self.drive.write_file(fig, folder_id, filename)

    def preprocess(self, file_path_read, file_path_write):
        df = self.read_file_to_df()


if __name__ == '__main__':
    pass