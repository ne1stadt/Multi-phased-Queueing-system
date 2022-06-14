import pandas as pd

temp_col = []
for i in range(3):
    for j in range(5):
        temp_col.append('pi_' + str(i) + '_' + str(j))

a = pd.DataFrame(columns = temp_col)
print(a)