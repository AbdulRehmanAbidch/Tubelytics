import pandas as pd

df = pd.read_csv('data/raw/youtube_video_metadata.csv')

print(" Initial Data Overview")
print("Rows:", df.shape[0], "| Columns:", df.shape[1])
print()

print(" Null Value Report:")
nulls = df.isnull().sum()
print(nulls[nulls > 0])
print()

print(" Empty String Report:")
empty_counts = (df == '').sum()
print(empty_counts[empty_counts > 0])
print()

duplicate_rows = df[df.duplicated()]
print(f" Total Duplicate Rows: {len(duplicate_rows)}")
print()

if 'videoId' in df.columns:
    duplicate_ids = df[df.duplicated(subset='videoId')]
    print(f" Duplicate videoId entries: {len(duplicate_ids)}")
    print()
else:
    print("'videoId' column not found for ID-level duplicate check.")
    print()


df_cleaned = df.drop_duplicates(subset='videoId', keep='first')
df_cleaned = df_cleaned.dropna()  

df_cleaned.to_csv('data/transformed/youtube_video_cleaned.csv', index=False)
print("Cleaned data saved to: data/transformed/youtube_video_cleaned.csv")
