"""
Train sentiment analysis model using emotion detection dataset.
This script loads the CSV data, trains a machine learning model,
and saves it for use in the sentiment analysis service.
"""
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import re


def preprocess_text(text):
    """
    Preprocess text for model training.
    
    Args:
        text: Raw text string
    
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def map_emotion_to_sentiment(emotion):
    """
    Map detailed emotions to simplified sentiment categories.
    
    Args:
        emotion: Original emotion label
    
    Returns:
        Simplified sentiment label (Positive, Negative, Neutral)
    """
    emotion = str(emotion).strip().lower()
    
    # Positive emotions
    positive_emotions = {
        'love', 'joy', 'happy', 'happiness', 'excited', 'excitement',
        'grateful', 'gratitude', 'proud', 'pride', 'satisfied', 'satisfaction',
        'relief', 'relieved', 'hopeful', 'hope', 'optimistic', 'optimism',
        'enthusiastic', 'enthusiasm', 'cheerful', 'delight', 'pleased'
    }
    
    # Negative emotions
    negative_emotions = {
        'hate', 'anger', 'angry', 'sad', 'sadness', 'fear', 'afraid',
        'worry', 'worried', 'anxious', 'anxiety', 'frustrated', 'frustration',
        'disappointed', 'disappointment', 'disgust', 'disgusted', 'jealous',
        'jealousy', 'guilt', 'guilty', 'shame', 'ashamed', 'lonely', 'loneliness',
        'depressed', 'depression', 'annoyed', 'irritated', 'upset'
    }
    
    # Check emotion category
    if emotion in positive_emotions:
        return 'Positive'
    elif emotion in negative_emotions:
        return 'Negative'
    else:
        return 'Neutral'


def load_and_prepare_data(csv_path, sample_size=None):
    """
    Load and prepare the emotion detection dataset.
    
    Args:
        csv_path: Path to CSV file
        sample_size: Optional sample size for faster training (None = use all data)
    
    Returns:
        Tuple of (texts, sentiments)
    """
    print(f"Loading dataset from {csv_path}...")
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    print(f"Total rows loaded: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Sample data if specified (for faster training during development)
    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=42)
        print(f"Using sample of {sample_size} rows for training")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Extract text and emotion columns
    texts = df['text'].astype(str).apply(preprocess_text)
    emotions = df['Emotion'].astype(str).str.strip()
    
    # Map emotions to sentiment categories
    sentiments = emotions.apply(map_emotion_to_sentiment)
    
    # Remove empty texts
    valid_indices = texts.str.len() > 0
    texts = texts[valid_indices]
    sentiments = sentiments[valid_indices]
    
    print(f"\nSentiment distribution:")
    print(sentiments.value_counts())
    print(f"\nTotal valid samples: {len(texts)}")
    
    return texts.tolist(), sentiments.tolist()


def train_model(texts, sentiments, model_type='naive_bayes'):
    """
    Train sentiment analysis model.
    
    Args:
        texts: List of text samples
        sentiments: List of sentiment labels
        model_type: 'naive_bayes' or 'logistic_regression'
    
    Returns:
        Tuple of (model, vectorizer, accuracy, report)
    """
    print(f"\nTraining {model_type} model...")
    
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        texts, sentiments, test_size=0.2, random_state=42, stratify=sentiments
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Create TF-IDF vectorizer
    print("\nCreating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=5000,  # Limit features for efficiency
        ngram_range=(1, 2),  # Use unigrams and bigrams
        min_df=2,  # Ignore terms that appear in less than 2 documents
        max_df=0.8  # Ignore terms that appear in more than 80% of documents
    )
    
    # Transform text to TF-IDF features
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"Feature matrix shape: {X_train_tfidf.shape}")
    
    # Train model
    print(f"\nTraining {model_type} classifier...")
    if model_type == 'naive_bayes':
        model = MultinomialNB(alpha=0.1)
    else:  # logistic_regression
        model = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
    
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate model
    print("\nEvaluating model...")
    y_pred = model.predict(X_test_tfidf)
    
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(report)
    
    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=['Positive', 'Negative', 'Neutral'])
    print(cm)
    
    return model, vectorizer, accuracy, report


def save_model(model, vectorizer, model_dir='models'):
    """
    Save trained model and vectorizer to disk.
    
    Args:
        model: Trained classifier
        vectorizer: Fitted TF-IDF vectorizer
        model_dir: Directory to save models
    """
    # Create models directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'sentiment_model.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
    
    print(f"\nSaving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Saving vectorizer to {vectorizer_path}...")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("Model and vectorizer saved successfully!")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("Sentiment Analysis Model Training")
    print("=" * 60)
    
    # Configuration
    csv_path = 'data/EmotionDetection.csv'
    model_type = 'naive_bayes'  # or 'logistic_regression'
    sample_size = 100000  # Use 100K samples for faster training (None for all data)
    
    # Load and prepare data
    texts, sentiments = load_and_prepare_data(csv_path, sample_size=sample_size)
    
    # Train model
    model, vectorizer, accuracy, report = train_model(texts, sentiments, model_type)
    
    # Save model
    save_model(model, vectorizer)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"Final Accuracy: {accuracy:.4f}")
    print("\nThe trained model is ready to use in the sentiment analysis service.")
    print("Restart the Flask application to load the new model.")


if __name__ == '__main__':
    main()
