import React, { useState, useEffect } from 'react';
import { getVideos } from '../services/api';
import {
  Container,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  CardActionArea,
} from '@mui/material';
import {
  PlayCircleOutline,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Layout from './Layout';
import VideoThumbnail from './VideoThumbnail';

function Dashboard() {
  const navigate = useNavigate();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadVideos();
  }, [filter]);

  const loadVideos = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { category: filter } : {};
      const response = await getVideos(params);
      setVideos(response.data.videos);
      setError('');
    } catch (err) {
      setError('Failed to load videos');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      discrete_trial: 'primary',
      pivotal_response: 'secondary',
      functional_routines: 'success',
    };
    return colors[category] || 'default';
  };

  const getCategoryLabel = (category) => {
    const labels = {
      discrete_trial: 'Discrete Trial',
      pivotal_response: 'PRT',
      functional_routines: 'Functional Routines',
    };
    return labels[category] || category;
  };

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4">
            Video Library
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant={filter === 'all' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setFilter('all')}
            >
              All ({videos.length})
            </Button>
            <Button
              variant={filter === 'discrete_trial' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setFilter('discrete_trial')}
            >
              Discrete Trial
            </Button>
            <Button
              variant={filter === 'pivotal_response' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setFilter('pivotal_response')}
            >
              PRT
            </Button>
            <Button
              variant={filter === 'functional_routines' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setFilter('functional_routines')}
            >
              Functional Routines
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {videos.map((video) => (
              <Grid item xs={12} sm={6} md={4} key={video.id}>
                <Card>
                  <CardActionArea onClick={() => navigate(`/video/${video.id}`)}>
                    <VideoThumbnail video={video} height={180} />
                  </CardActionArea>
                  <CardContent>
                    <Typography variant="h6" component="div" gutterBottom>
                      {video.title}
                    </Typography>

                    {video.category && (
                      <Chip
                        label={getCategoryLabel(video.category)}
                        size="small"
                        color={getCategoryColor(video.category)}
                        sx={{ mb: 2 }}
                      />
                    )}

                    {video.description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {video.description.length > 100
                          ? `${video.description.substring(0, 100)}...`
                          : video.description}
                      </Typography>
                    )}

                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={video.source_type === 'url' ? 'External URL' : 'Local File'}
                        size="small"
                        variant="outlined"
                      />
                      {video.is_analyzed && (
                        <Chip
                          label="AI Analyzed"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      )}
                      {video.annotation_count > 0 && (
                        <Chip
                          label={`${video.annotation_count} annotations`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>

                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                      By: {video.uploader?.first_name} {video.uploader?.last_name}
                    </Typography>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => navigate(`/video/${video.id}`)}
                    >
                      View Details
                    </Button>
                    {video.url && (
                      <Button
                        size="small"
                        href={video.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Watch
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {!loading && videos.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography variant="h6" color="text.secondary">
              No videos found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {filter !== 'all' ? 'Try changing the filter' : 'Upload your first video to get started'}
            </Typography>
          </Box>
        )}
      </Container>
    </Layout>
  );
}

export default Dashboard;

