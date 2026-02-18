"""
Sentiment analysis service for LuckyVista.
Provides AI-driven sentiment classification of feedback comments using trained ML model.
"""
import re
import os
import pickle
from typing import Tuple, Optional
from flask import current_app


class SentimentAnalysisService:
    """Service for sentiment analysis of feedback comments using ML model."""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_loaded = False
        
        # Fallback keyword-based analysis
        self.positive_words = {
            'great', 'excellent', 'amazing', 'perfect', 'outstanding',
            'fantastic', 'wonderful', 'love', 'impressed', 'satisfied',
            'recommend', 'good', 'nice', 'awesome', 'brilliant', 'superb',
            'exceptional', 'marvelous', 'terrific', 'fabulous', 'incredible',
            'magnificent', 'splendid', 'delightful', 'pleased', 'happy',
            'thrilled', 'ecstatic', 'overjoyed', 'elated', 'cheerful'
        }
        
        self.negative_words = {
            'terrible', 'poor', 'bad', 'worst', 'horrible', 'awful',
            'disappointing', 'frustrated', 'useless', 'waste', 'hate',
            'difficult', 'confusing', 'bugs', 'issues', 'problems',
            'disgusting', 'pathetic', 'dreadful', 'appalling', 'atrocious',
            'abysmal', 'deplorable', 'lousy', 'rotten', 'miserable',
            'annoying', 'irritating', 'infuriating', 'outrageous', 'ridiculous'
        }
        
        self.neutral_indicators = {
            'okay', 'fine', 'average', 'normal', 'standard', 'typical',
            'regular', 'ordinary', 'common', 'usual', 'acceptable',
            'adequate', 'sufficient', 'reasonable', 'fair', 'moderate'
        }
        
        # Try to load ML model
        self._load_model()
    
    def _load_model(self):
        """Load trained ML model and vectorizer from disk."""
        try:
            model_path = current_app.config.get('MODEL_PATH', 'models/sentiment_model.pkl')
            vectorizer_path = current_app.config.get('VECTORIZER_PATH', 'models/vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                current_app.logger.info(f"Loading ML model from {model_path}...")
                
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                self.model_loaded = True
                current_app.logger.info("ML model loaded successfully!")
            else:
                current_app.logger.warning(
                    f"ML model files not found. Using fallback keyword-based analysis. "
                    f"Run 'python train_sentiment_model.py' to train the model."
                )
        except Exception as e:
            current_app.logger.error(f"Failed to load ML model: {str(e)}")
            current_app.logger.warning("Falling back to keyword-based analysis")
    
    def classify_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Classify sentiment of text using trained ML model or fallback to keyword-based analysis.
        
        Args:
            text: Text to analyze
        
        Returns:
            Tuple of (sentiment_label, confidence_score)
        """
        try:
            if not text or not isinstance(text, str):
                return 'Neutral', 0.0
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if not cleaned_text:
                return 'Neutral', 0.0
            
            # Use ML model if available
            if self.model_loaded and self.model and self.vectorizer:
                return self._classify_with_ml_model(cleaned_text)
            else:
                # Fallback to keyword-based analysis
                return self._classify_with_keywords(cleaned_text)
            
        except Exception as e:
            current_app.logger.error(f"Sentiment analysis failed: {str(e)}")
            return 'Unclassified', 0.0
    
    def _classify_with_ml_model(self, text: str) -> Tuple[str, float]:
        """
        Classify sentiment using trained ML model.
        
        Args:
            text: Preprocessed text
        
        Returns:
            Tuple of (sentiment_label, confidence_score)
        """
        try:
            # Transform text to TF-IDF features
            text_tfidf = self.vectorizer.transform([text])
            
            # Predict sentiment
            prediction = self.model.predict(text_tfidf)[0]
            
            # Get prediction probabilities for confidence score
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(text_tfidf)[0]
                confidence = float(max(probabilities))
            else:
                # For models without predict_proba, use a default confidence
                confidence = 0.75
            
            return prediction, confidence
            
        except Exception as e:
            current_app.logger.error(f"ML model prediction failed: {str(e)}")
            # Fallback to keyword-based
            return self._classify_with_keywords(text)
    
    def _classify_with_keywords(self, text: str) -> Tuple[str, float]:
        """
        Classify sentiment using keyword-based analysis (fallback method).
        
        Args:
            text: Preprocessed text
        
        Returns:
            Tuple of (sentiment_label, confidence_score)
        """
        # Count sentiment indicators
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = sum(1 for word in words if word in self.neutral_indicators)
        
        # Calculate sentiment scores
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            # No sentiment words found, analyze overall tone
            return self._analyze_overall_tone(text)
        
        # Calculate confidence based on sentiment word density
        confidence = min(0.95, max(0.5, total_sentiment_words / len(words) * 2))
        
        # Determine sentiment
        if positive_count > negative_count and positive_count > neutral_count:
            return 'Positive', confidence
        elif negative_count > positive_count and negative_count > neutral_count:
            return 'Negative', confidence
        elif neutral_count > positive_count and neutral_count > neutral_count:
            return 'Neutral', confidence
        elif positive_count == negative_count:
            return 'Neutral', confidence * 0.8  # Lower confidence for mixed sentiment
        else:
            return 'Neutral', confidence * 0.7
    
    def _analyze_overall_tone(self, text: str) -> Tuple[str, float]:
        """
        Analyze overall tone when no explicit sentiment words are found.
        
        Args:
            text: Preprocessed text
        
        Returns:
            Tuple of (sentiment_label, confidence_score)
        """
        # Look for patterns that might indicate sentiment
        text_lower = text.lower()
        
        # Positive patterns
        positive_patterns = [
            r'\b(thank you|thanks)\b',
            r'\b(keep up|well done)\b',
            r'\b(highly|very|really|extremely)\s+\w+',
            r'[!]{2,}',  # Multiple exclamation marks
            r'\b(yes|definitely|absolutely|certainly)\b'
        ]
        
        # Negative patterns
        negative_patterns = [
            r'\b(never|not|no|don\'t|can\'t|won\'t)\b',
            r'\b(fix|broken|error|fail|crash)\b',
            r'\b(slow|sluggish|laggy)\b',
            r'\b(missing|lack|without)\b',
            r'\b(why|how come|what\'s wrong)\b'
        ]
        
        positive_matches = sum(1 for pattern in positive_patterns if re.search(pattern, text_lower))
        negative_matches = sum(1 for pattern in negative_patterns if re.search(pattern, text_lower))
        
        if positive_matches > negative_matches:
            return 'Positive', 0.6
        elif negative_matches > positive_matches:
            return 'Negative', 0.6
        else:
            return 'Neutral', 0.5
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for sentiment analysis.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\!\?]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def get_model_info(self) -> dict:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        if self.model_loaded:
            return {
                'model_type': 'MachineLearningModel',
                'model_file_exists': True,
                'model_loaded': True,
                'model_class': self.model.__class__.__name__,
                'vectorizer_class': self.vectorizer.__class__.__name__
            }
        else:
            return {
                'model_type': 'KeywordBasedSentimentAnalyzer',
                'model_file_exists': False,
                'model_loaded': False,
                'positive_words_count': len(self.positive_words),
                'negative_words_count': len(self.negative_words),
                'neutral_indicators_count': len(self.neutral_indicators)
            }
    
    def retrain_model(self, feedback_data: list) -> bool:
        """
        Retrain model with new feedback data (future enhancement).
        
        Args:
            feedback_data: List of (text, sentiment_label) tuples
        
        Returns:
            Success status
        """
        # This would be implemented for continuous learning
        # For now, return False to indicate not implemented
        return False
