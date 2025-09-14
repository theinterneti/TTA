/**
 * TTA Dashboard Component
 *
 * Main dashboard for the therapeutic gaming experience.
 */

import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Avatar,
  Chip,
  LinearProgress,
} from "@mui/material";
import {
  Person,
  PlayArrow,
  TrendingUp,
  Psychology,
  Explore,
} from "@mui/icons-material";
import { RootState } from "../store/store";
import { UserAccount } from "../types/therapeutic";

interface DashboardProps {
  user: UserAccount | null;
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  // Mock data for now - in a real app this would come from Redux store
  const mockStats = {
    sessionsCompleted: 12,
    currentStreak: 5,
    totalProgress: 68,
    nextMilestone: "Complete 15 sessions",
  };

  const mockRecentSessions = [
    {
      id: "1",
      title: "Character Building Session",
      date: "2024-09-12",
      progress: 85,
      status: "completed",
    },
    {
      id: "2",
      title: "World Exploration",
      date: "2024-09-11",
      progress: 92,
      status: "completed",
    },
  ];

  const handleStartNewSession = () => {
    navigate("/session/new");
  };

  const handleViewCharacters = () => {
    navigate("/characters");
  };

  const handleExploreWorlds = () => {
    navigate("/worlds");
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome back, {user?.username || "Player"}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Continue your therapeutic gaming journey
        </Typography>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Avatar sx={{ bgcolor: "primary.main", mr: 2 }}>
                  <PlayArrow />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {mockStats.sessionsCompleted}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Sessions Completed
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Avatar sx={{ bgcolor: "success.main", mr: 2 }}>
                  <TrendingUp />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {mockStats.currentStreak}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Day Streak
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Avatar sx={{ bgcolor: "info.main", mr: 2 }}>
                  <Psychology />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {mockStats.totalProgress}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overall Progress
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Next Milestone
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {mockStats.nextMilestone}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={mockStats.totalProgress}
                sx={{ mt: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Quick Actions
          </Typography>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrow />}
              onClick={handleStartNewSession}
            >
              Start New Session
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<Person />}
              onClick={handleViewCharacters}
            >
              Manage Characters
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<Explore />}
              onClick={handleExploreWorlds}
            >
              Explore Worlds
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Recent Sessions */}
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Recent Sessions
          </Typography>
          <Grid container spacing={2}>
            {mockRecentSessions.map((session) => (
              <Grid item xs={12} md={6} key={session.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                      <Typography variant="h6">{session.title}</Typography>
                      <Chip
                        label={session.status}
                        color="success"
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {new Date(session.date).toLocaleDateString()}
                    </Typography>
                    <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
                      <Typography variant="body2" sx={{ mr: 1 }}>
                        Progress:
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={session.progress}
                        sx={{ flexGrow: 1, mr: 1 }}
                      />
                      <Typography variant="body2">
                        {session.progress}%
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default Dashboard;
