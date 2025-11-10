import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVideo, getAnnotations, getVideoReport, createAnnotation, analyzeVideo, getAnalysisStatus } from '../services/api';
import { useNotification } from '../context/NotificationContext';
import ReactPlayer from 'react-player';
import {
  Container,
  Paper,
  Typography,
  Box,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
} from '@mui/material';
import { PlayCircle, Assessment, Add, Psychology } from '@mui/icons-material';
import Layout from './Layout';

function VideoDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showSuccess, showError, showInfo } = useNotification();
  const [video, setVideo] = useState(null);
  const [annotations, setAnnotations] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [annotationDialog, setAnnotationDialog] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStage, setAnalysisStage] = useState('');
  const progressIntervalRef = useRef(null);
  const [newAnnotation, setNewAnnotation] = useState({
    start_time: 0,
    comment: '',
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [videoRes, annotationsRes] = await Promise.all([
        getVideo(id),
        getAnnotations(id),
      ]);
      setVideo(videoRes.data.video);
      setAnnotations(annotationsRes.data.annotations);
      
      // Try to load report
      try {
        const reportRes = await getVideoReport(id);
        setReport(reportRes.data);
      } catch (err) {
        // Report might not exist yet
      }
      
      setError('');
    } catch (err) {
      setError('Failed to load video details');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAnnotation = async () => {
    try {
      await createAnnotation({
        video_id: parseInt(id),
        start_time: parseFloat(newAnnotation.start_time),
        practice_category: video.category || 'general',
        comment: newAnnotation.comment,
      });
      setAnnotationDialog(false);
      setNewAnnotation({ start_time: 0, comment: '' });
      showSuccess('Annotation created successfully!');
      loadData();
    } catch (err) {
      showError('Failed to create annotation');
    }
  };

  const checkAnalysisProgress = async () => {
    try {
      const response = await getAnalysisStatus(id);
      const { progress, stage, analysis_status } = response.data;
      
      console.log('📊 Progress update:', { progress, stage, analysis_status });
      setAnalysisProgress(progress || 0);
      setAnalysisStage(stage || 'Processing...');
      
      // If complete or failed, stop polling
      if (analysis_status === 'completed' || analysis_status === 'failed') {
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
          progressIntervalRef.current = null;
        }
        setAnalyzing(false);
        
        if (analysis_status === 'completed') {
          showSuccess('Video analyzed successfully! Check annotations and report.');
          loadData();
        } else {
          showError('Analysis failed. Please try again.');
        }
      }
    } catch (err) {
      console.error('Progress check error:', err);
    }
  };

  const handleAnalyzeVideo = async () => {
    try {
      setAnalyzing(true);
      setAnalysisProgress(0);
      setAnalysisStage('Starting analysis...');
      showInfo('AI analysis started. This may take 1-2 minutes...');
      
      // Start polling for progress immediately
      progressIntervalRef.current = setInterval(checkAnalysisProgress, 2000);
      
      // Start analysis (don't await - let it run in background)
      analyzeVideo(id).catch(err => {
        const message = err.response?.data?.error || 'Failed to analyze video';
        showError(message);
        setAnalyzing(false);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
          progressIntervalRef.current = null;
        }
      });
      
    } catch (err) {
      const message = err.response?.data?.error || 'Failed to analyze video';
      showError(message);
      setAnalyzing(false);
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
    }
  };

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

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

  if (!video) {
    return (
      <Layout>
        <Container>
          <Alert severity="error">Video not found</Alert>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Typography variant="h4">
              {video.title}
            </Typography>
            {!analyzing && (
              <Button
                variant="contained"
                color="secondary"
                startIcon={<Psychology />}
                onClick={handleAnalyzeVideo}
              >
                {video.is_analyzed ? 'Re-Analyze with AI' : 'AI Analyze'}
              </Button>
            )}
          </Box>
          
          {/* Analysis Progress Bar */}
          {analyzing && (
            <Card sx={{ mb: 2, bgcolor: 'primary.50' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CircularProgress size={24} sx={{ mr: 2 }} />
                  <Typography variant="h6" color="primary">
                    AI Analysis in Progress...
                  </Typography>
                </Box>
                <Box sx={{ mb: 1 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={analysisProgress} 
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    {analysisStage}
                  </Typography>
                  <Typography variant="body2" color="primary" fontWeight="bold">
                    {analysisProgress}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            {video.category && (
              <Chip label={video.category.replace('_', ' ')} color="primary" />
            )}
            <Chip label={video.source_type} variant="outlined" />
            {video.is_analyzed && <Chip label="AI Analyzed" color="success" />}
          </Box>
          {video.description && (
            <Typography variant="body1" color="text.secondary">
              {video.description}
            </Typography>
          )}
        </Box>

        <Grid container spacing={3}>
          {/* Video Player */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3}>
              {video.url ? (
                <ReactPlayer
                  url={video.url}
                  width="100%"
                  height="500px"
                  controls
                />
              ) : video.source_type === 'local' && video.file_path ? (
                <ReactPlayer
                  url={`${process.env.REACT_APP_API_URL || 'http://localhost:5001'}/api/videos/${video.id}/stream?token=${localStorage.getItem('token')}`}
                  width="100%"
                  height="500px"
                  controls
                  config={{
                    file: {
                      attributes: {
                        controlsList: 'nodownload'
                      }
                    }
                  }}
                />
              ) : (
                <Box sx={{ p: 4, textAlign: 'center' }}>
                  <PlayCircle sx={{ fontSize: 60, color: 'text.secondary' }} />
                  <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                    Video file not available
                  </Typography>
                </Box>
              )}
            </Paper>

            {/* Annotations */}
            <Box sx={{ mt: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5">
                  Annotations ({annotations.length})
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setAnnotationDialog(true)}
                >
                  Add Note
                </Button>
              </Box>

              {annotations.length === 0 ? (
                <Alert severity="info">No annotations yet. Add one to get started!</Alert>
              ) : (
                annotations.map((ann) => {
                  // Determine if this is a strength or improvement based on comment
                  const isStrength = ann.comment.includes('✅ STRENGTH');
                  const isImprovement = ann.comment.includes('⚠️ IMPROVEMENT');
                  
                  // Format timestamp (show minutes:seconds if > 60s)
                  const formatTime = (seconds) => {
                    const mins = Math.floor(seconds / 60);
                    const secs = Math.floor(seconds % 60);
                    return mins > 0 ? `${mins}:${String(secs).padStart(2, '0')}` : `${secs}s`;
                  };
                  
                  return (
                    <Card 
                      key={ann.id} 
                      sx={{ 
                        mb: 2,
                        borderLeft: isStrength ? '4px solid #4caf50' : 
                                   isImprovement ? '4px solid #ff9800' : 
                                   '4px solid #e0e0e0'
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Chip 
                            label={formatTime(ann.start_time)} 
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {isStrength && (
                              <Chip 
                                label="Strength" 
                                size="small" 
                                color="success"
                              />
                            )}
                            {isImprovement && (
                              <Chip 
                                label="Improvement" 
                                size="small" 
                                color="warning"
                              />
                            )}
                            <Chip 
                              label={ann.annotation_type === 'ai_generated' ? 'AI Generated' : ann.annotation_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} 
                              size="small" 
                              color={ann.annotation_type === 'ai_generated' ? 'secondary' : 'default'}
                            />
                          </Box>
                        </Box>
                        <Typography variant="body2">
                          {ann.comment}
                        </Typography>
                        {ann.practice && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            Practice: {ann.practice.title}
                          </Typography>
                        )}
                        {ann.confidence_score && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                            Confidence: {Math.round(ann.confidence_score * 100)}%
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </Box>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            {/* Report Summary */}
            {report && (
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Assessment sx={{ mr: 1 }} />
                    Report Summary
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Total Annotations
                    </Typography>
                    <Typography variant="h4">
                      {report.summary?.total_annotations || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Strengths Identified
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {report.summary?.positive_indicators || 0}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Areas for Improvement
                    </Typography>
                    <Typography variant="h4" color="warning.main">
                      {report.summary?.areas_for_improvement || 0}
                    </Typography>
                  </Box>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => navigate(`/reports/${id}`)}
                  >
                    View Full Report
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Video Info */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Video Information
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Uploaded By
                  </Typography>
                  <Typography variant="body1">
                    {video.uploader?.first_name} {video.uploader?.last_name}
                  </Typography>
                </Box>
                {video.duration && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Duration
                    </Typography>
                    <Typography variant="body1">
                      {Math.floor(video.duration / 60)}:{String(Math.floor(video.duration % 60)).padStart(2, '0')}
                    </Typography>
                  </Box>
                )}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Analysis Status
                  </Typography>
                  <Typography variant="body1">
                    {video.analysis_status}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Add Annotation Dialog */}
        <Dialog open={annotationDialog} onClose={() => setAnnotationDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Annotation</DialogTitle>
          <DialogContent>
            <TextField
              label="Timestamp (seconds)"
              type="number"
              fullWidth
              margin="normal"
              value={newAnnotation.start_time}
              onChange={(e) => setNewAnnotation({ ...newAnnotation, start_time: e.target.value })}
            />
            <TextField
              label="Comment"
              multiline
              rows={4}
              fullWidth
              margin="normal"
              value={newAnnotation.comment}
              onChange={(e) => setNewAnnotation({ ...newAnnotation, comment: e.target.value })}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAnnotationDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateAnnotation} variant="contained">
              Add
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Layout>
  );
}

export default VideoDetails;

