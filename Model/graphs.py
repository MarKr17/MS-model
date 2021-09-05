import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches

df= pd.read_csv("Data/myelin_healths2.txt", sep=' ')

df1=pd.read_csv("Data/myelin_healths6.txt", sep=' ')

df2=pd.read_csv("Data/myelin_healths13.txt", sep=' ')

df3=pd.read_csv("Data/myelin_healths17.txt", sep=' ')

df4=pd.read_csv("Data/myelin_healths.txt", sep=' ')

df5=pd.read_csv("Data/T_active_population.txt", sep=' ')

df6=pd.read_csv("Data/B_infected_population.txt", sep=' ')

df = df.iloc[0: , :]
df1 = df1.iloc[0: , :]
df2 = df2.iloc[0: , :]
df3 = df3.iloc[0: , :]
df4 = df4.iloc[0: , :]
df5 = df5.iloc[0: , :]
df6 = df6.iloc[0: , :]

x=df.iloc[:,0]
y=df.iloc[:,1]
print(str(x))

# plotting the points 
#plt.plot(x, y, color="yellow")

#plt.plot(df.iloc[:,0], df.iloc[:,1], color="#A17917")
#plt.plot(df1.iloc[:,0], df1.iloc[:,1], color="#F4D03F")
#plt.plot(df2.iloc[:,0], df2.iloc[:,1], color="#F7CA18")
#plt.plot(df3.iloc[:,0], df3.iloc[:,1], color="#F5AB35")
plt.plot(df4.iloc[:,0], df4.iloc[:,1], color="yellow")

first_patch = mpatches.Patch(color='#A17917', label='mimikra= 0%')
second_patch = mpatches.Patch(color='#F4D03F', label='mimikra= 25%')
third_patch=mpatches.Patch(color='#F7CA18', label='mimikra=50%')
fourth_patch=mpatches.Patch(color='#F5AB35', label='mimikra=75%')
fifth_patch=mpatches.Patch(color='yellow', label='mimikra=100%')
plt.legend(handles=[fifth_patch])
#plt.legend(handles=[yellow_patch])
# naming the x axis
plt.xlabel('Krok')
# naming the y axis
plt.ylabel('Wartość')

# giving a title to my graph
plt.title('Wykres demielinizacji dla wybranej wartości mimikry')
  
# function to show the plot
plt.show()


