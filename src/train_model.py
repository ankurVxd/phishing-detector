import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

def evaluate_model(model, X_test, y_test, name):
    preds = model.predict(X_test)
    print(f"\n--- {name} ---")
    print("Accuracy :", accuracy_score(y_test, preds))
    print("Precision:", precision_score(y_test, preds))
    print("Recall   :", recall_score(y_test, preds))
    print("F1 Score :", f1_score(y_test, preds))
    print(confusion_matrix(y_test, preds))
    print(classification_report(y_test, preds))
    return f1_score(y_test, preds)

def train_and_select_best():
    X_train, X_test, y_train, y_test = joblib.load("data/processed/train_test_split.pkl")

    log_reg = LogisticRegression(max_iter=1000, class_weight='balanced')
    log_reg.fit(X_train, y_train)
    f1_lr = evaluate_model(log_reg, X_test, y_test, "Logistic Regression")

    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    f1_nb = evaluate_model(nb, X_test, y_test, "Naive Bayes")

    best_model, best_name = (log_reg, "Logistic Regression") if f1_lr >= f1_nb else (nb, "Naive Bayes")
    print(f"\nBest model: {best_name}")

    joblib.dump(best_model, "models/best_model.pkl")
    return best_model

if __name__ == "__main__":
    train_and_select_best()