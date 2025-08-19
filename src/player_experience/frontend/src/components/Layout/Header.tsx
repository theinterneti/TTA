import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { RootState } from '../../store/store';
import { logout } from '../../store/slices/authSlice';

const Header: React.FC = () => {
  const location = useLocation();
  const dispatch = useDispatch();
  const { profile } = useSelector((state: RootState) => state.player);
  const { selectedCharacter } = useSelector((state: RootState) => state.character);
  const { isConnected } = useSelector((state: RootState) => state.chat);

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/dashboard':
        return 'Dashboard';
      case '/characters':
        return 'Character Management';
      case '/worlds':
        return 'World Selection';
      case '/settings':
        return 'Settings';
      default:
        if (location.pathname.startsWith('/chat')) {
          return selectedCharacter ? `Chat - ${selectedCharacter.name}` : 'Chat';
        }
        return 'TTA Platform';
    }
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-gray-900">{getPageTitle()}</h2>
          
          {/* Connection Status */}
          {location.pathname.startsWith('/chat') && (
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-xs text-gray-500">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* Active Character Indicator */}
          {selectedCharacter && (
            <div className="flex items-center space-x-2 px-3 py-1 bg-primary-50 rounded-full">
              <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-medium">
                  {selectedCharacter.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm text-primary-700">{selectedCharacter.name}</span>
            </div>
          )}

          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-5 5v-5zM10.07 2.82l3.12 3.12M7.05 5.84l3.12 3.12M4.03 8.86l3.12 3.12M1.01 11.88l3.12 3.12"
              />
            </svg>
          </button>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 hover:text-gray-900 transition-colors duration-200"
            >
              <span>Logout</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;