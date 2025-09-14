import React from 'react';
import { Container, Typography, Box, Card, CardContent, Button, Grid } from '@mui/material';
import { Explore, Add } from '@mui/icons-material';

const WorldExplorer: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          World Explorer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover and create therapeutic worlds for your gaming experiences
        </Typography>
      </Box>

      <Button variant="contained" startIcon={<Add />} sx={{ mb: 3 }}>
        Create New World
      </Button>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Explore sx={{ mr: 1 }} />
                <Typography variant="h6">Sample World</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                A peaceful therapeutic environment for exploration and growth.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default WorldExplorer;
