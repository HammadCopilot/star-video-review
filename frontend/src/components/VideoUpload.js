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
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import { CloudUpload, Link as LinkIcon, VideoFile } from '@mui/icons-material';
import Layout from './Layout';

function VideoUpload() {
  const navigate = useNavigate();
  const [uploadType, setUploadType] = useState('url'); // 'url' or 'file'
  const [formData, setFormData] = useState({
    title: '',
    url: '',
    category: '',
    description: '',
  });
  const [selectedFile, setSelectedFile] = useState(null);
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
      if (uploadType === 'file') {
        if (!selectedFile) {
          setError('Please select a video file');
          setLoading(false);
          return;
        }
        
        // Upload file using FormData
        const formDataToSend = new FormData();
        formDataToSend.append('file', selectedFile);
        formDataToSend.append('title', formData.title);
        formDataToSend.append('category', formData.category);
        if (formData.description) {
          formDataToSend.append('description', formData.description);
        }
        
        const token = localStorage.getItem('token');
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5001'}/api/videos`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formDataToSend,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to upload video');
        }
        
        setSuccess('Video uploaded successfully! You can now analyze it with AI.');
      } else {
        // URL upload
        await createVideo(formData);
        setSuccess('Video URL added successfully!');
      }
      
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

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      // Auto-fill title if empty
      if (!formData.title) {
        setFormData({ ...formData, title: file.name.replace(/\.[^/.]+$/, '') });
      }
    }
  };

  return (
    <Layout>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <CloudUpload sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
            <Typography variant="h4">Add New Video</Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Upload Method
            </Typography>
            <ToggleButtonGroup
              value={uploadType}
              exclusive
              onChange={(e, newType) => newType && setUploadType(newType)}
              fullWidth
              disabled={loading}
            >
              <ToggleButton value="file">
                <VideoFile sx={{ mr: 1 }} />
                Upload File (For AI Analysis)
              </ToggleButton>
              <ToggleButton value="url">
                <LinkIcon sx={{ mr: 1 }} />
                External URL
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          <form onSubmit={handleSubmit}>
            {uploadType === 'file' && (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Upload local video files to enable AI analysis. Supported formats: MP4, AVI, MOV, MKV
                  </Typography>
                </Alert>
                
                <Button
                  variant="outlined"
                  component="label"
                  fullWidth
                  sx={{ mb: 2, py: 2 }}
                  disabled={loading}
                >
                  <CloudUpload sx={{ mr: 1 }} />
                  {selectedFile ? selectedFile.name : 'Choose Video File'}
                  <input
                    type="file"
                    hidden
                    accept="video/*"
                    onChange={handleFileChange}
                  />
                </Button>
              </>
            )}

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

            {uploadType === 'url' && (
              <TextField
                label="Video URL"
                name="url"
                fullWidth
                margin="normal"
                value={formData.url}
                onChange={handleChange}
                required
                disabled={loading}
                helperText="External video URL (YouTube, Vimeo, JWPlayer, etc.) - Note: AI analysis not available for URLs"
              />
            )}

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

