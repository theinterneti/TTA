import React, { useEffect, useState } from 'react';
import { waitForSessionRestoration } from '../../utils/sessionRestoration';

interface SessionRestorationWrapperProps {
  children: React.ReactNode;
}

/**
 * SessionRestorationWrapper component that waits for session restoration to complete
 * before rendering the app. This ensures that the ProtectedRoute component has the
 * correct authentication state before checking it.
 */
const SessionRestorationWrapper: React.FC<SessionRestorationWrapperProps> = ({ children }) => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Wait for session restoration to complete
    console.info('SessionRestorationWrapper: Waiting for session restoration...');
    waitForSessionRestoration().then((result) => {
      console.info('Session restoration complete:', result);
      // Add a small delay to ensure Redux store is updated
      setTimeout(() => {
        setIsReady(true);
      }, 100);
    }).catch((error) => {
      console.error('Session restoration wrapper error:', error);
      // Still render the app even if restoration fails
      setTimeout(() => {
        setIsReady(true);
      }, 100);
    });
  }, []);

  if (!isReady) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="spinner"></div>
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }

  return <>{children}</>;
};

export default SessionRestorationWrapper;
