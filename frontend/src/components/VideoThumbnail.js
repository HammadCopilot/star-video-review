import React from 'react';
import { Box, CardMedia } from '@mui/material';
import { PlayCircleOutline } from '@mui/icons-material';

function VideoThumbnail({ video, width = '100%', height = 200 }) {
  // Generate thumbnail from video URL or use placeholder
  const getThumbnailUrl = () => {
    if (!video.url) {
      return null;
    }

    // For YouTube videos
    if (video.url.includes('youtube.com') || video.url.includes('youtu.be')) {
      const videoId = extractYouTubeId(video.url);
      if (videoId) {
        return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
      }
    }

    // For Vimeo videos
    if (video.url.includes('vimeo.com')) {
      // Would need Vimeo API to get thumbnail
      return null;
    }

    // For other videos, use a placeholder with category color
    return null;
  };

  const extractYouTubeId = (url) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  };

  const getCategoryColor = (category) => {
    const colors = {
      discrete_trial: '#1976d2',
      pivotal_response: '#dc004e',
      functional_routines: '#2e7d32',
    };
    return colors[category] || '#757575';
  };

  const thumbnailUrl = getThumbnailUrl();

  if (thumbnailUrl) {
    return (
      <Box sx={{ position: 'relative', width, height }}>
        <CardMedia
          component="img"
          height={height}
          image={thumbnailUrl}
          alt={video.title}
          sx={{
            objectFit: 'cover',
            borderRadius: 1,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            borderRadius: 1,
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
            },
          }}
        >
          <PlayCircleOutline sx={{ fontSize: 60, color: 'white' }} />
        </Box>
      </Box>
    );
  }

  // Placeholder thumbnail with category color
  return (
    <Box
      sx={{
        width,
        height,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: getCategoryColor(video.category),
        borderRadius: 1,
        position: 'relative',
      }}
    >
      <PlayCircleOutline sx={{ fontSize: 60, color: 'white', opacity: 0.9 }} />
      <Box
        sx={{
          position: 'absolute',
          bottom: 8,
          left: 8,
          right: 8,
          textAlign: 'center',
          color: 'white',
          fontSize: '0.75rem',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          opacity: 0.8,
        }}
      >
        {video.category?.replace('_', ' ') || 'Video'}
      </Box>
    </Box>
  );
}

export default VideoThumbnail;

