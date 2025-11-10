import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
} from '@mui/material';
import {
  VideoLibrary,
  AccountCircle,
  Dashboard as DashboardIcon,
  School,
  Assessment,
  CloudUpload,
  Menu as MenuIcon,
  Search as SearchIcon,
} from '@mui/icons-material';

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Best Practices', icon: <School />, path: '/practices' },
    { text: 'Upload Video', icon: <CloudUpload />, path: '/upload' },
    { text: 'Reports', icon: <Assessment />, path: '/reports' },
  ];

  // Admin-only menu items
  const adminItems = user?.role === 'admin' ? [
    { text: 'Admin Dashboard', icon: <Assessment />, path: '/admin' },
    { text: 'User Management', icon: <AccountCircle />, path: '/admin/users' },
    { text: 'Analytics', icon: <Assessment />, path: '/analytics' },
  ] : [];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(true)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <VideoLibrary sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            STAR Video Review
          </Typography>
          <IconButton color="inherit" onClick={() => navigate('/search')}>
            <SearchIcon />
          </IconButton>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.email} ({user?.role})
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <AccountCircle />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 250 }} role="presentation" onClick={() => setDrawerOpen(false)}>
          <List>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => navigate(item.path)}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
            {adminItems.length > 0 && (
              <>
                <Box sx={{ px: 2, py: 1, mt: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
                    ADMIN
                  </Typography>
                </Box>
                {adminItems.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton
                      selected={location.pathname === item.path}
                      onClick={() => navigate(item.path)}
                    >
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </>
            )}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1 }}>
        {children}
      </Box>

      <Box sx={{ 
        bgcolor: 'background.paper', 
        borderTop: 1, 
        borderColor: 'divider',
        p: 2,
        textAlign: 'center'
      }}>
        <Typography variant="caption" color="text.secondary">
          STAR Video Review System v3.0 - Backend: {process.env.REACT_APP_API_URL}
        </Typography>
      </Box>
    </Box>
  );
}

export default Layout;

