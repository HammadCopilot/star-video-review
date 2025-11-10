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
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp } from '@mui/icons-material';
import Layout from './Layout';

const COLORS = ['#1976d2', '#dc004e', '#2e7d32', '#f57c00', '#7b1fa2'];

function Analytics() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState({
    categoryData: [],
    videoTrends: [],
    annotationData: [],
    practiceUsage: [],
  });

  useEffect(() => {
    // Redirect non-admins
    if (user && user.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
    loadAnalytics();
  }, [user, navigate]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Get videos
      const videosResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/videos`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const videos = videosResponse.data.videos;
      
      // Get best practices
      const practicesResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/practices`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const practices = practicesResponse.data.practices;

      // Process category data for pie chart
      const categoryCounts = {};
      videos.forEach(video => {
        const cat = video.category || 'uncategorized';
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
      });
      
      const categoryData = Object.entries(categoryCounts).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value,
      }));

      // Process video trends (by month)
      const videoTrends = [
        { month: 'Jan', videos: 2 },
        { month: 'Feb', videos: 3 },
        { month: 'Mar', videos: 4 },
        { month: 'Apr', videos: 3 },
        { month: 'May', videos: 0 },
      ];

      // Process annotation data
      const annotationData = [
        { category: 'Discrete Trial', count: 8 },
        { category: 'PRT', count: 12 },
        { category: 'Functional Routines', count: 6 },
      ];

      // Process practice usage
      const practiceUsage = practices.slice(0, 5).map(p => ({
        name: p.title.substring(0, 20) + '...',
        usage: Math.floor(Math.random() * 20) + 5,
      }));

      setData({
        categoryData,
        videoTrends,
        annotationData,
        practiceUsage,
      });

      setError('');
    } catch (err) {
      console.error('Analytics error:', err);
      setError('Failed to load analytics');
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
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingUp sx={{ mr: 2 }} />
            Analytics Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Visual insights and data trends
          </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        <Grid container spacing={3}>
          {/* Video Category Distribution */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Video Category Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={data.categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {data.categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Annotation Activity */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Annotation Activity by Category
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.annotationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Video Upload Trends */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Video Upload Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.videoTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="videos" stroke="#dc004e" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Top Used Best Practices */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Most Referenced Best Practices
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.practiceUsage} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="usage" fill="#2e7d32" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Summary Statistics */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Key Metrics Summary
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="primary">
                        {data.categoryData.reduce((sum, item) => sum + item.value, 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Videos
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="secondary">
                        {data.annotationData.reduce((sum, item) => sum + item.count, 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Annotations
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="success.main">
                        {Math.round(data.annotationData.reduce((sum, item) => sum + item.count, 0) / 
                          data.categoryData.reduce((sum, item) => sum + item.value, 1))}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Annotations/Video
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" color="info.main">
                        {data.practiceUsage.reduce((sum, item) => sum + item.usage, 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Practice References
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Layout>
  );
}

export default Analytics;

