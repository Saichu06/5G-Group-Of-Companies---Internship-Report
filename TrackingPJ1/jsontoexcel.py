import openpyxl

data = [
    {"name": "Sai", "age": 20, "city": "Hyderabad"},
    {"name": "John", "age": 25, "city": "Delhi"},
    {"name": "Emma", "age": 30, "city": "Mumbai"}
]


wb=openpyxl.Workbook() #new excel file in memory
ws=wb.active #select first sheet (in mem)
ws.title="5G Group"

#extracting headers from data for column names
headers=list(data[0].keys())
ws.append(headers)

#writing each json objects as a row 
for item in data:
    row=[item[key] for key in headers]
    ws.append(row)

wb.save("test.xlsx")

print("Excel file created : test.xlsx")
