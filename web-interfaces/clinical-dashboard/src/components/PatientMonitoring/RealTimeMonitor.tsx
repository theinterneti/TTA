import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  useTheme,
} from '@mui/material';
import {
  Warning,
  Emergency,
  TrendingUp,
  TrendingDown,
  Psychology,
  Favorite,
  AccessTime,
  Person,
  Phone,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchClinicalDashboard, 
  acknowledgeAlert, 
  triggerIntervention 
} from '@tta/shared-components/store/therapeuticStore';
import type { RootState, AppDispatch } from '@tta/shared-components/store/therapeuticStore';
import type { 
  ClinicalAlert, 
  PatientSummary, 
  ClinicalMetrics 
} from '@tta/shared-components/types/therapeutic';

interface RealTimeMonitorProps {
  clinicianId: string;
}

const RealTimeMonitor: React.FC<RealTimeMonitorProps> = ({ clinicianId }) => {
  const theme = useTheme();
  const dispatch = useDispatch<AppDispatch>();
  
  const { 
    clinicalDashboard, 
    alerts, 
    loading, 
    error 
  } = useSelector((state: RootState) => state.therapeutic);

  const [selectedAlert, setSelectedAlert] = useState<ClinicalAlert | null>(null);
  const [showInterventionDialog, setShowInterventionDialog] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<PatientSummary | null>(null);
  const [emotionalTrendData, setEmotionalTrendData] = useState<any[]>([]);

  // Fetch dashboard data on mount and set up real-time updates
  useEffect(() => {
    dispatch(fetchClinicalDashboard(clinicianId));
    
    // Set up real-time updates every 30 seconds
    const interval = setInterval(() => {
      dispatch(fetchClinicalDashboard(clinicianId));
    }, 30000);

    return () => clearInterval(interval);
  }, [clinicianId, dispatch]);

  // Generate mock emotional trend data
  useEffect(() => {
    const generateTrendData = () => {
      const now = new Date();
      const data = [];
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        data.push({
          time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          valence: Math.random() * 100 - 50,
          arousal: Math.random() * 100,
          engagement: Math.random() * 100,
        });
      }
      setEmotionalTrendData(data);
    };

    generateTrendData();
    const interval = setInterval(generateTrendData, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const handleAcknowledgeAlert = useCallback((alertId: string) => {
    dispatch(acknowledgeAlert(alertId));
    setSelectedAlert(null);
  }, [dispatch]);

  const handleTriggerIntervention = useCallback(async (patientId: string, interventionType: string) => {
    await dispatch(triggerIntervention({
      type: interventionType,
      trigger: {
        type: 'manual',
        conditions: [],
        priority: 'high',
      },
      content: {
        title: `${interventionType} Intervention`,
        description: `Manual intervention triggered by clinician`,
        instructions: ['Immediate support being provided'],
        resources: [],
        estimatedDuration: 10,
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
    
    setShowInterventionDialog(false);
    setSelectedPatient(null);
  }, [dispatch]);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'crisis': return theme.palette.error.main;
      case 'high': return theme.palette.warning.main;
      case 'medium': return theme.palette.info.main;
      default: return theme.palette.success.main;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp color="success" />;
      case 'declining': return <TrendingDown color="error" />;
      default: return <TrendingUp color="disabled" />;
    }
  };

  const criticalAlerts = alerts.filter(alert => 
    alert.severity === 'critical' && !alert.acknowledged
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Critical Alerts Banner */}
      {criticalAlerts.length > 0 && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small">
              View All ({criticalAlerts.length})
            </Button>
          }
        >
          {criticalAlerts.length} critical alert{criticalAlerts.length > 1 ? 's' : ''} require immediate attention
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Overview Metrics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Patients
              </Typography>
              <Typography variant="h3" color="primary">
                {clinicalDashboard?.metrics.activePatients || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                of {clinicalDashboard?.metrics.totalPatients || 0} total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Avg Engagement
              </Typography>
              <Typography variant="h3" color="success.main">
                {clinicalDashboard?.metrics.averageEngagement || 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 24 hours
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Crisis Interventions
              </Typography>
              <Typography variant="h3" color="warning.main">
                {clinicalDashboard?.metrics.crisisInterventions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Today
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Satisfaction
              </Typography>
              <Typography variant="h3" color="info.main">
                {clinicalDashboard?.metrics.patientSatisfaction || 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Patient feedback
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Emotional Trends Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Emotional State Trends (24h)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={emotionalTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="valence" 
                    stackId="1" 
                    stroke={theme.palette.primary.main} 
                    fill={theme.palette.primary.light}
                    name="Emotional Valence"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="engagement" 
                    stackId="2" 
                    stroke={theme.palette.secondary.main} 
                    fill={theme.palette.secondary.light}
                    name="Engagement Level"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Alerts */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Alerts
                <Badge badgeContent={alerts.filter(a => !a.acknowledged).length} color="error" sx={{ ml: 2 }} />
              </Typography>
              <List dense>
                {alerts.slice(0, 5).map((alert) => (
                  <ListItem
                    key={alert.id}
                    button
                    onClick={() => setSelectedAlert(alert)}
                    sx={{
                      borderLeft: `4px solid ${
                        alert.severity === 'critical' ? theme.palette.error.main :
                        alert.severity === 'high' ? theme.palette.warning.main :
                        theme.palette.info.main
                      }`,
                      mb: 1,
                      borderRadius: 1,
                      backgroundColor: alert.acknowledged ? 'transparent' : 'action.hover',
                    }}
                  >
                    <ListItemIcon>
                      {alert.type === 'crisis' ? <Emergency color="error" /> : <Warning />}
                    </ListItemIcon>
                    <ListItemText
                      primary={alert.message}
                      secondary={`${alert.timestamp.toLocaleTimeString()} - ${alert.severity}`}
                      primaryTypographyProps={{
                        variant: 'body2',
                        sx: { fontWeight: alert.acknowledged ? 'normal' : 'bold' }
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Patient List */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patient Overview
              </Typography>
              <Grid container spacing={2}>
                {clinicalDashboard?.patients.map((patient) => (
                  <Grid item xs={12} sm={6} md={4} key={patient.patientId}>
                    <Card 
                      variant="outlined"
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { boxShadow: 2 }
                      }}
                      onClick={() => setSelectedPatient(patient)}
                    >
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="subtitle1">
                            {patient.name}
                          </Typography>
                          <Chip
                            size="small"
                            label={patient.riskLevel}
                            sx={{ 
                              backgroundColor: getRiskColor(patient.riskLevel),
                              color: 'white'
                            }}
                          />
                        </Box>
                        
                        <Box display="flex" alignItems="center" mb={1}>
                          {getTrendIcon(patient.progressTrend)}
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {patient.progressTrend}
                          </Typography>
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary">
                          Last session: {patient.lastSession.toLocaleDateString()}
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary">
                          Active interventions: {patient.activeInterventions}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alert Detail Dialog */}
      <Dialog
        open={!!selectedAlert}
        onClose={() => setSelectedAlert(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Alert Details
        </DialogTitle>
        <DialogContent>
          {selectedAlert && (
            <Box>
              <Typography variant="body1" paragraph>
                <strong>Type:</strong> {selectedAlert.type}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Severity:</strong> {selectedAlert.severity}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Message:</strong> {selectedAlert.message}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Time:</strong> {selectedAlert.timestamp.toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedAlert(null)}>
            Close
          </Button>
          {selectedAlert && !selectedAlert.acknowledged && (
            <Button 
              variant="contained"
              onClick={() => handleAcknowledgeAlert(selectedAlert.id)}
            >
              Acknowledge
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Intervention Dialog */}
      <Dialog
        open={showInterventionDialog}
        onClose={() => setShowInterventionDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Trigger Intervention
        </DialogTitle>
        <DialogContent>
          {selectedPatient && (
            <Box>
              <Typography variant="body1" paragraph>
                Patient: {selectedPatient.name}
              </Typography>
              <Typography variant="body1" paragraph>
                Current Risk Level: {selectedPatient.riskLevel}
              </Typography>
              <Typography variant="body2" paragraph>
                Select intervention type:
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInterventionDialog(false)}>
            Cancel
          </Button>
          <Button 
            variant="outlined"
            onClick={() => selectedPatient && handleTriggerIntervention(selectedPatient.patientId, 'emotional_support')}
          >
            Emotional Support
          </Button>
          <Button 
            variant="contained"
            color="error"
            onClick={() => selectedPatient && handleTriggerIntervention(selectedPatient.patientId, 'crisis_support')}
          >
            Crisis Support
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RealTimeMonitor;
