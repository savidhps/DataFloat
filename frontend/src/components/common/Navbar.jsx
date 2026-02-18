import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogOut, LayoutDashboard, MessageSquare, User, Menu, X } from 'lucide-react';

const Navbar = () => {
  const { user, isAuthenticated, isAdmin, signout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSignout = async () => {
    const result = await signout();
    if (result.success) {
      navigate('/login');
    }
    setMobileMenuOpen(false);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and Desktop Navigation */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center flex-shrink-0">
              <span className="text-xl sm:text-2xl font-bold text-primary-600">LuckyVista</span>
            </Link>
            
            {/* Desktop Navigation */}
            <div className="hidden md:ml-10 md:flex md:items-center md:space-x-4">
              {isAdmin() ? (
                <Link
                  to="/admin/dashboard"
                  className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Dashboard</span>
                </Link>
              ) : (
                <>
                  <Link
                    to="/feedback"
                    className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span>Submit Feedback</span>
                  </Link>
                  <Link
                    to="/my-feedback"
                    className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <User className="w-4 h-4" />
                    <span>My Submissions</span>
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Desktop User Info and Sign Out */}
          <div className="hidden md:flex md:items-center md:gap-4">
            <div className="text-sm text-right">
              <p className="font-medium text-gray-900 truncate max-w-[150px]">{user?.name}</p>
              <p className="text-gray-500 text-xs truncate max-w-[150px]">{user?.tenant}</p>
            </div>
            <button
              onClick={handleSignout}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <X className="block h-6 w-6" />
              ) : (
                <Menu className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {/* User Info */}
            <div className="px-3 py-3 border-b border-gray-200 mb-2">
              <p className="font-medium text-gray-900">{user?.name}</p>
              <p className="text-gray-500 text-sm">{user?.tenant}</p>
            </div>

            {/* Navigation Links */}
            {isAdmin() ? (
              <Link
                to="/admin/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-3 px-3 py-3 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <LayoutDashboard className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
            ) : (
              <>
                <Link
                  to="/feedback"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-3 py-3 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  <MessageSquare className="w-5 h-5" />
                  <span>Submit Feedback</span>
                </Link>
                <Link
                  to="/my-feedback"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-3 py-3 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  <User className="w-5 h-5" />
                  <span>My Submissions</span>
                </Link>
              </>
            )}

            {/* Sign Out */}
            <button
              onClick={handleSignout}
              className="w-full flex items-center gap-3 px-3 py-3 rounded-md text-base font-medium text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
