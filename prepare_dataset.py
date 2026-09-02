import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

# Load the raw file we downloaded
df = pd.read_csv("data/raw/zefang_phishing_email.csv")

print("Original shape:", df.shape)
print("Columns found:", df.columns.tolist())

# Drop the unnamed index column if present
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# Rename to match our pipeline's expected schema
df = df.rename(columns={
    'Email Text': 'body',
    'Email Type': 'label_text'
})

# This dataset has no separate subject line — leave it blank
df['subject'] = ''

# Convert label text to binary: 1 = phishing, 0 = safe
df['label'] = df['label_text'].apply(lambda x: 1 if str(x).strip().lower() == 'phishing email' else 0)

# Drop rows with missing/empty body text
df = df.dropna(subset=['body'])
df = df[df['body'].astype(str).str.strip() != '']

# Keep only the columns our pipeline needs
df = df[['subject', 'body', 'label']]

print("\nCleaned shape:", df.shape)
print("\nLabel distribution:")
print(df['label'].value_counts())
print("\n0 = Safe, 1 = Phishing")

# Save as the combined dataset our data_preprocessing.py script expects
df.to_csv("data/raw/combined_dataset.csv", index=False)
print("\nSaved to data/raw/combined_dataset.csv")