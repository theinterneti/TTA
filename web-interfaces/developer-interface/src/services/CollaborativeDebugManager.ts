/**
 * Multi-User Debug Session Sharing System
 *
 * Enables collaborative debugging capabilities that allow multiple developers
 * to share debug sessions in real-time with synchronized debug panel states,
 * shared network monitoring, and collaborative error analysis.
 */

import { EventEmitter } from 'events';
import { webSocketManager } from './WebSocketManager';

export interface DebugSession {
  id: string;
  name: string;
  description: string;
  createdBy: string;
  createdAt: string;
  isActive: boolean;
  participants: DebugParticipant[];
  sharedState: DebugSessionState;
  permissions: DebugSessionPermissions;
  settings: DebugSessionSettings;
}

export interface DebugParticipant {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'collaborator' | 'viewer';
  joinedAt: string;
  lastActivity: string;
  isOnline: boolean;
  cursor?: {
    x: number;
    y: number;
    component?: string;
  };
  currentView: string; // 'network' | 'errors' | 'console' | 'performance' | 'components'
}

export interface DebugSessionState {
  activeTab: string;
  filters: {
    network: any;
    errors: any;
    console: any;
    performance: any;
    components: any;
  };
  selectedItems: {
    networkRequest?: string;
    error?: string;
    logEntry?: string;
    component?: string;
  };
  annotations: DebugAnnotation[];
  bookmarks: DebugBookmark[];
  sharedNotes: DebugNote[];
}

export interface DebugSessionPermissions {
  canModifyFilters: boolean;
  canSelectItems: boolean;
  canAddAnnotations: boolean;
  canAddBookmarks: boolean;
  canAddNotes: boolean;
  canInviteUsers: boolean;
  canModifySettings: boolean;
}

export interface DebugSessionSettings {
  autoSync: boolean;
  showCursors: boolean;
  showParticipantViews: boolean;
  notifyOnChanges: boolean;
  recordSession: boolean;
  maxParticipants: number;
}

export interface DebugAnnotation {
  id: string;
  type: 'highlight' | 'comment' | 'issue' | 'suggestion';
  target: {
    component: string;
    selector?: string;
    data?: any;
  };
  content: string;
  author: string;
  createdAt: string;
  resolved: boolean;
  resolvedBy?: string;
  resolvedAt?: string;
}

export interface DebugBookmark {
  id: string;
  name: string;
  description: string;
  state: Partial<DebugSessionState>;
  author: string;
  createdAt: string;
  tags: string[];
}

export interface DebugNote {
  id: string;
  content: string;
  author: string;
  createdAt: string;
  updatedAt?: string;
  type: 'general' | 'issue' | 'solution' | 'question';
  priority: 'low' | 'medium' | 'high';
  assignedTo?: string;
}

export interface SessionInvitation {
  id: string;
  sessionId: string;
  invitedBy: string;
  invitedEmail: string;
  role: 'collaborator' | 'viewer';
  expiresAt: string;
  accepted: boolean;
  acceptedAt?: string;
}

