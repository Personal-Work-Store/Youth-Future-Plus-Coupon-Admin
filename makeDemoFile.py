import pandas as pd

# 데이터 생성
data = {'customer_id' : [11111, 22222, 33333]}
df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv("customer_ids.csv", index=False)

# Excel 파일로 저장
df.to_excel("customer_ids.xlsx", index=False)