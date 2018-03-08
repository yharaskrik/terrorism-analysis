import csv
import pandas as pd


class File:

    def __init__(self):
        with open('output.txt', 'w') as outfile:
            pass

    def read_data(self, file):
        print('Reading data in from: ', file)
        return pd.read_csv(file, encoding='utf-8')

    def write_line(self, title, data):
        print('Writing: ', title, str(data))
        with open('output.txt', 'a') as outfile:
            outfile.write(title + '\n')
            outfile.write(str(data) + '\n\n')
