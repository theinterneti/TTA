import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Chip,
} from '@mui/material';
import {
  AccountCircle,
  Dashboard,
  Person,
  Explore,
  Psychology,
  ExitToApp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { UserAccount, ServiceHealth } from '../../types/therapeutic';

interface NavigationBarProps {
  user: UserAccount | null;
  onLogout: () => void;
  serviceHealth: ServiceHealth | null;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ user, onLogout, serviceHealth }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    onLogout();
  };

  const handleProfileClick = () => {
    handleClose();
    navigate('/profile');
  };

  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          TTA Therapeutic Gaming
        </Typography>

        <Box sx={{ flexGrow: 1, display: 'flex', ml: 4 }}>
          <Button
            color="inherit"
            startIcon={<Dashboard />}
            onClick={() => navigate('/')}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            startIcon={<Person />}
            onClick={() => navigate('/characters')}
          >
            Characters
          </Button>
          <Button
            color="inherit"
            startIcon={<Explore />}
            onClick={() => navigate('/worlds')}
          >
            Worlds
          </Button>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {serviceHealth && (
            <Chip
              label={serviceHealth.overallStatus === 'healthy' ? 'Online' : 'Offline'}
              color={serviceHealth.overallStatus === 'healthy' ? 'success' : 'error'}
              size="small"
              sx={{ mr: 2 }}
            />
          )}

          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
              <AccountCircle />
            </Avatar>
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleProfileClick}>
              <Person sx={{ mr: 1 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ExitToApp sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavigationBar;
