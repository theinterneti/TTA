import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  Alert,
  Collapse,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  People,
  Assessment,
  Warning,
  Settings,
  Logout,
  AccountCircle,
  Notifications,
  Security,
  ExpandLess,
  ExpandMore,
  LocalHospital,
  Timeline,
  Analytics,
  Report,
} from '@mui/icons-material';
import {
  useAuth,
  useHIPAACompliance,
  useCrisisSupport,
  CrisisSupportButton,
  ThemeSelector,
} from '@tta/shared-components';

const drawerWidth = 280;

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  children?: NavigationItem[];
  requiresAuth?: boolean;
  clinicalOnly?: boolean;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <Dashboard />,
    path: '/dashboard',
    requiresAuth: true,
  },
  {
    id: 'patients',
    label: 'Patient Management',
    icon: <People />,
    path: '/patients',
    requiresAuth: true,
    clinicalOnly: true,
    children: [
      {
        id: 'patient-list',
        label: 'Patient List',
        icon: <People />,
        path: '/patients/list',
      },
      {
        id: 'patient-monitoring',
        label: 'Real-time Monitoring',
        icon: <Timeline />,
        path: '/patients/monitoring',
      },
    ],
  },
  {
    id: 'assessments',
    label: 'Clinical Assessments',
    icon: <Assessment />,
    path: '/assessments',
    requiresAuth: true,
    clinicalOnly: true,
  },
  {
    id: 'crisis',
    label: 'Crisis Management',
    icon: <Warning />,
    path: '/crisis',
    requiresAuth: true,
    clinicalOnly: true,
  },
  {
    id: 'analytics',
    label: 'Analytics & Reports',
    icon: <Analytics />,
    path: '/analytics',
    requiresAuth: true,
    clinicalOnly: true,
    children: [
      {
        id: 'outcomes',
        label: 'Outcome Measurements',
        icon: <Report />,
        path: '/analytics/outcomes',
      },
      {
        id: 'compliance',
        label: 'Compliance Reports',
        icon: <Security />,
        path: '/analytics/compliance',
      },
    ],
  },
];

const ClinicalLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { complianceStatus, securityEvents } = useHIPAACompliance();
  const { lastAssessment, isMonitoring } = useCrisisSupport();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>(['patients', 'analytics']);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleProfileMenuClose();
    await logout();
    navigate('/login');
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (mobileOpen) {
      setMobileOpen(false);
    }
  };

  const handleExpandClick = (itemId: string) => {
    setExpandedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const renderNavigationItem = (item: NavigationItem, depth = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.includes(item.id);
    const active = isActive(item.path);

    return (
      <React.Fragment key={item.id}>
        <ListItem disablePadding sx={{ pl: depth * 2 }}>
          <ListItemButton
            selected={active}
            onClick={() => {
              if (hasChildren) {
                handleExpandClick(item.id);
              } else {
                handleNavigate(item.path);
              }
            }}
            sx={{
              minHeight: 48,
              '&.Mui-selected': {
                bgcolor: 'primary.light',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.label}
              primaryTypographyProps={{
                fontSize: depth > 0 ? '0.875rem' : '1rem',
                fontWeight: active ? 600 : 400,
              }}
            />
            {hasChildren && (
              isExpanded ? <ExpandLess /> : <ExpandMore />
            )}
          </ListItemButton>
        </ListItem>

        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderNavigationItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawer = (
    <Box>
      <Box
        sx={{
          p: 2,
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          textAlign: 'center',
        }}
      >
        <Avatar
          sx={{
            bgcolor: 'primary.light',
            width: 48,
            height: 48,
            mx: 'auto',
            mb: 1,
          }}
        >
          <LocalHospital />
        </Avatar>
        <Typography variant="h6" noWrap>
          TTA Clinical
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          Healthcare Provider Portal
        </Typography>
      </Box>

      <Divider />

      {/* Compliance Status Alert */}
      {complianceStatus !== 'compliant' && (
        <Box sx={{ p: 2 }}>
          <Alert
            severity={complianceStatus === 'violation' ? 'error' : 'warning'}
            size="small"
          >
            Compliance: {complianceStatus}
          </Alert>
        </Box>
      )}

      {/* Crisis Monitoring Status */}
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: isMonitoring ? 'success.main' : 'error.main',
            }}
          />
          <Typography variant="caption" color="text.secondary">
            Crisis Monitoring {isMonitoring ? 'Active' : 'Inactive'}
          </Typography>
        </Box>
        {lastAssessment && lastAssessment.crisis_level >= 3 && (
          <CrisisSupportButton variant="emergency" className="w-full" />
        )}
      </Box>

      <Divider />

      <List>
        {navigationItems.map(item => renderNavigationItem(item))}
      </List>

      <Divider />

      {/* Theme Selector */}
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          Interface Theme
        </Typography>
        <ThemeSelector showLabels={false} />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Clinical Dashboard
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Notifications */}
            <Tooltip title="Security Events">
              <IconButton color="inherit">
                <Badge badgeContent={securityEvents.length} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* Crisis Support */}
            <CrisisSupportButton variant="secondary" />

            {/* Profile Menu */}
            <Tooltip title="Account settings">
              <IconButton
                onClick={handleProfileMenuOpen}
                color="inherit"
                sx={{ ml: 1 }}
              >
                <AccountCircle />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        onClick={handleProfileMenuClose}
      >
        <MenuItem disabled>
          <AccountCircle sx={{ mr: 1 }} />
          Dr. {user?.username || 'Smith'}
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => navigate('/settings')}>
          <Settings sx={{ mr: 1 }} />
          Settings
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <Logout sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 0,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default ClinicalLayout;
