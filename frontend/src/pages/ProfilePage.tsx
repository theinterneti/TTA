import React from 'react';
import { Container, Typography, Box, Card, CardContent, Avatar, Button } from '@mui/material';
import { Person, Edit, Settings } from '@mui/icons-material';
import { UserAccount } from '../types/therapeutic';

interface ProfilePageProps {
  user: UserAccount | null;
}

const ProfilePage: React.FC<ProfilePageProps> = ({ user }) => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your account and therapeutic preferences
        </Typography>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main' }}>
              <Person fontSize="large" />
            </Avatar>
            <Box>
              <Typography variant="h5" gutterBottom>
                {user?.username || 'User'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Member since {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="contained" startIcon={<Edit />}>
              Edit Profile
            </Button>
            <Button variant="outlined" startIcon={<Settings />}>
              Settings
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Therapeutic Progress
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Your therapeutic journey and achievements will be displayed here.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ProfilePage;
