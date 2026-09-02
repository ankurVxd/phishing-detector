import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

def build_tfidf_features(df, max_features=5000):
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9
    )
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['label']
    joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
    return X, y, vectorizer

if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_emails.csv")
    X, y, vectorizer = build_tfidf_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    joblib.dump((X_train, X_test, y_train, y_test), "data/processed/train_test_split.pkl")
    print("TF-IDF shape:", X.shape)