import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createVideo } from '../services/api';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import { Link as LinkIcon } from '@mui/icons-material';
import Layout from './Layout';

function VideoUpload() {
  const navigate = useNavigate();
  // File uploads are DISABLED to save disk space - URL only mode
  const [formData, setFormData] = useState({
    title: '',
    url: '',
    category: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const categories = [
    { value: 'discrete_trial', label: 'Discrete Trial' },
    { value: 'pivotal_response', label: 'Pivotal Response Training' },
    { value: 'functional_routines', label: 'Functional Routines' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // URL only upload
      await createVideo(formData);
      setSuccess('Video URL added successfully! You can now analyze it with AI.');
      
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err) {
      setError(err.message || err.response?.data?.error || 'Failed to add video');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <Layout>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <LinkIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
            <Typography variant="h4">Add New Video by URL</Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2" fontWeight="bold" gutterBottom>
              File uploads are disabled to save disk space
            </Typography>
            <Typography variant="body2">
              Videos will be downloaded temporarily for AI analysis and then deleted automatically. 
              Please provide a direct video URL that's accessible online.
            </Typography>
          </Alert>

          <form onSubmit={handleSubmit}>

            <TextField
              label="Video URL"
              name="url"
              fullWidth
              margin="normal"
              value={formData.url}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="https://example.com/video.mp4"
              helperText="Direct video URL (must be publicly accessible for analysis)"
            />

            <TextField
              label="Video Title"
              name="title"
              fullWidth
              margin="normal"
              value={formData.title}
              onChange={handleChange}
              required
              disabled={loading}
            />

            <TextField
              label="Category"
              name="category"
              select
              fullWidth
              margin="normal"
              value={formData.category}
              onChange={handleChange}
              required
              disabled={loading}
            >
              {categories.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              label="Description"
              name="description"
              fullWidth
              margin="normal"
              multiline
              rows={4}
              value={formData.description}
              onChange={handleChange}
              disabled={loading}
              helperText="Optional description of the video content"
            />

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Add Video'}
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/dashboard')}
                disabled={loading}
              >
                Cancel
              </Button>
            </Box>
          </form>
        </Paper>

      </Container>
    </Layout>
  );
}

export default VideoUpload;

