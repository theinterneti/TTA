import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Paper,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  People,
  Warning,
  TrendingUp,
  Refresh,
  Emergency,
  Assessment,
  Timeline,
} from "@mui/icons-material";
import {
  useAuth,
  useHIPAACompliance,
  useCrisisSupport,
  LoadingSpinner,
  CrisisSupportButton,
} from "@tta/shared-components";

interface PatientSummary {
  id: string;
  name: string;
  status: "active" | "at_risk" | "stable" | "crisis";
  lastSession: string;
  riskLevel: number;
  progressScore: number;
}

interface DashboardStats {
  totalPatients: number;
  activeSessions: number;
  crisisAlerts: number;
  avgProgressScore: number;
  sessionsToday: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { logUserAction, logDataAccess } = useHIPAACompliance();
  const { isMonitoring, lastAssessment, averageResponseTime } =
    useCrisisSupport();

  const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
    totalPatients: 0,
    activeSessions: 0,
    crisisAlerts: 0,
    avgProgressScore: 0,
    sessionsToday: 0,
  });

  const [recentPatients, setRecentPatients] = useState<PatientSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  useEffect(() => {
    // Log dashboard access
    logUserAction("dashboard_access", "clinical_dashboard", user?.id);
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Log data access for dashboard metrics
      logDataAccess("dashboard", "clinical_metrics", "clinical_overview");

      // Simulate API call - in production, this would fetch real data
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock data for demonstration
      setDashboardStats({
        totalPatients: 24,
        activeSessions: 3,
        crisisAlerts: 1,
        avgProgressScore: 78,
        sessionsToday: 12,
      });

      setRecentPatients([
        {
          id: "1",
          name: "Patient A",
          status: "stable",
          lastSession: "2 hours ago",
          riskLevel: 2,
          progressScore: 85,
        },
        {
          id: "2",
          name: "Patient B",
          status: "at_risk",
          lastSession: "30 minutes ago",
          riskLevel: 6,
          progressScore: 62,
        },
        {
          id: "3",
          name: "Patient C",
          status: "crisis",
          lastSession: "5 minutes ago",
          riskLevel: 9,
          progressScore: 34,
        },
        {
          id: "4",
          name: "Patient D",
          status: "active",
          lastSession: "1 hour ago",
          riskLevel: 3,
          progressScore: 91,
        },
      ]);

      setLastRefresh(new Date());
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    logUserAction("dashboard_refresh", "clinical_dashboard");
    loadDashboardData();
  };

  const getStatusColor = (status: PatientSummary["status"]) => {
    switch (status) {
      case "crisis":
        return "error";
      case "at_risk":
        return "warning";
      case "active":
        return "info";
      case "stable":
        return "success";
      default:
        return "default";
    }
  };

  const getRiskLevelColor = (riskLevel: number) => {
    if (riskLevel >= 8) return "error";
    if (riskLevel >= 6) return "warning";
    if (riskLevel >= 4) return "info";
    return "success";
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSpinner size="large" message="Loading clinical dashboard..." />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Clinical Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Welcome back,{" "}
            {user?.profile?.firstName && user?.profile?.lastName
              ? `${user.profile.firstName} ${user.profile.lastName}`
              : user?.username || "User"}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          <CrisisSupportButton variant="emergency" />
          <Tooltip title="Refresh Dashboard">
            <IconButton onClick={handleRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Crisis Alert */}
      {lastAssessment && lastAssessment.crisis_level >= 3 && (
        <Alert
          severity="error"
          icon={<Emergency />}
          sx={{ mb: 3 }}
          action={<CrisisSupportButton variant="emergency" />}
        >
          <Typography variant="h6">Crisis Alert</Typography>
          High-risk assessment detected. Immediate intervention may be required.
        </Alert>
      )}

      {/* System Status */}
      <Paper
        sx={{ p: 2, mb: 3, bgcolor: "info.light", color: "info.contrastText" }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Typography variant="body2">
            Crisis Monitoring: {isMonitoring ? "🟢 Active" : "🔴 Inactive"}
          </Typography>
          <Typography variant="body2">
            Avg Response Time: {averageResponseTime.toFixed(0)}ms
          </Typography>
          <Typography variant="body2">
            Last Updated: {lastRefresh.toLocaleTimeString()}
          </Typography>
        </Box>
      </Paper>

      {/* Dashboard Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <People color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {dashboardStats.totalPatients}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Total Patients
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Timeline color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {dashboardStats.activeSessions}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Active Sessions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Warning color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {dashboardStats.crisisAlerts}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Crisis Alerts
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <TrendingUp color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {dashboardStats.avgProgressScore}%
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Avg Progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Assessment color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {dashboardStats.sessionsToday}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Sessions Today
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Patients */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Patient Activity
          </Typography>
          <Grid container spacing={2}>
            {recentPatients.map((patient) => (
              <Grid item xs={12} sm={6} md={3} key={patient.id}>
                <Paper
                  sx={{
                    p: 2,
                    border: 1,
                    borderColor: "divider",
                    "&:hover": {
                      boxShadow: 2,
                      cursor: "pointer",
                    },
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="subtitle2">{patient.name}</Typography>
                    <Chip
                      label={patient.status}
                      size="small"
                      color={getStatusColor(patient.status)}
                    />
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 1 }}
                  >
                    Last session: {patient.lastSession}
                  </Typography>

                  <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Risk Level: {patient.riskLevel}/10
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={patient.riskLevel * 10}
                      color={getRiskLevelColor(patient.riskLevel)}
                      sx={{ height: 4, borderRadius: 2 }}
                    />
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Progress: {patient.progressScore}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={patient.progressScore}
                      color="success"
                      sx={{ height: 4, borderRadius: 2 }}
                    />
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
