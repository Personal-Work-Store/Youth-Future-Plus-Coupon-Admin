import pandas as pd

# 1. 제목행이 customer_id이고 회원번호가 들어있는 파일 (정상 케이스)
data1 = {"customer_id": [11111, 22222, 33333]}
df1 = pd.DataFrame(data1)
df1.to_csv("test1_normal.csv", index=False)
df1.to_excel("test1_normal.xlsx", index=False)

# 2. 제목행이 customer_id이고 회원번호가 없는 파일 (빈 목록)
data2 = {"customer_id": []}
df2 = pd.DataFrame(data2)
df2.to_csv("test2_empty_data.csv", index=False)
df2.to_excel("test2_empty_data.xlsx", index=False)

# 3. 제목행이 있지만 customer_id가 아니고 회원번호가 들어있는 파일
data3 = {"user_id": [11111, 22222, 33333]}
df3 = pd.DataFrame(data3)
df3.to_csv("test3_wrong_header.csv", index=False)
df3.to_excel("test3_wrong_header.xlsx", index=False)

# 4. 제목행이 있지만 customer_id가 아니고 회원번호가 없는 파일
data4 = {"user_id": []}
df4 = pd.DataFrame(data4)
df4.to_csv("test4_wrong_header_empty.csv", index=False)
df4.to_excel("test4_wrong_header_empty.xlsx", index=False)

# 5. 제목행이 없고 바로 회원번호가 있는 파일
data5 = [[11111], [22222], [33333]]
df5 = pd.DataFrame(data5)
df5.to_csv("test5_no_header.csv", index=False, header=False)
df5.to_excel("test5_no_header.xlsx", index=False, header=False)

# 6. 완전히 비어있는 파일
df6 = pd.DataFrame()
df6.to_csv("test6_completely_empty.csv", index=False)
df6.to_excel("test6_completely_empty.xlsx", index=False)

# 7. 지원하지 않는 확장자 파일 (.txt)
with open("test7_unsupported_extension.txt", "w", encoding="utf-8") as f:
    f.write("customer_id\n11111\n22222\n33333")

# 8. csv 확장자지만 내용이 다른 형식
with open("test8_fake_csv.csv", "w", encoding="utf-8") as f:
    f.write("This is not a CSV file content. Just plain text.")

print("모든 테스트 파일 생성 완료!")
print("생성된 파일 목록:")
print("- test1_normal.csv/xlsx (정상)")
print("- test2_empty_data.csv/xlsx (빈 데이터)")
print("- test3_wrong_header.csv/xlsx (잘못된 헤더)")
print("- test4_wrong_header_empty.csv/xlsx (잘못된 헤더 + 빈 데이터)")
print("- test5_no_header.csv/xlsx (헤더 없음)")
print("- test6_completely_empty.csv/xlsx (완전히 빈 파일)")
print("- test7_unsupported_extension.txt (지원하지 않는 확장자)")
print("- test8_fake_csv.csv (가짜 CSV)")
