import pandas as pd

csv = pd.read_csv('UploadFile/test1_normal.csv')
csv.columns
print(csv)
print(csv.sum)
print("len(csv)" , len(csv))

for csv_data in csv :
    
