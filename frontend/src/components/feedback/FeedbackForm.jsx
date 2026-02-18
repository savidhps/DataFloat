import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { feedbackAPI } from '../../services/api';
import { Star, MessageSquare, Loader2 } from 'lucide-react';
import ErrorMessage from '../common/ErrorMessage';
import SuccessMessage from '../common/SuccessMessage';

const FeedbackForm = () => {
  const { register, handleSubmit, reset, formState: { errors }, watch, setValue } = useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [overallRatingHover, setOverallRatingHover] = useState(0);
  const [experienceRatingHover, setExperienceRatingHover] = useState(0);
  
  const overallRating = watch('overall_rating');
  const experienceRating = watch('experience_rating');

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Convert string ratings to integers
      const feedbackData = {
        overall_rating: parseInt(data.overall_rating),
        experience_rating: parseInt(data.experience_rating),
        comments: data.comments,
        feature_satisfaction: data.feature_satisfaction ? parseInt(data.feature_satisfaction) : undefined,
        ui_rating: data.ui_rating ? parseInt(data.ui_rating) : undefined,
        recommendation_likelihood: data.recommendation_likelihood ? parseInt(data.recommendation_likelihood) : undefined,
        additional_suggestions: data.additional_suggestions || undefined,
      };

      const response = await feedbackAPI.submit(feedbackData);

      if (response.success) {
        setSuccess('Feedback submitted successfully! Thank you for your input.');
        reset();
      } else {
        setError(response.error || 'Failed to submit feedback');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-3 sm:px-4 py-4 sm:py-6">
      <div className="card">
        <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
          <MessageSquare className="w-6 h-6 sm:w-8 sm:h-8 text-primary-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Submit Feedback</h2>
        </div>

        {error && <ErrorMessage message={error} onClose={() => setError('')} />}
        {success && <SuccessMessage message={success} onClose={() => setSuccess('')} />}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 sm:space-y-6 mt-4 sm:mt-6">
          {/* Overall Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overall Rating <span className="text-red-500">*</span>
            </label>
            <div className="flex items-center gap-1.5 sm:gap-2">
              {[1, 2, 3, 4, 5].map((rating) => {
                const isActive = rating <= (overallRatingHover || overallRating || 0);
                return (
                  <label 
                    key={rating} 
                    className="cursor-pointer"
                    onMouseEnter={() => setOverallRatingHover(rating)}
                    onMouseLeave={() => setOverallRatingHover(0)}
                  >
                    <input
                      type="radio"
                      value={rating}
                      {...register('overall_rating', { required: 'Overall rating is required' })}
                      className="sr-only"
                    />
                    <Star 
                      className={`w-7 h-7 sm:w-8 sm:h-8 transition-colors ${
                        isActive 
                          ? 'text-yellow-400 fill-yellow-400' 
                          : 'text-gray-300'
                      } hover:scale-110`}
                    />
                  </label>
                );
              })}
            </div>
            {errors.overall_rating && (
              <p className="error-message">{errors.overall_rating.message}</p>
            )}
          </div>

          {/* Experience Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Experience Rating <span className="text-red-500">*</span>
            </label>
            <div className="flex items-center gap-1.5 sm:gap-2">
              {[1, 2, 3, 4, 5].map((rating) => {
                const isActive = rating <= (experienceRatingHover || experienceRating || 0);
                return (
                  <label 
                    key={rating} 
                    className="cursor-pointer"
                    onMouseEnter={() => setExperienceRatingHover(rating)}
                    onMouseLeave={() => setExperienceRatingHover(0)}
                  >
                    <input
                      type="radio"
                      value={rating}
                      {...register('experience_rating', { required: 'Experience rating is required' })}
                      className="sr-only"
                    />
                    <Star 
                      className={`w-7 h-7 sm:w-8 sm:h-8 transition-colors ${
                        isActive 
                          ? 'text-yellow-400 fill-yellow-400' 
                          : 'text-gray-300'
                      } hover:scale-110`}
                    />
                  </label>
                );
              })}
            </div>
            {errors.experience_rating && (
              <p className="error-message">{errors.experience_rating.message}</p>
            )}
          </div>

          {/* Comments */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comments <span className="text-red-500">*</span>
            </label>
            <textarea
              {...register('comments', {
                required: 'Comments are required',
                minLength: { value: 10, message: 'Comments must be at least 10 characters' },
                maxLength: { value: 5000, message: 'Comments must not exceed 5000 characters' }
              })}
              rows={4}
              className={`input-field ${errors.comments ? 'input-error' : ''}`}
              placeholder="Please share your detailed feedback..."
            />
            {errors.comments && <p className="error-message">{errors.comments.message}</p>}
          </div>

          {/* Optional Fields */}
          <div className="border-t border-gray-200 pt-4 sm:pt-6">
            <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">Optional Details</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              {/* Feature Satisfaction */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feature Satisfaction (1-5)
                </label>
                <select
                  {...register('feature_satisfaction')}
                  className="input-field"
                >
                  <option value="">Select rating</option>
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <option key={rating} value={rating}>{rating}</option>
                  ))}
                </select>
              </div>

              {/* UI Rating */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  UI Rating (1-5)
                </label>
                <select
                  {...register('ui_rating')}
                  className="input-field"
                >
                  <option value="">Select rating</option>
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <option key={rating} value={rating}>{rating}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Recommendation Likelihood */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How likely are you to recommend us? (1-10)
              </label>
              <select
                {...register('recommendation_likelihood')}
                className="input-field"
              >
                <option value="">Select rating</option>
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                  <option key={rating} value={rating}>{rating}</option>
                ))}
              </select>
            </div>

            {/* Additional Suggestions */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Suggestions
              </label>
              <textarea
                {...register('additional_suggestions', {
                  maxLength: { value: 2000, message: 'Suggestions must not exceed 2000 characters' }
                })}
                rows={3}
                className={`input-field ${errors.additional_suggestions ? 'input-error' : ''}`}
                placeholder="Any additional suggestions or comments..."
              />
              {errors.additional_suggestions && (
                <p className="error-message">{errors.additional_suggestions.message}</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit Feedback'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default FeedbackForm;
