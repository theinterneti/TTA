import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../auth/AuthProvider';

// Crisis levels matching backend SafetyValidationOrchestrator
export enum CrisisLevel {
  NONE = 0,
  LOW = 1,
  MODERATE = 2,
  HIGH = 3,
  CRITICAL = 4,
}

// Crisis indicators from backend
export interface CrisisIndicator {
  type: string;
  severity: number;
  confidence: number;
  context: string;
}

// Crisis assessment result
export interface CrisisAssessment {
  crisis_detected: boolean;
  crisis_level: CrisisLevel;
  immediate_intervention: boolean;
  indicators: CrisisIndicator[];
  response_time: number;
  assessment_id: string;
  professional_escalation_needed?: boolean;
  escalation_id?: string;
}

// Crisis support context type
interface CrisisSupportContextType {
  // Crisis detection
  assessCrisisRisk: (userInput: string, userHistory?: any[]) => Promise<CrisisAssessment>;

  // Crisis response
  triggerCrisisProtocol: (assessment: CrisisAssessment) => Promise<void>;
  escalateToProfessional: (userId: string, crisisLevel: CrisisLevel) => Promise<any>;

  // Crisis support UI
  showCrisisSupport: boolean;
  setShowCrisisSupport: (show: boolean) => void;
  crisisResources: CrisisResource[];

  // Real-time monitoring
  isMonitoring: boolean;
  lastAssessment: CrisisAssessment | null;

  // Performance tracking
  averageResponseTime: number;
  totalAssessments: number;
}

// Crisis resource information
interface CrisisResource {
  id: string;
  name: string;
  type: 'hotline' | 'chat' | 'text' | 'emergency';
  contact: string;
  description: string;
  availability: string;
  priority: number;
}

// Default crisis resources
const DEFAULT_CRISIS_RESOURCES: CrisisResource[] = [
  {
    id: 'suicide-prevention-lifeline',
    name: 'National Suicide Prevention Lifeline',
    type: 'hotline',
    contact: '988',
    description: '24/7 free and confidential support for people in distress',
    availability: '24/7',
    priority: 1,
  },
  {
    id: 'crisis-text-line',
    name: 'Crisis Text Line',
    type: 'text',
    contact: 'Text HOME to 741741',
    description: 'Free, 24/7 support via text message',
    availability: '24/7',
    priority: 2,
  },
  {
    id: 'emergency-services',
    name: 'Emergency Services',
    type: 'emergency',
    contact: '911',
    description: 'Immediate emergency response',
    availability: '24/7',
    priority: 3,
  },
];

const CrisisSupportContext = createContext<CrisisSupportContextType | undefined>(undefined);

export const useCrisisSupport = () => {
  const context = useContext(CrisisSupportContext);
  if (context === undefined) {
    throw new Error('useCrisisSupport must be used within a CrisisSupportProvider');
  }
  return context;
};

interface CrisisSupportProviderProps {
  children: ReactNode;
  apiBaseUrl?: string;
  enableRealTimeMonitoring?: boolean;
  customResources?: CrisisResource[];
}

export const CrisisSupportProvider: React.FC<CrisisSupportProviderProps> = ({
  children,
  apiBaseUrl = 'http://localhost:8080',
  enableRealTimeMonitoring = true,
  customResources,
}) => {
  const { user, token, isAuthenticated } = useAuth();
  const [showCrisisSupport, setShowCrisisSupport] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [lastAssessment, setLastAssessment] = useState<CrisisAssessment | null>(null);
  const [averageResponseTime, setAverageResponseTime] = useState(0);
  const [totalAssessments, setTotalAssessments] = useState(0);
  const [crisisResources] = useState<CrisisResource[]>(
    customResources || DEFAULT_CRISIS_RESOURCES
  );

  // WebSocket connection for real-time crisis monitoring
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Initialize WebSocket connection for real-time monitoring
  useEffect(() => {
    if (enableRealTimeMonitoring && isAuthenticated && token) {
      const wsUrl = `ws://localhost:8080/ws/crisis-monitoring?token=${token}`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        console.log('Crisis monitoring WebSocket connected');
        setIsMonitoring(true);
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'crisis_assessment') {
            setLastAssessment(data.assessment);
            if (data.assessment.crisis_level >= CrisisLevel.HIGH) {
              setShowCrisisSupport(true);
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocket.onclose = () => {
        console.log('Crisis monitoring WebSocket disconnected');
        setIsMonitoring(false);
      };

      websocket.onerror = (error) => {
        console.error('Crisis monitoring WebSocket error:', error);
        setIsMonitoring(false);
      };

      setWs(websocket);

      return () => {
        websocket.close();
      };
    }
  }, [enableRealTimeMonitoring, isAuthenticated, token]);

  // Assess crisis risk using SafetyValidationOrchestrator
  const assessCrisisRisk = useCallback(async (
    userInput: string,
    userHistory?: any[]
  ): Promise<CrisisAssessment> => {
    const startTime = performance.now();

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/safety/assess-crisis-risk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_input: userInput,
          user_id: user?.id || 'anonymous',
          user_history: userHistory || [],
        }),
      });

      if (!response.ok) {
        throw new Error(`Crisis assessment failed: ${response.statusText}`);
      }

      const assessment: CrisisAssessment = await response.json();
      const responseTime = performance.now() - startTime;

      // Update performance metrics
      setTotalAssessments(prev => prev + 1);
      setAverageResponseTime(prev =>
        (prev * (totalAssessments) + responseTime) / (totalAssessments + 1)
      );

      // Validate <1s response time requirement
      if (responseTime > 1000) {
        console.warn(`Crisis assessment exceeded 1s requirement: ${responseTime}ms`);
      }

      setLastAssessment(assessment);

      // Auto-trigger crisis support for high-risk assessments
      if (assessment.crisis_level >= CrisisLevel.HIGH) {
        await triggerCrisisProtocol(assessment);
      }

      return assessment;
    } catch (error) {
      console.error('Crisis assessment error:', error);

      // Return safe fallback assessment
      return {
        crisis_detected: false,
        crisis_level: CrisisLevel.NONE,
        immediate_intervention: false,
        indicators: [],
        response_time: performance.now() - startTime,
        assessment_id: `fallback-${Date.now()}`,
      };
    }
  }, [apiBaseUrl, token, user?.id, totalAssessments]);

  // Trigger crisis protocol
  const triggerCrisisProtocol = useCallback(async (assessment: CrisisAssessment) => {
    try {
      // Show crisis support UI immediately
      setShowCrisisSupport(true);

      // Log crisis event
      console.log('Crisis protocol triggered:', assessment);

      // Send crisis event to backend for logging and professional notification
      await fetch(`${apiBaseUrl}/api/v1/safety/crisis-protocol`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          assessment_id: assessment.assessment_id,
          user_id: user?.id || 'anonymous',
          crisis_level: assessment.crisis_level,
          immediate_intervention: assessment.immediate_intervention,
        }),
      });

      // Auto-escalate for critical cases
      if (assessment.crisis_level === CrisisLevel.CRITICAL) {
        await escalateToProfessional(user?.id || 'anonymous', assessment.crisis_level);
      }
    } catch (error) {
      console.error('Crisis protocol error:', error);
    }
  }, [apiBaseUrl, token, user?.id]);

  // Escalate to professional
  const escalateToProfessional = useCallback(async (
    userId: string,
    crisisLevel: CrisisLevel
  ) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/safety/escalate-professional`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          crisis_level: crisisLevel,
        }),
      });

      if (!response.ok) {
        throw new Error(`Professional escalation failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Professional escalation initiated:', result);
      return result;
    } catch (error) {
      console.error('Professional escalation error:', error);
      throw error;
    }
  }, [apiBaseUrl, token]);

  const value: CrisisSupportContextType = {
    assessCrisisRisk,
    triggerCrisisProtocol,
    escalateToProfessional,
    showCrisisSupport,
    setShowCrisisSupport,
    crisisResources,
    isMonitoring,
    lastAssessment,
    averageResponseTime,
    totalAssessments,
  };

  return (
    <CrisisSupportContext.Provider value={value}>
      {children}
      <CrisisSupportModal />
    </CrisisSupportContext.Provider>
  );
};

