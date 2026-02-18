import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Phone, Building, Lock, Loader2 } from 'lucide-react';
import ErrorMessage from '../common/ErrorMessage';
import SuccessMessage from '../common/SuccessMessage';

const RegisterForm = () => {
  const { register, handleSubmit, watch, formState: { errors } } = useForm();
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const password = watch('password');

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    setSuccess('');

    const result = await signup(data);

    if (result.success) {
      setSuccess('Registration successful! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError(result.error || 'Registration failed');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-3 sm:px-4 py-6 sm:py-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-primary-600 mb-2">LuckyVista</h1>
          <p className="text-sm sm:text-base text-gray-600">Create your account</p>
        </div>

        <div className="card">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">Sign Up</h2>

          {error && <ErrorMessage message={error} onClose={() => setError('')} />}
          {success && <SuccessMessage message={success} />}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3 sm:space-y-4 mt-3 sm:mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  {...register('name', {
                    required: 'Name is required',
                    minLength: { value: 2, message: 'Name must be at least 2 characters' },
                    maxLength: { value: 100, message: 'Name must not exceed 100 characters' },
                    pattern: {
                      value: /^[a-zA-Z\s\-']+$/,
                      message: 'Name can only contain letters, spaces, hyphens, and apostrophes'
                    }
                  })}
                  className={`input-field pl-10 ${errors.name ? 'input-error' : ''}`}
                  placeholder="John Doe"
                />
              </div>
              {errors.name && <p className="error-message">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address'
                    }
                  })}
                  className={`input-field pl-10 ${errors.email ? 'input-error' : ''}`}
                  placeholder="you@example.com"
                />
              </div>
              {errors.email && <p className="error-message">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  {...register('phone', {
                    required: 'Phone number is required',
                    pattern: {
                      value: /^\+?[1-9]\d{1,14}$/,
                      message: 'Invalid phone number format (e.g., +1234567890)'
                    }
                  })}
                  className={`input-field pl-10 ${errors.phone ? 'input-error' : ''}`}
                  placeholder="+1234567890"
                />
              </div>
              {errors.phone && <p className="error-message">{errors.phone.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  {...register('tenant', {
                    required: 'Organization is required',
                    minLength: { value: 2, message: 'Organization must be at least 2 characters' },
                    maxLength: { value: 100, message: 'Organization must not exceed 100 characters' },
                    pattern: {
                      value: /^[a-zA-Z0-9\-_]+$/,
                      message: 'Organization can only contain letters, numbers, hyphens, and underscores'
                    }
                  })}
                  className={`input-field pl-10 ${errors.tenant ? 'input-error' : ''}`}
                  placeholder="acme-corp"
                />
              </div>
              {errors.tenant && <p className="error-message">{errors.tenant.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 8, message: 'Password must be at least 8 characters' },
                    pattern: {
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])/,
                      message: 'Password must contain uppercase, lowercase, digit, and special character'
                    }
                  })}
                  className={`input-field pl-10 ${errors.password ? 'input-error' : ''}`}
                  placeholder="••••••••"
                />
              </div>
              {errors.password && <p className="error-message">{errors.password.message}</p>}
              <p className="text-xs text-gray-500 mt-1">
                Must be 8+ characters with uppercase, lowercase, digit, and special character
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;
