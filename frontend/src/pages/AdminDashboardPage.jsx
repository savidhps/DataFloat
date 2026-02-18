import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Users, MessageSquare, TrendingUp, Star, Loader2 } from 'lucide-react';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

const AdminDashboardPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [sentimentData, setSentimentData] = useState([]);
  const [ratingData, setRatingData] = useState([]);
  const [allFeedback, setAllFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load all dashboard data
      const [metricsRes, sentimentRes, ratingRes, feedbackRes] = await Promise.all([
        adminAPI.getMetrics(),
        adminAPI.getSentimentDistribution(),
        adminAPI.getRatingBreakdown(),
        adminAPI.getFeedback({ limit: 20 }) // Limit to 20 for dashboard display
      ]);

      if (metricsRes.success) {
        setMetrics(metricsRes.metrics);
      }

      if (sentimentRes.success) {
        // Convert sentiment distribution to chart format
        const sentimentChartData = Object.entries(sentimentRes.distribution || {}).map(([key, value]) => ({
          name: key,
          count: value
        })).filter(item => item.count > 0); // Only show non-zero values
        setSentimentData(sentimentChartData);
      }

      if (ratingRes.success) {
        // Convert rating breakdown to chart format
        const ratingChartData = Object.entries(ratingRes.breakdown || {}).map(([key, value]) => ({
          rating: key,
          count: value
        })).filter(item => item.count > 0); // Only show non-zero values
        setRatingData(ratingChartData);
      }

      if (feedbackRes.success) {
        setAllFeedback(feedbackRes.feedback || []);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = {
    Love: '#10b981',
    Happiness: '#34d399',
    Fun: '#6ee7b7',
    Enthusiasm: '#a7f3d0',
    Relief: '#d1fae5',
    Anger: '#ef4444',
    Hate: '#dc2626',
    Sadness: '#3b82f6',
    Worry: '#60a5fa',
    Empty: '#93c5fd',
    Surprise: '#fbbf24',
    Boredom: '#9ca3af',
    Neutral: '#6b7280',
    Unclassified: '#9ca3af'
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
    return <Loading message="Loading dashboard..." />;
  }

  return (
    <div className="py-4 sm:py-6 lg:py-8 px-3 sm:px-4 lg:px-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-6 lg:mb-8">Admin Dashboard</h1>

        {error && <ErrorMessage message={error} onClose={() => setError('')} />}

        {/* Metrics Cards */}
        {metrics && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-4 sm:mb-6 lg:mb-8">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm text-gray-600">Total Users</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">{metrics.total_users}</p>
                </div>
                <Users className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-primary-600" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm text-gray-600">Total Feedback</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">{metrics.total_feedback}</p>
                </div>
                <MessageSquare className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-primary-600" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm text-gray-600">Average Rating</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">{metrics.average_overall_rating?.toFixed(1) || 'N/A'}</p>
                </div>
                <Star className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-yellow-400 fill-yellow-400" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm text-gray-600">Positive Ratio</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">{metrics.positive_to_negative_ratio?.toFixed(1) || 'N/A'}</p>
                </div>
                <TrendingUp className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-green-600" />
              </div>
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 lg:gap-6 mb-4 sm:mb-6 lg:mb-8">
          {/* Sentiment Distribution */}
          <div className="card">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">Sentiment Distribution</h2>
            {sentimentData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={window.innerWidth < 640 ? 60 : 80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#9ca3af'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8 sm:py-12 text-sm sm:text-base">No sentiment data available</p>
            )}
          </div>

          {/* Rating Breakdown */}
          <div className="card">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">Rating Breakdown</h2>
            {ratingData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
                <BarChart data={ratingData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="rating" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0ea5e9" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8 sm:py-12 text-sm sm:text-base">No rating data available</p>
            )}
          </div>
        </div>

        {/* All Feedback Table */}
        <div className="card">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4">All Feedback</h2>
          {allFeedback.length > 0 ? (
            <div className="overflow-x-auto -mx-6 sm:mx-0">
              <div className="inline-block min-w-full align-middle">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tenant
                      </th>
                      <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rating
                      </th>
                      <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sentiment
                      </th>
                      <th className="hidden md:table-cell px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Comments
                      </th>
                      <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {allFeedback.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">
                          <span className="block max-w-[100px] sm:max-w-none truncate">{item.tenant}</span>
                        </td>
                        <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900">
                          <div className="flex items-center gap-1">
                            <Star className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-400 fill-yellow-400" />
                            {item.overall_rating}
                          </div>
                        </td>
                        <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap">
                          <span className={`px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs font-medium ${getSentimentColor(item.sentiment_label)}`}>
                            {item.sentiment_label || 'N/A'}
                          </span>
                        </td>
                        <td className="hidden md:table-cell px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-900 max-w-xs lg:max-w-md truncate">
                          {item.comments}
                        </td>
                        <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                          <span className="hidden sm:inline">{new Date(item.created_at).toLocaleDateString()}</span>
                          <span className="sm:hidden">{new Date(item.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8 sm:py-12 text-sm sm:text-base">No feedback available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
