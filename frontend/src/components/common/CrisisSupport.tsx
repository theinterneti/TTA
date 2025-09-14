/**
 * TTA Crisis Support Component
 *
 * Provides emergency crisis support functionality.
 */

import React, { useState } from 'react';
import {
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Box,
  Alert,
  Link,
} from '@mui/material';
import { Phone, Close } from '@mui/icons-material';

const CrisisSupport: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = () => {
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const emergencyContacts = [
    {
      name: 'National Suicide Prevention Lifeline',
      phone: '988',
      description: '24/7 crisis support',
    },
    {
      name: 'Crisis Text Line',
      phone: 'Text HOME to 741741',
      description: '24/7 text-based crisis support',
    },
    {
      name: 'Emergency Services',
      phone: '911',
      description: 'For immediate emergencies',
    },
  ];

  return (
    <>
      {/* Crisis Support FAB */}
      <Fab
        color="error"
        aria-label="crisis support"
        onClick={handleOpen}
        sx={{
          position: 'fixed',
          bottom: 16,
          left: 16,
          zIndex: 1000,
        }}
      >
        <Phone />
      </Fab>

      {/* Crisis Support Dialog */}
      <Dialog
        open={isOpen}
        onClose={handleClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">Crisis Support</Typography>
            <Button
              onClick={handleClose}
              sx={{ minWidth: 'auto', p: 1 }}
            >
              <Close />
            </Button>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 3 }}>
            If you are experiencing a mental health crisis or having thoughts of self-harm, 
            please reach out for help immediately.
          </Alert>

          <Typography variant="h6" gutterBottom>
            Emergency Contacts
          </Typography>

          <Box sx={{ mb: 3 }}>
            {emergencyContacts.map((contact, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {contact.name}
                </Typography>
                <Typography variant="h6" color="primary" sx={{ my: 1 }}>
                  {contact.phone}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {contact.description}
                </Typography>
              </Box>
            ))}
          </Box>

          <Typography variant="h6" gutterBottom>
            Additional Resources
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Link href="https://www.mentalhealth.gov" target="_blank" rel="noopener">
              MentalHealth.gov
            </Link>
            <Typography variant="body2" color="text.secondary">
              Mental health information and resources
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Link href="https://www.nami.org" target="_blank" rel="noopener">
              National Alliance on Mental Illness (NAMI)
            </Link>
            <Typography variant="body2" color="text.secondary">
              Support, education, and advocacy
            </Typography>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} variant="contained">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CrisisSupport;
