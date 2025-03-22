import React, { useState } from "react";
import {
  Button,
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  AlertTitle
} from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import "../style/assets.css";

const FinetuneControl = ({ onStart, wsStatus }) => {
  const [loading, setLoading] = useState(false);

  const handleStartFineTuning = () => {
    setLoading(true);
    onStart();
    // We don't set loading to false here because training is asynchronous
    // and progress is shown through wsStatus
  };

  // Reset loading state when fine-tuning completes
  React.useEffect(() => {
    if (wsStatus && wsStatus.includes("complete")) {
      setLoading(false);
    }
  }, [wsStatus]);

  return (
    <Paper elevation={3} sx={{ padding: 3, marginBottom: 2, backgroundColor: "#f9f9f9" }}>
      <Typography variant="h5" gutterBottom className="sessionName">
        Start Fine-Tuning
      </Typography>
      
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<PlayArrowIcon />}
          onClick={handleStartFineTuning}
          disabled={loading}
          sx={{ 
            backgroundColor: "#6200ee", 
            "&:hover": { backgroundColor: "#3700b3" } 
          }}
        >
          {loading ? (
            <>
              <CircularProgress size={24} color="inherit" sx={{ marginRight: 1 }} />
              Fine-Tuning in Progress
            </>
          ) : (
            "Start Fine-Tuning"
          )}
        </Button>
        
        {wsStatus && (
          <Alert 
            severity={wsStatus.includes("error") ? "error" : wsStatus.includes("complete") ? "success" : "info"}
            sx={{ width: "100%" }}
          >
            <AlertTitle>
              {wsStatus.includes("error") ? "Error" : wsStatus.includes("complete") ? "Success" : "Status"}
            </AlertTitle>
            {wsStatus}
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

export default FinetuneControl;
