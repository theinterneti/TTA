import React, { useEffect, useRef } from 'react';

interface ScreenReaderAnnouncementProps {
  message: string;
  priority?: 'polite' | 'assertive';
  clearAfter?: number; // milliseconds
}

const ScreenReaderAnnouncement: React.FC<ScreenReaderAnnouncementProps> = ({
  message,
  priority = 'polite',
  clearAfter = 1000,
}) => {
  const announcementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (message && announcementRef.current) {
      // Clear any existing content
      announcementRef.current.textContent = '';

      // Add the new message after a brief delay to ensure screen readers pick it up
      setTimeout(() => {
        if (announcementRef.current) {
          announcementRef.current.textContent = message;
        }
      }, 100);

      // Clear the message after the specified time
      if (clearAfter > 0) {
        setTimeout(() => {
          if (announcementRef.current) {
            announcementRef.current.textContent = '';
          }
        }, clearAfter);
      }
    }
  }, [message, clearAfter]);

  return (
    <div
      ref={announcementRef}
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
      role="status"
    />
  );
};

export default ScreenReaderAnnouncement;
