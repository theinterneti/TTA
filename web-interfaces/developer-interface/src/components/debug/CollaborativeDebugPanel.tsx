import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  UsersIcon,
  PlusIcon,
  ShareIcon,
  ChatBubbleLeftRightIcon,
  BookmarkIcon,
  AnnotationIcon,
  EyeIcon,
  UserCircleIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { collaborativeDebugManager, DebugSession, DebugParticipant, DebugAnnotation, DebugNote } from '../../services/CollaborativeDebugManager';

export const CollaborativeDebugPanel: React.FC = () => {
  const [currentSession, setCurrentSession] = useState<DebugSession | null>(null);
  const [currentUser, setCurrentUser] = useState<DebugParticipant | null>(null);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [showInviteUser, setShowInviteUser] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [sessionDescription, setSessionDescription] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [newNote, setNewNote] = useState('');
  const [newAnnotation, setNewAnnotation] = useState('');

  useEffect(() => {
    // Load current session and user
    setCurrentSession(collaborativeDebugManager.getCurrentSession());
    setCurrentUser(collaborativeDebugManager.getCurrentUser());

    // Set up event listeners
    const handleSessionCreated = (session: DebugSession) => {
      setCurrentSession(session);
    };

    const handleSessionJoined = (session: DebugSession) => {
      setCurrentSession(session);
    };

    const handleSessionLeft = () => {
      setCurrentSession(null);
    };

    const handleParticipantUpdated = (participant: DebugParticipant) => {
      if (currentSession) {
        setCurrentSession({ ...currentSession });
      }
    };

    collaborativeDebugManager.on('session_created', handleSessionCreated);
    collaborativeDebugManager.on('session_joined', handleSessionJoined);
    collaborativeDebugManager.on('session_left', handleSessionLeft);
    collaborativeDebugManager.on('participant_updated', handleParticipantUpdated);

    return () => {
      collaborativeDebugManager.off('session_created', handleSessionCreated);
      collaborativeDebugManager.off('session_joined', handleSessionJoined);
      collaborativeDebugManager.off('session_left', handleSessionLeft);
      collaborativeDebugManager.off('participant_updated', handleParticipantUpdated);
    };
  }, [currentSession]);

  const handleCreateSession = async () => {
    if (!sessionName.trim()) return;

    try {
      await collaborativeDebugManager.createSession(sessionName, sessionDescription);
      setShowCreateSession(false);
      setSessionName('');
      setSessionDescription('');
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const handleLeaveSession = () => {
    collaborativeDebugManager.leaveSession();
  };

  const handleInviteUser = () => {
    if (!inviteEmail.trim() || !currentSession) return;

    try {
      collaborativeDebugManager.inviteUser(inviteEmail, 'collaborator');
      setShowInviteUser(false);
      setInviteEmail('');
    } catch (error) {
      console.error('Error inviting user:', error);
    }
  };

  const handleAddNote = () => {
    if (!newNote.trim() || !currentSession) return;

    collaborativeDebugManager.addNote({
      content: newNote,
      type: 'general',
      priority: 'medium'
    });
    setNewNote('');
  };

  const handleAddAnnotation = () => {
    if (!newAnnotation.trim() || !currentSession) return;

    collaborativeDebugManager.addAnnotation({
      type: 'comment',
      target: {
        component: 'debug-panel',
        selector: '.debug-content'
      },
      content: newAnnotation
    });
    setNewAnnotation('');
  };

  const getParticipantStatusColor = (participant: DebugParticipant) => {
    if (!participant.isOnline) return 'text-gray-400';

    const lastActivity = new Date(participant.lastActivity);
    const now = new Date();
    const minutesAgo = (now.getTime() - lastActivity.getTime()) / (1000 * 60);

    if (minutesAgo < 1) return 'text-green-500';
    if (minutesAgo < 5) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (!currentSession) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8">
        <div className="text-center mb-8">
          <UsersIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Collaborative Debugging</h3>
          <p className="text-gray-600 mb-6">Share debug sessions with your team in real-time</p>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => setShowCreateSession(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Create Debug Session</span>
          </button>

          <div className="text-center">
            <p className="text-sm text-gray-500">or join an existing session with an invitation link</p>
          </div>
        </div>

        {/* Create Session Modal */}
        {showCreateSession && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg p-6 w-96 max-w-full mx-4"
            >
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Debug Session</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Session Name</label>
                  <input
                    type="text"
                    value={sessionName}
                    onChange={(e) => setSessionName(e.target.value)}
                    placeholder="Enter session name..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                  <textarea
                    value={sessionDescription}
                    onChange={(e) => setSessionDescription(e.target.value)}
                    placeholder="Describe what you're debugging..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateSession(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateSession}
                  disabled={!sessionName.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Create Session
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Session Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-semibold text-gray-900">{currentSession.name}</h3>
            <p className="text-sm text-gray-600">{currentSession.description}</p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowInviteUser(true)}
              className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
            >
              <ShareIcon className="h-4 w-4 inline mr-1" />
              Invite
            </button>

            <button
              onClick={handleLeaveSession}
              className="text-sm px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
            >
              Leave
            </button>
          </div>
        </div>

        {/* Participants */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Participants ({currentSession.participants.length}):</span>
          <div className="flex space-x-1">
            {currentSession.participants.map(participant => (
              <div
                key={participant.id}
                className="flex items-center space-x-1 px-2 py-1 bg-white rounded-full text-xs"
                title={`${participant.name} - ${participant.role} - ${participant.isOnline ? 'Online' : 'Offline'}`}
              >
                <div className={`w-2 h-2 rounded-full ${getParticipantStatusColor(participant)}`} />
                <span>{participant.name}</span>
                {participant.role === 'owner' && <span className="text-yellow-600">👑</span>}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-6">
        {/* Shared Notes */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900 flex items-center space-x-2">
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              <span>Shared Notes</span>
            </h4>
          </div>

          <div className="space-y-2 mb-4">
            {currentSession.sharedState.sharedNotes.map(note => (
              <div key={note.id} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">
                    {currentSession.participants.find(p => p.id === note.author)?.name || 'Unknown'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(note.createdAt).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{note.content}</p>
              </div>
            ))}
          </div>

          <div className="flex space-x-2">
            <input
              type="text"
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add a note..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleAddNote()}
            />
            <button
              onClick={handleAddNote}
              disabled={!newNote.trim()}
              className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Add
            </button>
          </div>
        </div>

        {/* Annotations */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900 flex items-center space-x-2">
              <AnnotationIcon className="h-4 w-4" />
              <span>Annotations</span>
            </h4>
          </div>

          <div className="space-y-2 mb-4">
            {currentSession.sharedState.annotations.map(annotation => (
              <div key={annotation.id} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">
                    {currentSession.participants.find(p => p.id === annotation.author)?.name || 'Unknown'}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">
                      {new Date(annotation.createdAt).toLocaleString()}
                    </span>
                    {annotation.resolved ? (
                      <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircleIcon className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-700">{annotation.content}</p>
                <div className="text-xs text-gray-500 mt-1">
                  Target: {annotation.target.component}
                </div>
              </div>
            ))}
          </div>

          <div className="flex space-x-2">
            <input
              type="text"
              value={newAnnotation}
              onChange={(e) => setNewAnnotation(e.target.value)}
              placeholder="Add an annotation..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleAddAnnotation()}
            />
            <button
              onClick={handleAddAnnotation}
              disabled={!newAnnotation.trim()}
              className="px-3 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Annotate
            </button>
          </div>
        </div>

        {/* Bookmarks */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900 flex items-center space-x-2">
              <BookmarkIcon className="h-4 w-4" />
              <span>Bookmarks</span>
            </h4>
            <button
              onClick={() => collaborativeDebugManager.createBookmark('Current State', 'Bookmarked current debug state')}
              className="text-sm px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors"
            >
              <BookmarkIcon className="h-3 w-3 inline mr-1" />
              Bookmark
            </button>
          </div>

          <div className="space-y-2">
            {currentSession.sharedState.bookmarks.map(bookmark => (
              <div key={bookmark.id} className="p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">{bookmark.name}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(bookmark.createdAt).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{bookmark.description}</p>
                <div className="flex items-center space-x-2 mt-2">
                  <span className="text-xs text-gray-500">
                    By: {currentSession.participants.find(p => p.id === bookmark.author)?.name || 'Unknown'}
                  </span>
                  {bookmark.tags.map(tag => (
                    <span key={tag} className="px-1 py-0.5 text-xs bg-green-200 text-green-800 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Invite User Modal */}
      {showInviteUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 w-96 max-w-full mx-4"
          >
            <h3 className="text-lg font-medium text-gray-900 mb-4">Invite User</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="Enter email address..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowInviteUser(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleInviteUser}
                disabled={!inviteEmail.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Send Invitation
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};
