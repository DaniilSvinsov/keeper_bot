import re

date = '13.12.2023'
x = re.search("^(0[1-9]|1[0-9]|2[0-9]|3[0-1])(.|-)(0[1-9]|1[0-2])(.|-|)20[0-9][0-9]$", date)
print(bool(x))