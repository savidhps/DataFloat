import React, { useState, useEffect } from 'react';
import { feedbackAPI } from '../services/api';
import { MessageSquare, Calendar, Star, Loader2 } from 'lucide-react';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

const MyFeedbackPage = () => {
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadFeedback();
  }, []);

  const loadFeedback = async () => {
    try {
      const response = await feedbackAPI.getMySubmissions();
      if (response.success) {
        setFeedback(response.feedback || []);
      } else {
        setError('Failed to load feedback');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load feedback');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'love':
      case 'happiness':
      case 'fun':
      case 'enthusiasm':
      case 'relief':
        return 'bg-green-100 text-green-800';
      case 'anger':
      case 'hate':
        return 'bg-red-100 text-red-800';
      case 'sadness':
      case 'worry':
      case 'empty':
        return 'bg-blue-100 text-blue-800';
      case 'surprise':
        return 'bg-yellow-100 text-yellow-800';
      case 'boredom':
        return 'bg-gray-100 text-gray-600';
      case 'neutral':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  if (loading) {
    return <Loading message="Loading your feedback..." />;
  }

  return (
    <div className="py-4 sm:py-6 lg:py-8 px-3 sm:px-4">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
          <MessageSquare className="w-6 h-6 sm:w-8 sm:h-8 text-primary-600" />
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">My Feedback Submissions</h1>
        </div>

        {error && <ErrorMessage message={error} onClose={() => setError('')} />}

        {feedback.length === 0 ? (
          <div className="card text-center py-8 sm:py-12">
            <MessageSquare className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-3 sm:mb-4" />
            <h3 className="text-lg sm:text-xl font-medium text-gray-900 mb-2">No feedback yet</h3>
            <p className="text-sm sm:text-base text-gray-600">You haven't submitted any feedback yet.</p>
          </div>
        ) : (
          <div className="space-y-3 sm:space-y-4">
            {feedback.map((item) => (
              <div key={item.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 sm:gap-4 mb-3 sm:mb-4">
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400 fill-yellow-400" />
                    <span className="font-semibold text-base sm:text-lg">{item.overall_rating}</span>
                  </div>
                  <div className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-500">
                    <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    <span className="hidden sm:inline">{new Date(item.created_at).toLocaleDateString()}</span>
                    <span className="sm:hidden">{new Date(item.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  </div>
                </div>

                <p className="text-sm sm:text-base text-gray-700 mb-3 sm:mb-4">{item.comments}</p>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 pt-3 sm:pt-4 border-t border-gray-200">
                  <div>
                    <p className="text-xs text-gray-500">Experience</p>
                    <p className="text-sm sm:text-base font-medium">{item.experience_rating}/5</p>
                  </div>
                  {item.feature_satisfaction && (
                    <div>
                      <p className="text-xs text-gray-500">Features</p>
                      <p className="text-sm sm:text-base font-medium">{item.feature_satisfaction}/5</p>
                    </div>
                  )}
                  {item.ui_rating && (
                    <div>
                      <p className="text-xs text-gray-500">UI</p>
                      <p className="text-sm sm:text-base font-medium">{item.ui_rating}/5</p>
                    </div>
                  )}
                  {item.recommendation_likelihood && (
                    <div>
                      <p className="text-xs text-gray-500">Recommend</p>
                      <p className="text-sm sm:text-base font-medium">{item.recommendation_likelihood}/10</p>
                    </div>
                  )}
                </div>

                {item.additional_suggestions && (
                  <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gray-200">
                    <p className="text-xs sm:text-sm text-gray-600">
                      <span className="font-medium">Additional suggestions:</span> {item.additional_suggestions}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyFeedbackPage;