export class CollaborativeDebugManager extends EventEmitter {
  private currentSession: DebugSession | null = null;
  private currentUser: DebugParticipant | null = null;
  private sessions: Map<string, DebugSession> = new Map();
  private invitations: Map<string, SessionInvitation> = new Map();
  private syncInterval: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeUser();
    this.setupWebSocketListeners();
  }

  private initializeUser(): void {
    // Initialize current user from stored data or create anonymous user
    const storedUser = localStorage.getItem('tta_debug_user');
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        this.currentUser = {
          ...userData,
          isOnline: true,
          lastActivity: new Date().toISOString(),
          currentView: 'network'
        };
      } catch (error) {
        console.error('Error loading stored user data:', error);
      }
    }

    if (!this.currentUser) {
      this.currentUser = {
        id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: 'Anonymous Developer',
        email: '',
        role: 'owner',
        joinedAt: new Date().toISOString(),
        lastActivity: new Date().toISOString(),
        isOnline: true,
        currentView: 'network'
      };
    }
  }

  private setupWebSocketListeners(): void {
    // Listen for collaborative debug events
    webSocketManager.on('dev_event', (event) => {
      if (event.type.startsWith('debug_session_')) {
        this.handleSessionEvent(event);
      }
    });

    webSocketManager.on('message', (event) => {
      if (event.type === 'collaborative_debug') {
        this.handleCollaborativeEvent(event);
      }
    });
  }

  private handleSessionEvent(event: any): void {
    try {
      switch (event.type) {
        case 'debug_session_state_sync':
          this.handleStateSync(event.data);
          break;
        case 'debug_session_participant_update':
          this.handleParticipantUpdate(event.data);
          break;
        case 'debug_session_annotation_added':
          this.handleAnnotationAdded(event.data);
          break;
        case 'debug_session_note_added':
          this.handleNoteAdded(event.data);
          break;
        default:
          console.log('Unknown session event:', event.type);
      }
    } catch (error) {
      console.error('Error handling session event:', error);
    }
  }

  private handleCollaborativeEvent(event: any): void {
    try {
      const { sessionId, participantId, action, data } = event.data;

      if (this.currentSession?.id === sessionId) {
        this.emit('collaborative_event', {
          sessionId,
          participantId,
          action,
          data,
          timestamp: event.timestamp
        });
      }
    } catch (error) {
      console.error('Error handling collaborative event:', error);
    }
  }

  public async createSession(name: string, description: string, settings?: Partial<DebugSessionSettings>): Promise<DebugSession> {
    if (!this.currentUser) {
      throw new Error('No current user available');
    }

    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const session: DebugSession = {
      id: sessionId,
      name,
      description,
      createdBy: this.currentUser.id,
      createdAt: new Date().toISOString(),
      isActive: true,
      participants: [{ ...this.currentUser, role: 'owner' }],
      sharedState: {
        activeTab: 'network',
        filters: {
          network: {},
          errors: {},
          console: {},
          performance: {},
          components: {}
        },
        selectedItems: {},
        annotations: [],
        bookmarks: [],
        sharedNotes: []
      },
      permissions: {
        canModifyFilters: true,
        canSelectItems: true,
        canAddAnnotations: true,
        canAddBookmarks: true,
        canAddNotes: true,
        canInviteUsers: true,
        canModifySettings: true
      },
      settings: {
        autoSync: true,
        showCursors: true,
        showParticipantViews: true,
        notifyOnChanges: true,
        recordSession: false,
        maxParticipants: 10,
        ...settings
      }
    };

    this.sessions.set(sessionId, session);
    this.currentSession = session;

    // Start sync and heartbeat
    this.startSessionSync();
    this.startHeartbeat();

    // Broadcast session creation
    this.broadcastSessionEvent('session_created', session);

    this.emit('session_created', session);
    console.log(`🤝 Created collaborative debug session: ${name}`);

    return session;
  }

  public async joinSession(sessionId: string, invitationId?: string): Promise<DebugSession> {
    if (!this.currentUser) {
      throw new Error('No current user available');
    }

    // Validate invitation if provided
    if (invitationId) {
      const invitation = this.invitations.get(invitationId);
      if (!invitation || invitation.sessionId !== sessionId || invitation.accepted) {
        throw new Error('Invalid or expired invitation');
      }

      // Accept invitation
      invitation.accepted = true;
      invitation.acceptedAt = new Date().toISOString();
      this.currentUser.role = invitation.role;
    }

    // Get session (in real implementation, this would fetch from server)
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    // Add current user as participant
    const existingParticipant = session.participants.find(p => p.id === this.currentUser!.id);
    if (!existingParticipant) {
      session.participants.push({
        ...this.currentUser,
        joinedAt: new Date().toISOString()
      });
    } else {
      existingParticipant.isOnline = true;
      existingParticipant.lastActivity = new Date().toISOString();
    }

    this.currentSession = session;

    // Start sync and heartbeat
    this.startSessionSync();
    this.startHeartbeat();

    // Broadcast participant joined
    this.broadcastSessionEvent('participant_joined', {
      sessionId,
      participant: this.currentUser
    });

    this.emit('session_joined', session);
    console.log(`🤝 Joined collaborative debug session: ${session.name}`);

    return session;
  }

  public leaveSession(): void {
    if (!this.currentSession || !this.currentUser) return;

    // Update participant status
    const participant = this.currentSession.participants.find(p => p.id === this.currentUser!.id);
    if (participant) {
      participant.isOnline = false;
      participant.lastActivity = new Date().toISOString();
    }

    // Broadcast participant left
    this.broadcastSessionEvent('participant_left', {
      sessionId: this.currentSession.id,
      participantId: this.currentUser.id
    });

    // Stop sync and heartbeat
    this.stopSessionSync();
    this.stopHeartbeat();

    this.emit('session_left', this.currentSession);
    console.log(`🤝 Left collaborative debug session: ${this.currentSession.name}`);

    this.currentSession = null;
  }

  public updateSessionState(updates: Partial<DebugSessionState>): void {
    if (!this.currentSession || !this.hasPermission('canModifyFilters')) return;

    // Update local state
    this.currentSession.sharedState = {
      ...this.currentSession.sharedState,
      ...updates
    };

    // Broadcast state update
    this.broadcastSessionEvent('state_updated', {
      sessionId: this.currentSession.id,
      updates,
      updatedBy: this.currentUser?.id
    });

    this.emit('session_state_updated', this.currentSession.sharedState);
  }

  public selectItem(component: string, itemId: string): void {
    if (!this.currentSession || !this.hasPermission('canSelectItems')) return;

    const updates = {
      selectedItems: {
        ...this.currentSession.sharedState.selectedItems,
        [component]: itemId
      }
    };

    this.updateSessionState(updates);
  }

  public addAnnotation(annotation: Omit<DebugAnnotation, 'id' | 'author' | 'createdAt' | 'resolved'>): void {
    if (!this.currentSession || !this.currentUser || !this.hasPermission('canAddAnnotations')) return;

    const newAnnotation: DebugAnnotation = {
      ...annotation,
      id: `annotation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      author: this.currentUser.id,
      createdAt: new Date().toISOString(),
      resolved: false
    };

    this.currentSession.sharedState.annotations.push(newAnnotation);

    this.broadcastSessionEvent('annotation_added', {
      sessionId: this.currentSession.id,
      annotation: newAnnotation
    });

    this.emit('annotation_added', newAnnotation);
  }

  public addNote(note: Omit<DebugNote, 'id' | 'author' | 'createdAt'>): void {
    if (!this.currentSession || !this.currentUser || !this.hasPermission('canAddNotes')) return;

    const newNote: DebugNote = {
      ...note,
      id: `note_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      author: this.currentUser.id,
      createdAt: new Date().toISOString()
    };

    this.currentSession.sharedState.sharedNotes.push(newNote);

    this.broadcastSessionEvent('note_added', {
      sessionId: this.currentSession.id,
      note: newNote
    });

    this.emit('note_added', newNote);
  }

  public createBookmark(name: string, description: string, tags: string[] = []): void {
    if (!this.currentSession || !this.currentUser || !this.hasPermission('canAddBookmarks')) return;

    const bookmark: DebugBookmark = {
      id: `bookmark_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      description,
      state: { ...this.currentSession.sharedState },
      author: this.currentUser.id,
      createdAt: new Date().toISOString(),
      tags
    };

    this.currentSession.sharedState.bookmarks.push(bookmark);

    this.broadcastSessionEvent('bookmark_added', {
      sessionId: this.currentSession.id,
      bookmark
    });

    this.emit('bookmark_added', bookmark);
  }

  public inviteUser(email: string, role: 'collaborator' | 'viewer' = 'collaborator'): SessionInvitation {
    if (!this.currentSession || !this.currentUser || !this.hasPermission('canInviteUsers')) {
      throw new Error('Cannot invite users');
    }

    const invitation: SessionInvitation = {
      id: `invite_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      sessionId: this.currentSession.id,
      invitedBy: this.currentUser.id,
      invitedEmail: email,
      role,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
      accepted: false
    };

    this.invitations.set(invitation.id, invitation);

    // In real implementation, this would send an email
    console.log(`📧 Invitation created for ${email} to join session ${this.currentSession.name}`);

    this.emit('invitation_created', invitation);
    return invitation;
  }

  public updateCursor(x: number, y: number, component?: string): void {
    if (!this.currentSession || !this.currentUser) return;

    this.currentUser.cursor = { x, y, component };
    this.currentUser.lastActivity = new Date().toISOString();

    this.broadcastSessionEvent('cursor_updated', {
      sessionId: this.currentSession.id,
      participantId: this.currentUser.id,
      cursor: this.currentUser.cursor
    });
  }

  public switchView(view: string): void {
    if (!this.currentSession || !this.currentUser) return;

    this.currentUser.currentView = view;
    this.currentUser.lastActivity = new Date().toISOString();

    this.broadcastSessionEvent('view_changed', {
      sessionId: this.currentSession.id,
      participantId: this.currentUser.id,
      view
    });

    this.emit('view_changed', { participantId: this.currentUser.id, view });
  }

  private hasPermission(permission: keyof DebugSessionPermissions): boolean {
    if (!this.currentSession || !this.currentUser) return false;

    // Owners have all permissions
    if (this.currentUser.role === 'owner') return true;

    return this.currentSession.permissions[permission];
  }

  private startSessionSync(): void {
    if (this.syncInterval) return;

    this.syncInterval = setInterval(() => {
      if (this.currentSession?.settings.autoSync) {
        this.syncSessionState();
      }
    }, 1000); // Sync every second
  }

  private stopSessionSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) return;

    this.heartbeatInterval = setInterval(() => {
      if (this.currentSession && this.currentUser) {
        this.currentUser.lastActivity = new Date().toISOString();
        this.broadcastSessionEvent('heartbeat', {
          sessionId: this.currentSession.id,
          participantId: this.currentUser.id,
          timestamp: this.currentUser.lastActivity
        });
      }
    }, 30000); // Heartbeat every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private syncSessionState(): void {
    if (!this.currentSession) return;

    this.broadcastSessionEvent('state_sync', {
      sessionId: this.currentSession.id,
      state: this.currentSession.sharedState,
      timestamp: new Date().toISOString()
    });
  }

  private broadcastSessionEvent(eventType: string, data: any): void {
    webSocketManager.emit('collaborative_debug_broadcast', {
      type: `debug_session_${eventType}`,
      data,
      timestamp: new Date().toISOString()
    });
  }

  private handleStateSync(data: any): void {
    if (this.currentSession && data.sessionId === this.currentSession.id) {
      this.currentSession.sharedState = data.state;
      this.emit('session_state_synced', data.state);
    }
  }

  private handleParticipantUpdate(data: any): void {
    if (this.currentSession && data.sessionId === this.currentSession.id) {
      const participant = this.currentSession.participants.find(p => p.id === data.participantId);
      if (participant) {
        Object.assign(participant, data.updates);
        this.emit('participant_updated', participant);
      }
    }
  }

  private handleAnnotationAdded(data: any): void {
    if (this.currentSession && data.sessionId === this.currentSession.id) {
      this.currentSession.sharedState.annotations.push(data.annotation);
      this.emit('annotation_added', data.annotation);
    }
  }

  private handleNoteAdded(data: any): void {
    if (this.currentSession && data.sessionId === this.currentSession.id) {
      this.currentSession.sharedState.sharedNotes.push(data.note);
      this.emit('note_added', data.note);
    }
  }

  // Public API methods

  public getCurrentSession(): DebugSession | null {
    return this.currentSession;
  }

  public getCurrentUser(): DebugParticipant | null {
    return this.currentUser;
  }

  public getActiveSessions(): DebugSession[] {
    return Array.from(this.sessions.values()).filter(session => session.isActive);
  }

  public getInvitations(): SessionInvitation[] {
    return Array.from(this.invitations.values());
  }

  public updateUserProfile(updates: Partial<Pick<DebugParticipant, 'name' | 'email'>>): void {
    if (this.currentUser) {
      Object.assign(this.currentUser, updates);
      localStorage.setItem('tta_debug_user', JSON.stringify(this.currentUser));

      if (this.currentSession) {
        this.broadcastSessionEvent('participant_updated', {
          sessionId: this.currentSession.id,
          participantId: this.currentUser.id,
          updates
        });
      }
    }
  }

  public dispose(): void {
    this.leaveSession();
    this.removeAllListeners();
    this.sessions.clear();
    this.invitations.clear();
  }
}

// Singleton instance
export const collaborativeDebugManager = new CollaborativeDebugManager();
