import React, { useState } from "react";
import { 
  Button, 
  Box, 
  Typography, 
  Paper, 
  CircularProgress,
  Chip
} from "@mui/material";
import { styled } from "@mui/material/styles";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import DataObjectIcon from "@mui/icons-material/DataObject";
import TableChartIcon from "@mui/icons-material/TableChart";
import "../style/assets.css";

// Styled component for the file input
const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

const UploadDataset = ({ datasetFile, onFileChange, uploadStatus, onUpload }) => {
  const [loading, setLoading] = useState(false);
  
  // Determine file type icon
  const getFileTypeIcon = () => {
    if (!datasetFile) return null;
    
    const extension = datasetFile.name.split('.').pop().toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return <PictureAsPdfIcon sx={{ color: "#f44336" }} />;
      case 'json':
        return <DataObjectIcon sx={{ color: "#2196f3" }} />;
      case 'csv':
        return <TableChartIcon sx={{ color: "#4caf50" }} />;
      default:
        return null;
    }
  };

  const handleUpload = async () => {
    setLoading(true);
    await onUpload();
    setLoading(false);
  };

  return (
    <Paper elevation={3} sx={{ padding: 3, marginBottom: 2, backgroundColor: "#f9f9f9" }}>
      <Typography variant="h5" gutterBottom className="sessionName">
        Upload Dataset
      </Typography>
      
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2 }}>
        <Button
          component="label"
          variant="contained"
          startIcon={<CloudUploadIcon />}
          sx={{ 
            backgroundColor: "#6200ee", 
            "&:hover": { backgroundColor: "#3700b3" } 
          }}
        >
          Select File
          <VisuallyHiddenInput type="file" onChange={onFileChange} />
        </Button>
        
        {datasetFile && (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip 
              icon={getFileTypeIcon()} 
              label={datasetFile.name}
              variant="outlined" 
            />
            <Typography variant="caption">
              {datasetFile.size ? `(${(datasetFile.size / 1024).toFixed(2)} KB)` : ''}
            </Typography>
          </Box>
        )}
        
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!datasetFile || loading}
          sx={{ 
            backgroundColor: "#6200ee", 
            "&:hover": { backgroundColor: "#3700b3" },
            minWidth: "150px" 
          }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Upload Dataset"}
        </Button>
        
        {uploadStatus && (
          <Box sx={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 1, 
            padding: 1, 
            backgroundColor: "#e3f2fd", 
            borderRadius: 1,
            maxWidth: "100%",
            overflow: "hidden",
            textOverflow: "ellipsis"
          }}>
            <CheckCircleIcon color="success" />
            <Typography variant="body2">{uploadStatus}</Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default UploadDataset;
