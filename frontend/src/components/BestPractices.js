import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getBestPractices } from '../services/api';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import { CheckCircle, Warning } from '@mui/icons-material';
import Layout from './Layout';

function BestPractices() {
  const [practices, setPractices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [category, setCategory] = useState('all');

  useEffect(() => {
    loadPractices();
  }, [category]);

  const loadPractices = async () => {
    try {
      setLoading(true);
      const params = category !== 'all' ? category : '';
      const response = await getBestPractices(params);
      setPractices(response.data.practices);
      setError('');
    } catch (err) {
      setError('Failed to load best practices');
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { value: 'all', label: 'All Practices' },
    { value: 'discrete_trial', label: 'Discrete Trial' },
    { value: 'pivotal_response', label: 'Pivotal Response Training' },
    { value: 'functional_routines', label: 'Functional Routines' },
  ];

  const positivePractices = practices.filter(p => p.is_positive);
  const negativePractices = practices.filter(p => !p.is_positive);

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Best Practices Library
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Evidence-based teaching practices for autism intervention
        </Typography>

        <Tabs value={category} onChange={(e, v) => setCategory(v)} sx={{ mb: 3 }}>
          {categories.map(cat => (
            <Tab key={cat.value} label={cat.label} value={cat.value} />
          ))}
        </Tabs>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Positive Practices */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
                Strengths to Look For ({positivePractices.length})
              </Typography>
              <Grid container spacing={2}>
                {positivePractices.map(practice => (
                  <Grid item xs={12} md={6} key={practice.id}>
                    <Card variant="outlined" sx={{ borderLeft: 3, borderColor: 'success.main' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {practice.title}
                        </Typography>
                        <Chip 
                          label={practice.category.replace('_', ' ')} 
                          size="small" 
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {practice.description}
                        </Typography>
                        {practice.criteria && (
                          <Typography variant="caption" display="block" sx={{ mt: 1, fontStyle: 'italic' }}>
                            Criteria: {practice.criteria}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>

            {/* Negative Practices */}
            {negativePractices.length > 0 && (
              <Box>
                <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <Warning sx={{ mr: 1, color: 'warning.main' }} />
                  Areas for Improvement ({negativePractices.length})
                </Typography>
                <Grid container spacing={2}>
                  {negativePractices.map(practice => (
                    <Grid item xs={12} md={6} key={practice.id}>
                      <Card variant="outlined" sx={{ borderLeft: 3, borderColor: 'warning.main' }}>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {practice.title}
                          </Typography>
                          <Chip 
                            label={practice.category.replace('_', ' ')} 
                            size="small" 
                            sx={{ mb: 1 }}
                          />
                          <Typography variant="body2" color="text.secondary">
                            {practice.description}
                          </Typography>
                          {practice.criteria && (
                            <Typography variant="caption" display="block" sx={{ mt: 1, fontStyle: 'italic' }}>
                              What to avoid: {practice.criteria}
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </>
        )}
      </Container>
    </Layout>
  );
}

export default BestPractices;

