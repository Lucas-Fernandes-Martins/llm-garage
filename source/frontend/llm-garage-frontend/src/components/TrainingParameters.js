import React from "react";
import { 
  TextField, 
  Box, 
  Typography, 
  Paper,
  FormControl,
  FormLabel,
  Slider,
  InputAdornment
} from "@mui/material";
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Select from "react-select";
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
  {value:"google/gemma-3-1b-pt", label:"google/gemma-3-1b-pt"},
  {value:"google/gemma-3-1b-it", label:"google/gemma-3-1b-it"},
  {value:"google/gemma-3-4b-pt", label:"google/gemma-3-4b-pt"},
  {value:"google/gemma-3-4b-it", label:"google/gemma-3-4b-it"},
  { value: "google/gemma-2b", label: "google/gemma-2b" },
  //{ value: "princeton-nlp/Sheared-LLaMA-1.3B", label: "princeton-nlp/Sheared-LLaMA-1.3B" },
  { value: "google/gemma-2-2b-it", label: "google/gemma-2-2b-it" }
];

const TrainingParameters = ({
  modelName,
  epochs,
  learningRate,
  onModelNameChange,
  onEpochsChange,
  onLearningRateChange
}) => {
  // Find the selected option from the modelOptions array
  const selectedOption = modelOptions.find(option => option.value === modelName);

  const handleLearningRateChange = (event) => {
    onLearningRateChange(event.target.value);
  };

  return (
    <ThemeProvider theme={theme}>
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 2, backgroundColor: "#f9f9f9" }}>
        <Typography variant="h5" gutterBottom className="sessionName">
          Set Training Parameters
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <FormControl fullWidth>
            <FormLabel id="model-select-label" sx={{ marginBottom: 1, color: "text.primary", fontWeight: "medium" }}>
              Model Name
            </FormLabel>
            <Select
              inputId="model-select"
              value={selectedOption}
              onChange={(option) => onModelNameChange(option.value)}
              options={modelOptions}
              styles={selectStyles}
              isClearable={false}
              isSearchable={true}
            />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="epochs-label" sx={{ marginBottom: 1, color: "text.primary", fontWeight: "medium" }}>
              Epochs
            </FormLabel>
            <TextField
              id="epochs-input"
              type="number"
              value={epochs}
              onChange={(e) => onEpochsChange(e.target.value)}
              variant="outlined"
              InputProps={{
                inputProps: { min: 1 }
              }}
              fullWidth
            />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="learning-rate-label" sx={{ marginBottom: 1, color: "text.primary", fontWeight: "medium" }}>
              Learning Rate: {learningRate}
            </FormLabel>
            <TextField
              id="learning-rate-input"
              type="number"
              step="0.0001"
              value={learningRate}
              onChange={handleLearningRateChange}
              variant="outlined"
              InputProps={{
                inputProps: { min: 0.0001, max: 0.1, step: 0.0001 },
                startAdornment: <InputAdornment position="start">λ</InputAdornment>,
              }}
              fullWidth
            />
            <Slider 
              value={parseFloat(learningRate)}
              min={0.0001}
              max={0.01}
              step={0.0001}
              onChange={(_, value) => onLearningRateChange(value)}
              sx={{ mt: 2 }}
            />
          </FormControl>
        </Box>
      </Paper>
    </ThemeProvider>
  );
};

export default TrainingParameters;