// Crisis Support Modal Component
const CrisisSupportModal: React.FC = () => {
  const { showCrisisSupport, setShowCrisisSupport, crisisResources, lastAssessment } = useCrisisSupport();

  return (
    <AnimatePresence>
      {showCrisisSupport && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowCrisisSupport(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center mb-6">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <span className="text-red-600 text-2xl">🆘</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Crisis Support Available
              </h3>
              <p className="text-sm text-gray-600">
                We're here to help. You don't have to face this alone.
              </p>
            </div>

            <div className="space-y-3 mb-6">
              {crisisResources
                .sort((a, b) => a.priority - b.priority)
                .map((resource) => (
                  <div
                    key={resource.id}
                    className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start mb-1">
                      <h4 className="font-medium text-gray-900 text-sm">
                        {resource.name}
                      </h4>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {resource.availability}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {resource.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-sm font-medium text-blue-600">
                        {resource.contact}
                      </span>
                      <button
                        onClick={() => {
                          if (resource.type === 'hotline' || resource.type === 'emergency') {
                            window.open(`tel:${resource.contact.replace(/\D/g, '')}`);
                          }
                        }}
                        className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                      >
                        {resource.type === 'hotline' || resource.type === 'emergency' ? 'Call' : 'Contact'}
                      </button>
                    </div>
                  </div>
                ))}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowCrisisSupport(false)}
                className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200"
              >
                I'm Safe Now
              </button>
              <button
                onClick={() => {
                  window.open('tel:988');
                }}
                className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
              >
                Call 988 Now
              </button>
            </div>

            {lastAssessment && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  Assessment ID: {lastAssessment.assessment_id}
                </p>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Hook for automatic crisis detection on user input
export const useCrisisDetection = (enableAutoDetection: boolean = true) => {
  const { assessCrisisRisk } = useCrisisSupport();
  const [isAssessing, setIsAssessing] = useState(false);

  const detectCrisis = useCallback(async (userInput: string, userHistory?: any[]) => {
    if (!enableAutoDetection || !userInput.trim()) {
      return null;
    }

    setIsAssessing(true);
    try {
      const assessment = await assessCrisisRisk(userInput, userHistory);
      return assessment;
    } catch (error) {
      console.error('Crisis detection error:', error);
      return null;
    } finally {
      setIsAssessing(false);
    }
  }, [assessCrisisRisk, enableAutoDetection]);

  return {
    detectCrisis,
    isAssessing,
  };
};

// Crisis Support Button Component for manual access
export const CrisisSupportButton: React.FC<{
  className?: string;
  variant?: 'primary' | 'secondary' | 'emergency';
}> = ({ className = '', variant = 'primary' }) => {
  const { setShowCrisisSupport } = useCrisisSupport();

  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    emergency: 'bg-red-600 text-white hover:bg-red-700 animate-pulse',
  };

  return (
    <button
      onClick={() => setShowCrisisSupport(true)}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${variantClasses[variant]} ${className}`}
      aria-label="Access crisis support resources"
    >
      🆘 Crisis Support
    </button>
  );
};

export default CrisisSupportProvider;
