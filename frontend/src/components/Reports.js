import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getVideoReport } from '../services/api';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Button,
  Menu,
  MenuItem,
} from '@mui/material';
import { Assessment, CheckCircle, Warning, TrendingUp, Download, FileDownload } from '@mui/icons-material';
import Layout from './Layout';

function Reports() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exportAnchor, setExportAnchor] = useState(null);

  useEffect(() => {
    if (id) {
      loadReport();
    }
  }, [id]);

  const loadReport = async () => {
    try {
      setLoading(true);
      const response = await getVideoReport(id);
      setReport(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `video_report_${id}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    setExportAnchor(null);
  };

  const handleExportCSV = () => {
    // Create CSV from report data
    let csv = 'Category,Practice,Timestamp,Comment\n';
    
    if (report.strengths) {
      report.strengths.forEach(item => {
        csv += `Strength,"${item.practice}","${item.timestamp}","${item.comment || ''}"\n`;
      });
    }
    
    if (report.improvements) {
      report.improvements.forEach(item => {
        csv += `Improvement,"${item.practice}","${item.timestamp}","${item.comment || ''}"\n`;
      });
    }

    const dataBlob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `video_report_${id}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    setExportAnchor(null);
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

  if (error || !report) {
    return (
      <Layout>
        <Container>
          <Alert severity="error" sx={{ mt: 4 }}>
            {error || 'No report available'}
          </Alert>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Assessment sx={{ mr: 2 }} />
              Video Review Report
            </Typography>
            <Typography variant="h6" color="text.secondary">
              {report.video?.title}
            </Typography>
            <Chip 
              label={report.video?.category?.replace('_', ' ')} 
              sx={{ mt: 1 }} 
            />
          </Box>
          <Box>
            <Button
              variant="contained"
              startIcon={<Download />}
              onClick={(e) => setExportAnchor(e.currentTarget)}
            >
              Export
            </Button>
            <Menu
              anchorEl={exportAnchor}
              open={Boolean(exportAnchor)}
              onClose={() => setExportAnchor(null)}
            >
              <MenuItem onClick={handleExportJSON}>
                <FileDownload sx={{ mr: 1 }} />
                Export as JSON
              </MenuItem>
              <MenuItem onClick={handleExportCSV}>
                <FileDownload sx={{ mr: 1 }} />
                Export as CSV
              </MenuItem>
            </Menu>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Assessment color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Total Annotations
                  </Typography>
                </Box>
                <Typography variant="h3">
                  {report.summary?.total_annotations || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Strengths
                  </Typography>
                </Box>
                <Typography variant="h3" color="success.main">
                  {report.summary?.positive_indicators || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Warning color="warning" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Improvements
                  </Typography>
                </Box>
                <Typography variant="h3" color="warning.main">
                  {report.summary?.areas_for_improvement || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUp color="info" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Coverage
                  </Typography>
                </Box>
                <Typography variant="h3" color="info.main">
                  {report.summary?.practices_coverage_percent || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Strengths */}
        {report.strengths && report.strengths.length > 0 && (
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
              Identified Strengths
            </Typography>
            <Divider sx={{ my: 2 }} />
            <List>
              {report.strengths.map((strength, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={strength.practice}
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.secondary">
                          {strength.timestamp} - {strength.comment}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        {/* Areas for Improvement */}
        {report.improvements && report.improvements.length > 0 && (
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Warning sx={{ mr: 1, color: 'warning.main' }} />
              Areas for Improvement
            </Typography>
            <Divider sx={{ my: 2 }} />
            <List>
              {report.improvements.map((improvement, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={improvement.practice}
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.secondary">
                          {improvement.timestamp} - {improvement.comment}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        {/* Breakdown by Category */}
        {report.breakdown && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Annotation Breakdown
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  By Category
                </Typography>
                {Object.entries(report.breakdown.by_category || {}).map(([key, value]) => (
                  <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{key.replace('_', ' ')}</Typography>
                    <Chip label={value} size="small" />
                  </Box>
                ))}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  By Type
                </Typography>
                {Object.entries(report.breakdown.by_type || {}).map(([key, value]) => (
                  <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{key.replace('_', ' ')}</Typography>
                    <Chip label={value} size="small" />
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Paper>
        )}

        <Box sx={{ mt: 3 }}>
          <Typography variant="caption" color="text.secondary">
            Report generated: {new Date(report.generated_at).toLocaleString()}
          </Typography>
        </Box>
      </Container>
    </Layout>
  );
}

export default Reports;

