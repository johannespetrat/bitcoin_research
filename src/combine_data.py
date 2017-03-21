import os
import glob
import pandas as pd
import datetime
DATA_DIR = '/Users/Johannes/Documents/projects/quanttrading/bitcoin/backtester/data/'
if __name__ == "__main__":
	bitcoin_df = pd.read_csv(os.path.join('train_2015.csv'))[['Timestamp','Weighted Price']]
	bitcoin_df['Datetime'] = bitcoin_df['Timestamp'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
	files = glob.glob(os.path.join(DATA_DIR,'covariates','*.csv'))
	for file in files:		
		print file.split('/')[-1]
		if 'trends' in file:			
			df = pd.read_csv(file, header=1)
			if 'Week' in df.columns:
				df['Datetime'] = df['Week'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))				
				df.set_index('Datetime', inplace=True)
				df = df.resample('D').sum().interpolate()					
		else:
			df = pd.read_csv(file)
			df['Datetime'] = df.iloc[:,0].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
			df.set_index('Datetime', inplace=True)
			df = df.resample('D').sum().interpolate()
			df.columns = [file.split('/')[-1].replace('.csv','').replace('-','_')]
		
		bitcoin_df = bitcoin_df.merge(df, right_index=True, left_on='Datetime', how='left')

	with open(os.path.join(DATA_DIR,'combined.csv'),'w') as fp:
		bitcoin_df.to_csv(fp, index=False)
