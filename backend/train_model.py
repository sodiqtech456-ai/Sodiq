import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Example training data (expand this with real dataset!)
X_train = [
    "Aliens invade Nigeria, president welcomes them.",
    "CBN releases new policy for banking sector.",
    "Scientists discovered a pill to make you live forever.",
    "Governor commissions new bridge in Lagos.",
    "Vaccines cause mind control, experts warn.",
    "Local school wins award for excellence.",
]
y_train = [1, 0, 1, 0, 1, 0]  # 1 = Fake, 0 = Real

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X_train)
model = LogisticRegression()
model.fit(X_vec, y_train)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
print("Model and vectorizer saved to backend/")