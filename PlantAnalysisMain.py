import os
import pandas as pd
from PlantAnalysis import analyze_file

DATA_FOLDER = "/Users/arthurliu/Documents/InsectRobotics/plant-live-viewing-data/data"
CSV_FILE = "plant_data.csv"


def write_row(filepath, row):
  with open(filepath, 'a') as fd:
    fd.write(f"{row}\n")

def main():
  df = pd.read_csv(CSV_FILE, index_col=False)
  seen_timestamps = df["timestamp"].tolist()
  print("Seen Timestamps", seen_timestamps)

  possible_files = os.listdir(DATA_FOLDER)
  for file in possible_files:
    fullpath = os.path.join(DATA_FOLDER, file)
    if (not file.endswith(".jpg")):
      continue
    timestamp = os.path.splitext(os.path.basename(file))[0][:-7]
    print(timestamp)
    if (timestamp not in seen_timestamps):
      print("Processing: " + timestamp)
      result = analyze_file(fullpath)
      if (result is None):
        write_row(CSV_FILE, f"{timestamp},{-1},{-1}")
      else:
        for i in range(len(result)):
          write_row(CSV_FILE, f"{timestamp},{i},{result[i][0]},{result[i][1][0]},{result[i][1][1]}")

if __name__=="__main__":
  main()