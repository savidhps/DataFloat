"""
Train emotion classification model for LuckyVista feedback system.
Uses the EmotionDetection.csv dataset to train a model that predicts
ALL 13 emotions instead of just Positive/Neutral/Negative.
"""
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import re


def preprocess_text(text):
    """Preprocess text for model training."""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = ' '.join(text.split())
    
    return text


def main():
    """Main training pipeline for emotion classification."""
    print("=" * 70)
    print("EMOTION CLASSIFICATION MODEL TRAINING")
    print("Training on ALL 13 emotions from EmotionDetection.csv")
    print("=" * 70)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'data', 'EmotionDetection.csv')
    
    # Debug information
    print(f"\n🔍 DEBUG INFORMATION:")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
    print(f"Data path: {data_path}")
    print(f"Data file exists: {os.path.exists(data_path)}")
    
    # Load dataset
    print(f"\nLoading dataset from: {data_path}")
    if not os.path.exists(data_path):
        print(f"❌ ERROR: Dataset file not found at {data_path}")
        print(f"\nListing files in script directory:")
        for root, dirs, files in os.walk(script_dir):
            level = root.replace(script_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Limit to first 10 files per directory
                print(f"{subindent}{file}")
        return
    
    df = pd.read_csv(data_path)
    
    print(f"Total samples: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Standardize emotion labels (capitalize first letter for consistency)
    print("\nStandardizing emotion labels...")
    df['Emotion'] = df['Emotion'].str.strip().str.lower().str.capitalize()
    
    print("\nEmotion distribution in dataset:")
    emotion_counts = df['Emotion'].value_counts()
    print(emotion_counts)
    print(f"\nTotal unique emotions: {len(emotion_counts)}")
    
    # Preprocess text
    print("\nPreprocessing text...")
    df['text'] = df['text'].apply(preprocess_text)
    
    # Remove empty texts
    df = df[df['text'].str.len() > 0]
    print(f"Valid samples after preprocessing: {len(df)}")
    
    # Prepare features and labels
    X = df['text'].tolist()
    y = df['Emotion'].tolist()
    
    # Split data
    print("\nSplitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Create TF-IDF vectorizer
    print("\nCreating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=10000,  # More features for 13 classes
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8
    )
    
    # Transform text to TF-IDF features
    print("Transforming text to TF-IDF features...")
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"Feature matrix shape: {X_train_tfidf.shape}")
    
    # Train model
    print("\nTraining Multinomial Naive Bayes classifier...")
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate model
    print("\nEvaluating model...")
    y_pred = model.predict(X_test_tfidf)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    print("\nEmotion Classes in Model:")
    print(f"Total classes: {len(model.classes_)}")
    print(f"Classes: {', '.join(sorted(model.classes_))}")
    
    # Save model
    models_dir = os.path.join(script_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, 'sentiment_model.pkl')
    vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
    
    print(f"\nSaving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Saving vectorizer to {vectorizer_path}...")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Test with sample texts
    print("\n" + "=" * 70)
    print("TESTING MODEL WITH SAMPLE TEXTS")
    print("=" * 70)
    
    test_samples = [
        "I love this platform, it's amazing!",
        "I'm so angry and frustrated with this",
        "This makes me really sad and disappointed",
        "I'm worried about the security issues",
        "This is boring and uninteresting",
        "I feel empty and disconnected",
        "What a fun and enjoyable experience!",
        "I'm surprised by how good this is",
        "I feel relieved that it works now",
        "I'm enthusiastic about the new features",
        "I hate this terrible application",
        "It's okay, nothing special"
    ]
    
    for text in test_samples:
        text_tfidf = vectorizer.transform([preprocess_text(text)])
        prediction = model.predict(text_tfidf)[0]
        probabilities = model.predict_proba(text_tfidf)[0]
        confidence = max(probabilities)
        
        print(f"\nText: '{text}'")
        print(f"Predicted Emotion: {prediction} (Confidence: {confidence:.2%})")
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"Model Type: Multinomial Naive Bayes")
    print(f"Number of Emotions: {len(model.classes_)}")
    print(f"Emotions: {', '.join(sorted(model.classes_))}")
    print(f"Accuracy: {accuracy*100:.2f}%")
    print(f"Model saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")
    print("\n⚠️  IMPORTANT: Restart the Flask backend to load the new model!")
    print("=" * 70)


if __name__ == '__main__':
    main()
