import React, { useState, useEffect } from "react";
import {
  Paper,
  Typography,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Alert,
  Divider,
} from "@mui/material";
import { API_BASE_URL } from "../api";

const DatasetPreview = ({ datasetFile, dataset_path }) => {
  const [previewData, setPreviewData] = useState([]);
  const [augmentedData, setAugmentedData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [augmentationType, setAugmentationType] = useState("keyboard");
  const [augmenting, setAugmenting] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [totalEntries, setTotalEntries] = useState(0);
  const [augmentedFilePath, setAugmentedFilePath] = useState(null);

  // Debug log to check what's received
  console.log("DatasetPreview received path:", dataset_path);

  useEffect(() => {
    if (dataset_path) {
      loadPreview();
    }
  }, [dataset_path]);

  useEffect(() => {
    if (augmentedFilePath) {
      console.log("augmentedFilePath changed, loading data:", augmentedFilePath);
      //loadAugmentedData();
    }
  }, [augmentedFilePath]);

  const loadPreview = async () => {
    if (!dataset_path) return;
    
    setLoading(true);
    try {
      console.log("Loading preview for file:", dataset_path);
      const response = await fetch(`${API_BASE_URL}/dataset/preview?path=${encodeURIComponent(dataset_path)}`);
      if (response.ok) {
        const data = await response.json();
        console.log("Preview data received:", data);
        
        if (data.full_count) {
          setTotalEntries(data.full_count);
          setPreviewData(data.preview || []);
        } else {
          setPreviewData(data.slice(0, 5)); 
          setTotalEntries(data.length);
        }
        
        // if (augmentedFilePath) {
        //   //loadAugmentedData();
        // }
      } else {
        console.error("Error loading preview: Server returned", response.status);
      }
    } catch (error) {
      console.error("Error loading preview:", error);
    }
    setLoading(false);
  };

  const loadAugmentedData = async () => {
    if (!augmentedFilePath) return;
    
    console.log("Loading augmented data from:", augmentedFilePath);
    try {
      const response = await fetch(`${API_BASE_URL}/dataset/preview?path=${encodeURIComponent(augmentedFilePath)}`);
      if (response.ok) {
        const data = await response.json();
        console.log("Augmented data received:", data);
        
        if (data.preview && data.preview.length > 0) {
          console.log("Setting augmented data from preview, length:", data.preview.length);
          setAugmentedData(data.preview);
        } else if (Array.isArray(data) && data.length > 0) {
          console.log("Setting augmented data from array, length:", data.length);
          setAugmentedData(data.slice(0, 5));
        } else {
          console.warn("Received empty or invalid augmented data");
          setAugmentedData([]);
        }
        
        setActiveTab(1);
      } else {
        console.error("Error loading augmented data: Server returned", response.status);
      }
    } catch (error) {
      console.error("Error loading augmented data:", error);
    }
  };

  const handleAugment = async () => {
    if (!dataset_path) {
      alert("Please upload a dataset first");
      return;
    }

    setAugmenting(true);
    try {
      console.log("Augmenting file:", dataset_path);
      const response = await fetch(`${API_BASE_URL}/dataset/augment`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          augmentation_type: augmentationType,
          dataset_path: dataset_path,
          preserve_format: {
            enabled: true,
            patterns: ["Instruction:", "Input:", "Output:"]
          }
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error augmenting dataset");
      }

      const data = await response.json();
      console.log("Augmentation response:", data);

      if(data.augmented_data) {
        setAugmentedData(data.augmented_data.preview);
        setActiveTab(1);
      }
      
      if (data.file_location) {
        console.log("Setting augmented file path:", data.file_location);
        setAugmentedFilePath(data.file_location);
        
        //alert("Dataset augmented successfully!");
      } else {
        alert("Dataset augmented but couldn't retrieve results. Please check the console for errors.");
      }
      
    } catch (error) {
      console.error("Error augmenting dataset:", error);
      alert("Error augmenting dataset: " + error.message);
    }
    setAugmenting(false);
  };
  
  const handleTabChange = (event, newValue) => {
    console.log("Tab changed to:", newValue);
    if (newValue === 1 && augmentedFilePath && augmentedData.length === 0) {
      console.log("Switching to augmented tab but no data loaded, loading now...");
      // loadAugmentedData();
    } else {
      setActiveTab(newValue);
    }
  };

  const renderDataTable = (data) => {
    return (
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Text</TableCell>
              {data.length > 0 && data[0]?.label && <TableCell>Label</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={2} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={2} align="center">
                  No data available.
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, index) => (
                <TableRow key={index}>
                  <TableCell>{row.text}</TableCell>
                  {row.label && <TableCell>{row.label}</TableCell>}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Paper elevation={3} sx={{ padding: 3, marginBottom: 2, backgroundColor: "#f9f9f9" }}>
      <Typography variant="h5" gutterBottom className="sessionName">
        Dataset Preview {datasetFile ? `(${datasetFile.name})` : ""}
      </Typography>

      {dataset_path ? (
        <>
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Augmentation Type</InputLabel>
              <Select
                value={augmentationType}
                onChange={(e) => setAugmentationType(e.target.value)}
                label="Augmentation Type"
              >
                <MenuItem value="keyboard">Keyboard Augmentation</MenuItem>
                <MenuItem value="random_word">Random Word Augmentation</MenuItem>
                {/* <MenuItem value="spelling">Spelling Augmentation</MenuItem>
                <MenuItem value="synonym">Synonym Augmentation</MenuItem> */}
              </Select>
            </FormControl>

            <Button
              variant="contained"
              onClick={handleAugment}
              disabled={augmenting || !dataset_path}
              sx={{
                backgroundColor: "#6200ee",
                "&:hover": { backgroundColor: "#3700b3" },
              }}
            >
              {augmenting ? <CircularProgress size={24} /> : "Augment Dataset"}
            </Button>
          </Box>
          
          {totalEntries > 5 && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Showing only the first 5 entries out of {totalEntries} total entries.
            </Alert>
          )}
          
          <Box sx={{ width: '100%' }}>
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
            >
              <Tab label="Original Dataset" />
              <Tab 
                label="Augmented Dataset" 
                disabled={!augmentedFilePath}
              />
            </Tabs>
            
            <Box sx={{ mt: 2 }}>
              {activeTab === 0 ? (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Original Dataset Preview
                  </Typography>
                  {renderDataTable(previewData)}
                </>
              ) : (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Augmented Dataset Preview
                  </Typography>
                  {augmentedData.length > 0 ? (
                    renderDataTable(augmentedData)
                  ) : (
                    <Box display="flex" justifyContent="center" alignItems="center" p={3}>
                      <CircularProgress />
                      <Typography variant="body2" sx={{ ml: 2 }}>
                        Loading augmented data...
                      </Typography>
                    </Box>
                  )}
                </>
              )}
            </Box>
          </Box>
        </>
      ) : (
        <Typography variant="body1" align="center" sx={{ py: 3 }}>
          Please upload a dataset to see the preview and augmentation options.
        </Typography>
      )}
    </Paper>
  );
};

export default DatasetPreview;