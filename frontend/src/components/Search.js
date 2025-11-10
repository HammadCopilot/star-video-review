import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  TextField,
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  InputAdornment,
  Button,
} from '@mui/material';
import { Search as SearchIcon, VideoLibrary, Clear } from '@mui/icons-material';
import Layout from './Layout';

function Search() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState({ videos: [], practices: [], annotations: [] });
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      performSearch(q);
    }
  }, [searchParams]);

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults({ videos: [], practices: [], annotations: [] });
      setSearched(false);
      return;
    }

    try {
      setLoading(true);
      setSearched(true);
      const token = localStorage.getItem('token');
      
      // Search videos
      const videosResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/videos`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Filter videos by search query
      const filteredVideos = videosResponse.data.videos.filter(video =>
        video.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (video.description && video.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (video.category && video.category.toLowerCase().includes(searchQuery.toLowerCase()))
      );

      // Search best practices
      const practicesResponse = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/practices`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const filteredPractices = practicesResponse.data.practices.filter(practice =>
        practice.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        practice.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        practice.category.toLowerCase().includes(searchQuery.toLowerCase())
      );

      setResults({
        videos: filteredVideos,
        practices: filteredPractices,
        annotations: [], // Could add annotation search here
      });
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams({ q: query });
  };

  const handleClear = () => {
    setQuery('');
    setResults({ videos: [], practices: [], annotations: [] });
    setSearched(false);
    setSearchParams({});
  };

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Search
        </Typography>
        
        <Box component="form" onSubmit={handleSearch} sx={{ mb: 4 }}>
          <TextField
            fullWidth
            placeholder="Search videos, best practices, and content..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: query && (
                <InputAdornment position="end">
                  <Button onClick={handleClear} size="small">
                    <Clear />
                  </Button>
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />
          <Button type="submit" variant="contained" size="large">
            Search
          </Button>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {searched && !loading && (
          <>
            {/* Videos Results */}
            {results.videos.length > 0 && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <VideoLibrary sx={{ mr: 1 }} />
                  Videos ({results.videos.length})
                </Typography>
                <Grid container spacing={2}>
                  {results.videos.map((video) => (
                    <Grid item xs={12} md={6} key={video.id}>
                      <Card 
                        sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
                        onClick={() => navigate(`/video/${video.id}`)}
                      >
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {video.title}
                          </Typography>
                          {video.category && (
                            <Chip label={video.category.replace('_', ' ')} size="small" sx={{ mb: 1 }} />
                          )}
                          {video.description && (
                            <Typography variant="body2" color="text.secondary">
                              {video.description.substring(0, 150)}
                              {video.description.length > 150 && '...'}
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {/* Best Practices Results */}
            {results.practices.length > 0 && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" gutterBottom>
                  Best Practices ({results.practices.length})
                </Typography>
                <Grid container spacing={2}>
                  {results.practices.map((practice) => (
                    <Grid item xs={12} md={6} key={practice.id}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {practice.title}
                          </Typography>
                          <Chip 
                            label={practice.category.replace('_', ' ')} 
                            size="small"
                            sx={{ mb: 1 }}
                          />
                          <Chip 
                            label={practice.is_positive ? 'Strength' : 'Improvement'} 
                            size="small"
                            color={practice.is_positive ? 'success' : 'warning'}
                            sx={{ mb: 1, ml: 1 }}
                          />
                          <Typography variant="body2" color="text.secondary">
                            {practice.description.substring(0, 150)}
                            {practice.description.length > 150 && '...'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {/* No Results */}
            {results.videos.length === 0 && results.practices.length === 0 && (
              <Box sx={{ textAlign: 'center', mt: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  No results found for "{query}"
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Try different keywords or browse all content
                </Typography>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate('/dashboard')}
                  sx={{ mt: 2 }}
                >
                  Browse All Videos
                </Button>
              </Box>
            )}
          </>
        )}

        {!searched && !loading && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <SearchIcon sx={{ fontSize: 60, color: 'text.secondary' }} />
            <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
              Enter a search term to find videos and content
            </Typography>
          </Box>
        )}
      </Container>
    </Layout>
  );
}

export default Search;

