# train_model.py

import pandas as pd
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# 1. Load data
df = pd.read_csv('E:\Prediction MBTI\dataset\mbti_1.csv')

# 2. Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)         # Remove URLs
    text = re.sub(r'[^a-z\s]', '', text)        # Remove non-alphabetic
    text = re.sub(r'\s+', ' ', text).strip()    # Remove extra spaces
    return text

df['clean_posts'] = df['posts'].apply(clean_text)

# 3. Balance dataset 
filtered_df = df[df['type'].isin(df['type'].value_counts()[df['type'].value_counts() >= 600].index)]
balanced_parts = []
for t in filtered_df['type'].value_counts()[filtered_df['type'].value_counts() > 700].index:
    sampled = filtered_df[filtered_df['type'] == t].sample(n=650, random_state=42)
    balanced_parts.append(sampled)
for t in filtered_df['type'].value_counts()[filtered_df['type'].value_counts() <= 700].index:
    balanced_parts.append(filtered_df[filtered_df['type'] == t])
balanced_df = pd.concat(balanced_parts).reset_index(drop=True)

# 4. TF-IDF vectorization
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2), stop_words='english')
X = tfidf.fit_transform(balanced_df['clean_posts'])
y = balanced_df['type']

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 6. Train Logistic Regression
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 7. Save model and vectorizer for API
joblib.dump(model, 'personality_model.pkl')
joblib.dump(tfidf, 'vectorizer.pkl')

print("Model and vectorizer saved!")
f = df[df['type'].isin(df['type'].value_counts()[df['type'].value_counts() >= 600].index)]
balanced_parts = []
for t in filtered_df['type'].value_counts()[filtered_df['type'].value_counts() > 700].index:
    sampled = filtered_df[filtered_df['type'] == t].sample(n=650, random_state=42)
    balanced_parts.append(sampled)
for t in filtered_df['type'].value_counts()[filtered_df['type'].value_counts() <= 700].index:
    balanced_parts.append(filtered_df[filtered_df['type'] == t])
balanced_df = pd.concat(balanced_parts).reset_index(drop=True)

# 4. TF-IDF vectorization
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2), stop_words='english')
X = tfidf.fit_transform(balanced_df['clean_posts'])
y = balanced_df['type']

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 6. Train Logistic Regression
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 7. Save model and vectorizer for API
joblib.dump(model, 'personality_model.pkl')
joblib.dump(tfidf, 'vectorizer.pkl')

print("Model and vectorizer saved!")
