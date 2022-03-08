import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CSV_FILE = "plant_data.csv"
df = pd.read_csv(CSV_FILE, index_col=False)
df = df.pivot(index='timestamp', columns='id', values='size')

sns.lineplot(data=df)
plt.show()