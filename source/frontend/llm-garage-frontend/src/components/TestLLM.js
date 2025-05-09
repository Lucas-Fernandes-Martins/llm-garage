import React, { useState, useRef } from "react";
import { 
  Paper, 
  Typography, 
  Box, 
  TextField, 
  Button, 
  CircularProgress,
  FormControl,
  FormLabel
} from "@mui/material";
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Select from "react-select";
import SendIcon from "@mui/icons-material/Send";
import { WS_BASE_URL } from "../api"; // Define this as your WebSocket base URL (e.g., ws://localhost:8000)
import "../style/assets.css";

// Custom theme to match the color scheme
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

// Custom styles for react-select
const selectStyles = {
  control: (provided) => ({
    ...provided,
    borderRadius: "4px",
    borderColor: "#ccc",
    boxShadow: "none",
    "&:hover": {
      borderColor: "#6200ee"
    },
    padding: "2px",
    minHeight: "56px"
  }),
  option: (provided, state) => ({
    ...provided,
    backgroundColor: state.isSelected ? "#6200ee" : state.isFocused ? "#f0e6ff" : null,
    color: state.isSelected ? "white" : "#333",
    "&:hover": {
      backgroundColor: state.isSelected ? "#6200ee" : "#f0e6ff"
    }
  }),
  menu: (provided) => ({
    ...provided,
    borderRadius: "4px",
    boxShadow: "0 2px 5px rgba(0,0,0,0.2)"
  })
};

const modelOptions = [
  { value: "google/gemma-3-1b-pt", label: "google/gemma-3-1b-pt" },
  { value: "google/gemma-3-1b-it", label: "google/gemma-3-1b-it" },
  { value: "google/gemma-3-4b-pt", label: "google/gemma-3-4b-pt" },
  { value: "google/gemma-3-4b-it", label: "google/gemma-3-4b-it" },
  { value: "google/gemma-2b", label: "google/gemma-2b" },
  { value: "google/gemma-2-2b-it", label: "google/gemma-2-2b-it" }
];

const TestLLMWebSocket = () => {
  const [prompt, setPrompt] = useState("");
  const [modelName, setModelName] = useState("google/gemma-3-1b-it");
  // Hardcoded weights path
  const weightsPath = "./weights/weights.pth";
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);

  const handleTest = () => {
    if (!prompt.trim()) {
      alert("Please enter a prompt.");
      return;
    }
    setLoading(true);

    // Establish a new WebSocket connection
    const ws = new WebSocket(`${WS_BASE_URL}/inference/ws/test_llm`);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send the test parameters as JSON
      ws.send(JSON.stringify({ prompt, model_name: modelName, weights_path: weightsPath }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setResponse(`Error: ${data.error}`);
      } else if (data.response) {
        setResponse(data.response);
      }
      setLoading(false);
      ws.close();
    };

    ws.onerror = (error) => {
      console.error("WebSocket error", error);
      setResponse("WebSocket error occurred");
      setLoading(false);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
      setLoading(false);
    };
  };

  return (
    <ThemeProvider theme={theme}>
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 2, backgroundColor: "#f9f9f9" }}>
        <Typography variant="h5" gutterBottom className="sessionName">
          Test Fine-Tuned LLM
        </Typography>
        
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <FormControl fullWidth>
            <FormLabel sx={{ marginBottom: 1, color: "text.primary", fontWeight: "medium" }}>
              Model Name
            </FormLabel>
            <Select
              value={modelOptions.find((option) => option.value === modelName)}
              onChange={(option) => setModelName(option.value)}
              options={modelOptions}
              styles={selectStyles}
              isClearable={false}
              isSearchable={true}
            />
          </FormControl>
          
          <FormControl fullWidth>
            <FormLabel sx={{ marginBottom: 1, color: "text.primary", fontWeight: "medium" }}>
              Prompt
            </FormLabel>
            <TextField
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              multiline
              rows={6}
              variant="outlined"
              fullWidth
            />
          </FormControl>
          
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
            onClick={handleTest}
            disabled={loading}
            sx={{ 
              backgroundColor: "#6200ee", 
              "&:hover": { backgroundColor: "#3700b3" },
              alignSelf: "flex-start"
            }}
          >
            {loading ? "Testing..." : "Test Model"}
          </Button>
          
          <Box sx={{ marginTop: 2 }}>
            <Typography variant="h6" gutterBottom>
              Response:
            </Typography>
            <Paper 
              elevation={1} 
              sx={{ 
                padding: 2, 
                backgroundColor: "#f5f5f5", 
                minHeight: "100px",
                whiteSpace: "pre-wrap"
              }}
            >
              {response || "Response will appear here..."}
            </Paper>
          </Box>
        </Box>
      </Paper>
    </ThemeProvider>
  );
};

export default TestLLMWebSocket;
