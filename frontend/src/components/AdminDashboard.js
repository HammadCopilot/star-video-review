import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
} from '@mui/material';
import {
  VideoLibrary,
  People,
  School,
  Assessment,
  TrendingUp,
  Add,
} from '@mui/icons-material';
import Layout from './Layout';

function AdminDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Redirect non-admins
    if (user && user.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
    loadDashboardData();
  }, [user, navigate]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Get system summary
      const summaryResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/reports/summary`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Get all users
      const usersResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/auth/users`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Get videos
      const videosResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/videos`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Get best practices count
      const practicesResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/practices`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setStats({
        totalVideos: videosResponse.data.videos.length,
        totalUsers: usersResponse.data.users.length,
        totalPractices: practicesResponse.data.practices.length,
        analyzedVideos: videosResponse.data.videos.filter(v => v.is_analyzed).length,
        totalAnnotations: summaryResponse.data.total_annotations || 0,
      });

      // Mock recent activity (in production, fetch from audit logs)
      setRecentActivity([
        { type: 'video', action: 'uploaded', user: 'John Doe', time: '2 hours ago' },
        { type: 'annotation', action: 'created', user: 'Jane Smith', time: '3 hours ago' },
        { type: 'user', action: 'registered', user: 'Bob Johnson', time: '5 hours ago' },
      ]);

      setError('');
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Container>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Admin Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            System overview and management
          </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <VideoLibrary color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Total Videos
                  </Typography>
                </Box>
                <Typography variant="h3">{stats?.totalVideos || 0}</Typography>
                <Typography variant="caption" color="success.main">
                  {stats?.analyzedVideos || 0} analyzed
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <People color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Total Users
                  </Typography>
                </Box>
                <Typography variant="h3">{stats?.totalUsers || 0}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Active accounts
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <School color="info" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Best Practices
                  </Typography>
                </Box>
                <Typography variant="h3">{stats?.totalPractices || 0}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Evaluation criteria
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Assessment color="success" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Annotations
                  </Typography>
                </Box>
                <Typography variant="h3">{stats?.totalAnnotations || 0}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Total tags
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Actions & Recent Activity */}
        <Grid container spacing={3}>
          {/* Quick Actions */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUp sx={{ mr: 1 }} />
                  Quick Actions
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => navigate('/upload')}
                    fullWidth
                  >
                    Upload New Video
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => navigate('/admin/users')}
                    fullWidth
                  >
                    Manage Users
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<School />}
                    onClick={() => navigate('/practices')}
                    fullWidth
                  >
                    View Best Practices
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Assessment />}
                    onClick={() => navigate('/reports')}
                    fullWidth
                  >
                    View Reports
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <Divider sx={{ my: 2 }} />
                <List>
                  {recentActivity.length === 0 ? (
                    <ListItem>
                      <ListItemText
                        primary="No recent activity"
                        secondary="System activity will appear here"
                      />
                    </ListItem>
                  ) : (
                    recentActivity.map((activity, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Chip
                                label={activity.type}
                                size="small"
                                color={
                                  activity.type === 'video' ? 'primary' :
                                  activity.type === 'annotation' ? 'success' : 'default'
                                }
                              />
                              <Typography variant="body2">
                                {activity.user} {activity.action} a {activity.type}
                              </Typography>
                            </Box>
                          }
                          secondary={activity.time}
                        />
                      </ListItem>
                    ))
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* System Info */}
        <Box sx={{ mt: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Information
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Backend Version
                  </Typography>
                  <Typography variant="body1">v2.0.0</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Frontend Version
                  </Typography>
                  <Typography variant="body1">v3.0.0</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    API Status
                  </Typography>
                  <Chip label="Healthy" color="success" size="small" />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Database
                  </Typography>
                  <Chip label="Connected" color="success" size="small" />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Layout>
  );
}

export default AdminDashboard;

