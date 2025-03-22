// Header.js
import React from "react";
import { AppBar, Toolbar, Typography, Button, Box, useMediaQuery, IconButton } from "@mui/material";
import { ThemeProvider, createTheme } from '@mui/material/styles';
import GitHubIcon from '@mui/icons-material/GitHub';
import DiamondIcon from '@mui/icons-material/Diamond';
import CodeIcon from '@mui/icons-material/Code';
import "../style/Header.css";

const theme = createTheme({
  palette: {
    primary: {
      main: '#6200ee',
    },
    secondary: {
      main: '#3700b3',
    },
  },
});

const Header = () => {
  const isSmallScreen = useMediaQuery('(max-width:600px)');

  return (
    <ThemeProvider theme={theme}>
      <AppBar position="static" sx={{ 
        backgroundColor: '#6200ee', 
        marginBottom: 2,
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <DiamondIcon sx={{ mr: 1 }} />
            <Typography 
              variant={isSmallScreen ? "h6" : "h5"} 
              component="div" 
              sx={{ fontWeight: 'bold' }}
            >
              Gemma Garage
            </Typography>
          </Box>
          
          <Box>
            <Button 
              color="inherit" 
              href="https://github.com/Lucas-Fernandes-Martins/llm-garage" 
              target="_blank"
              rel="noopener noreferrer"
              startIcon={isSmallScreen ? null : <GitHubIcon />}
              sx={{ 
                textTransform: 'none',
                fontWeight: 'bold',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              {isSmallScreen ? (
                <GitHubIcon />
              ) : (
                "View on GitHub"
              )}
            </Button>
          </Box>
        </Toolbar>
        
        <Box sx={{ 
          backgroundColor: '#3700b3', 
          padding: '4px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center' 
        }}>
          <Typography 
            variant="body2" 
            component="div" 
            sx={{ 
              color: 'white',
              fontStyle: 'italic',
              textAlign: 'center'
            }}
          >
            The go-to place for fine-tuning your LLMs 🤖
          </Typography>
        </Box>
      </AppBar>
    </ThemeProvider>
  );
};

export default Header;
