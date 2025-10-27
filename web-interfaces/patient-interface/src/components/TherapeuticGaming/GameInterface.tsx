import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Alert,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Help,
  Emergency,
  Favorite,
  Psychology,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useDispatch, useSelector } from 'react-redux';
import {
  startTherapeuticSession,
  updateProgressMetrics,
  triggerIntervention,
  updateSessionStatus
} from '@tta/shared-components/store/therapeuticStore';
import type { RootState, AppDispatch } from '@tta/shared-components/store/therapeuticStore';
import type { TherapeuticSession, ProgressMetrics } from '@tta/shared-components/types/therapeutic';

interface GameInterfaceProps {
  patientId: string;
  onCrisisDetected?: () => void;
}

const GameInterface: React.FC<GameInterfaceProps> = ({ patientId, onCrisisDetected }) => {
  const theme = useTheme();
  const dispatch = useDispatch<AppDispatch>();

  const {
    currentSession,
    progressMetrics,
    loading,
    error,
    featureFlags
  } = useSelector((state: RootState) => state.therapeutic);

  const [gameState, setGameState] = useState<'idle' | 'playing' | 'paused'>('idle');
  const [currentScenario, setCurrentScenario] = useState<string>('');
  const [emotionalState, setEmotionalState] = useState({ valence: 0, arousal: 50 });
  const [showCrisisDialog, setShowCrisisDialog] = useState(false);
  const [showHelpDialog, setShowHelpDialog] = useState(false);

  // Crisis detection based on emotional state and engagement
  useEffect(() => {
    if (progressMetrics?.riskAssessment.overallRisk === 'crisis') {
      setShowCrisisDialog(true);
      onCrisisDetected?.();
    }
  }, [progressMetrics?.riskAssessment, onCrisisDetected]);

  // Auto-save progress every 30 seconds during active session
  useEffect(() => {
    if (gameState === 'playing' && currentSession) {
      const interval = setInterval(() => {
        const metrics: Partial<ProgressMetrics> = {
          emotionalState: {
            valence: emotionalState.valence,
            arousal: emotionalState.arousal,
            dominance: 50,
            timestamp: new Date(),
            confidence: 85,
          },
          engagementLevel: gameState === 'playing' ? 85 : 30,
        };

        dispatch(updateProgressMetrics({
          sessionId: currentSession.id,
          metrics
        }));
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [gameState, currentSession, emotionalState, dispatch]);

  const handleStartSession = useCallback(async () => {
    const sessionData: Partial<TherapeuticSession> = {
      patientId,
      startTime: new Date(),
      status: 'active',
      therapeuticFramework: {
        type: 'Narrative',
        techniques: ['storytelling', 'character_development', 'choice_consequence'],
        goals: [
          {
            id: 'emotional_regulation',
            description: 'Improve emotional regulation through narrative choices',
            category: 'emotional_regulation',
            targetMetric: 'emotional_stability',
            currentProgress: 0,
            milestones: [],
          }
        ],
        adaptiveDifficulty: {
          currentLevel: 3,
          adjustmentRate: 0.1,
          factors: [],
          lastAdjustment: new Date(),
        },
      },
      progressMetrics: {
        emotionalState: {
          valence: 0,
          arousal: 50,
          dominance: 50,
          timestamp: new Date(),
          confidence: 50,
        },
        engagementLevel: 0,
        therapeuticCompliance: 100,
        skillAcquisition: [],
        riskAssessment: {
          overallRisk: 'low',
          factors: [],
          lastAssessed: new Date(),
          interventionsTriggered: [],
        },
      },
      interventions: [],
    };

    await dispatch(startTherapeuticSession(sessionData));
    setGameState('playing');
    setCurrentScenario('Welcome to your therapeutic journey...');
  }, [patientId, dispatch]);

  const handlePauseSession = useCallback(() => {
    if (currentSession) {
      dispatch(updateSessionStatus('paused'));
      setGameState('paused');
    }
  }, [currentSession, dispatch]);

  const handleStopSession = useCallback(() => {
    if (currentSession) {
      dispatch(updateSessionStatus('completed'));
      setGameState('idle');
      setCurrentScenario('');
    }
  }, [currentSession, dispatch]);

  const handleCrisisSupport = useCallback(() => {
    dispatch(triggerIntervention({
      type: 'crisis_support',
      trigger: {
        type: 'manual',
        conditions: [],
        priority: 'emergency',
      },
      content: {
        title: 'Crisis Support Activated',
        description: 'Immediate support resources are being provided',
        instructions: [
          'Take deep breaths',
          'You are not alone',
          'Help is available',
        ],
        resources: [
          {
            type: 'text',
            url: '/crisis-resources',
            title: 'Crisis Support Resources',
          }
        ],
        estimatedDuration: 5,
        accessibility: {
          screenReaderCompatible: true,
          highContrast: true,
          largeText: true,
          keyboardNavigation: true,
        },
      },
      effectiveness: 0,
      timestamp: new Date(),
    }));
    setShowCrisisDialog(false);
  }, [dispatch]);

  const getProgressColor = (progress: number) => {
    if (progress < 30) return theme.palette.error.main;
    if (progress < 70) return theme.palette.warning.main;
    return theme.palette.success.main;
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header with session controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              Therapeutic Gaming Session
            </Typography>
            <Box display="flex" gap={1}>
              <Chip
                icon={<Psychology />}
                label={currentSession?.status || 'Not Started'}
                color={currentSession?.status === 'active' ? 'primary' : 'default'}
              />
              {featureFlags.aiNarrativeEnhancement && (
                <Chip
                  icon={<Favorite />}
                  label="AI Enhanced"
                  color="secondary"
                />
              )}
            </Box>
          </Box>

          {/* Session controls */}
          <Box display="flex" gap={2} mb={2}>
            {gameState === 'idle' && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleStartSession}
                disabled={loading.session}
                size="large"
              >
                Start Session
              </Button>
            )}

            {gameState === 'playing' && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<Pause />}
                  onClick={handlePauseSession}
                >
                  Pause
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Stop />}
                  onClick={handleStopSession}
                  color="error"
                >
                  End Session
                </Button>
              </>
            )}

            {gameState === 'paused' && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => {
                  setGameState('playing');
                  dispatch(updateSessionStatus('active'));
                }}
              >
                Resume
              </Button>
            )}
          </Box>

          {/* Progress indicators */}
          {progressMetrics && (
            <Box>
              <Typography variant="body2" gutterBottom>
                Engagement Level: {progressMetrics.engagementLevel}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progressMetrics.engagementLevel}
                sx={{
                  mb: 1,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getProgressColor(progressMetrics.engagementLevel),
                  },
                }}
              />

              <Typography variant="body2" gutterBottom>
                Emotional State: Valence {progressMetrics.emotionalState.valence},
                Arousal {progressMetrics.emotionalState.arousal}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Game content area */}
      <AnimatePresence>
        {gameState !== 'idle' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ minHeight: 400 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Scenario
                </Typography>
                <Typography variant="body1" paragraph>
                  {currentScenario || 'Loading therapeutic content...'}
                </Typography>

                {featureFlags.livingWorldsSystem && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    Living Worlds System Active - Your choices shape the narrative
                  </Alert>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating action buttons */}
      <Box sx={{ position: 'fixed', bottom: 24, right: 24 }}>
        <Fab
          color="primary"
          onClick={() => setShowHelpDialog(true)}
          sx={{ mr: 1 }}
          aria-label="Help"
        >
          <Help />
        </Fab>
        <Fab
          color="error"
          onClick={() => setShowCrisisDialog(true)}
          aria-label="Crisis Support"
        >
          <Emergency />
        </Fab>
      </Box>

      {/* Crisis support dialog */}
      <Dialog
        open={showCrisisDialog}
        onClose={() => setShowCrisisDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle color="error.main">
          Crisis Support Available
        </DialogTitle>
        <DialogContent>
          <Typography paragraph>
            If you're experiencing a mental health crisis, immediate support is available.
          </Typography>
          <Typography paragraph>
            • National Suicide Prevention Lifeline: 988
            • Crisis Text Line: Text HOME to 741741
            • Emergency Services: 911
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCrisisDialog(false)}>
            Close
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleCrisisSupport}
          >
            Get Support Now
          </Button>
        </DialogActions>
      </Dialog>

      {/* Help dialog */}
      <Dialog
        open={showHelpDialog}
        onClose={() => setShowHelpDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>How to Use the Therapeutic Gaming Interface</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            This interface provides therapeutic interventions through interactive storytelling:
          </Typography>
          <Typography component="div">
            <ul>
              <li>Start a session to begin your therapeutic journey</li>
              <li>Make choices that reflect your values and goals</li>
              <li>Your progress is automatically tracked and saved</li>
              <li>Crisis support is always available via the red button</li>
              <li>Sessions adapt to your emotional state and progress</li>
            </ul>
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHelpDialog(false)}>
            Got it
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error display */}
      {error.session && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error.session}
        </Alert>
      )}
    </Box>
  );
};

export default GameInterface;
