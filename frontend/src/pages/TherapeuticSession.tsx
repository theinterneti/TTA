import React from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Box, Card, CardContent, Button } from '@mui/material';
import { PlayArrow, Pause, Stop } from '@mui/icons-material';

const TherapeuticSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Therapeutic Session
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Session ID: {sessionId}
        </Typography>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Session Controls
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="contained" startIcon={<PlayArrow />}>
              Start Session
            </Button>
            <Button variant="outlined" startIcon={<Pause />}>
              Pause
            </Button>
            <Button variant="outlined" startIcon={<Stop />}>
              End Session
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Session Content
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Therapeutic session content will be displayed here.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default TherapeuticSession;
