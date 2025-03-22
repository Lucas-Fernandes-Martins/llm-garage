import React, { useState, useRef } from "react";
import Header from "./components/Header";
import UploadDataset from "./components/UploadDataset";
import TrainingParameters from "./components/TrainingParameters";
import FinetuneControl from "./components/FinetuneControl";
import LossGraph from "./components/LossGraph";
import Sidebar from "./components/Sidebar";
import TestLLM from "./components/TestLLM";
import "./style/App.css";

// Import our API endpoints
import { API_BASE_URL, WS_BASE_URL } from "./api";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { Paper, Typography, Button } from "@mui/material";
import GetAppIcon from "@mui/icons-material/GetApp";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [datasetFile, setDatasetFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [modelName, setModelName] = useState("google/gemma-3-1b-pt");
  const [epochs, setEpochs] = useState(1);
  const [learningRate, setLearningRate] = useState(0.0002);
  const [loraRank, setLoraRank] = useState(4);
  const [wsStatus, setWsStatus] = useState("");
  const [lossData, setLossData] = useState([]);
  const [weightsUrl, setWeightsUrl] = useState(null); // New state for weights URL
  const ws = useRef(null);

  // Handle file changes
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Reset any previous upload status
      setUploadStatus("");
      
      // Validate file type
      const fileExt = file.name.split('.').pop().toLowerCase();
      if (!['json', 'csv', 'pdf'].includes(fileExt)) {
        alert("Please upload a JSON, CSV, or PDF file.");
        return;
      }
      
      setDatasetFile(file);
    }
  };

  // Upload dataset using the API endpoint
  const uploadDataset = async () => {
    if (!datasetFile) {
      alert("Please select a file.");
      return;
    }
    
    const formData = new FormData();
    formData.append("file", datasetFile);

    try {
      setUploadStatus("Uploading...");
      const response = await fetch(`${API_BASE_URL}/dataset/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error uploading file");
      }
      
      const data = await response.json();
      
      // Show appropriate message based on file type
      const fileExt = datasetFile.name.split('.').pop().toLowerCase();
      if (fileExt === 'pdf') {
        setUploadStatus("PDF processed successfully: " + data.file_location);
      } else {
        setUploadStatus("Dataset uploaded successfully: " + data.file_location);
      }
    } catch (error) {
      console.error("Error uploading file", error);
      setUploadStatus("Error: " + error.message);
    }
  };

  // Start fine-tuning via WebSocket and update loss graph in real time
  const startFinetuning = () => {
    ws.current = new WebSocket(`${WS_BASE_URL}/finetune/ws/train`);
    ws.current.onopen = () => {
      setWsStatus("WebSocket connected");
      const payload = {
        model_name: modelName,
        dataset_path: datasetFile ? datasetFile.name : "",
        epochs: epochs,
        learning_rate: learningRate,
        lora_rank: loraRank,
      };
      ws.current.send(JSON.stringify(payload));
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        // Update loss graph if a loss datapoint is received
        if (message.loss) {
          setLossData((prevData) => [
            ...prevData,
            { time: new Date().toLocaleTimeString(), loss: message.loss },
          ]);
        } else if (message.status) {
          setWsStatus(message.status);
          setWeightsUrl(message.weights_url);
          setWsStatus("Fine-tuning complete. Weights ready for download.");
        } else if (message["test connection"]) {
          console.log("Backend response:", message);
        }
      } catch (e) {
        console.error("Error parsing message", e);
      }
    };

    ws.current.onclose = () => {
      setWsStatus("WebSocket closed");
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      setWsStatus("WebSocket error");
    };
  };

  const downloadWeights = async () => {
    if (!weightsUrl) return;
    try {
      console.log("Downloading weights from", weightsUrl);
      const response = await fetch(`${API_BASE_URL}/download/download_weights`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ weights_path: weightsUrl }),
      });
      if (!response.ok) {
        throw new Error("File not available");
      }
      const data = await response.json();
      // data.download_link now contains the URL to download the file.
      const link = document.createElement("a");
      link.href = data.download_link;
      link.download = "fine_tuned_weights.pth"; // Sets the suggested filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading file", error);
    }
  };
  
  

  return (
    <div className="container">
      {/* <Sidebar /> */}
      <div className="main-content">
        <Header />
        <UploadDataset
          datasetFile={datasetFile}
          onFileChange={handleFileChange}
          uploadStatus={uploadStatus}
          onUpload={uploadDataset}
        />
        <TrainingParameters
          modelName={modelName}
          epochs={epochs}
          learningRate={learningRate}
          loraRank={loraRank}
          onModelNameChange={setModelName}
          onEpochsChange={setEpochs}
          onLearningRateChange={setLearningRate}
          onLoraRankChange={setLoraRank}
        />
        <FinetuneControl onStart={startFinetuning} wsStatus={wsStatus} />
        <LossGraph lossData={lossData} />
        
        {/* Use MUI for Download Weights button */}
        {weightsUrl && (
          <Paper elevation={3} sx={{ padding: 3, marginBottom: 2, backgroundColor: "#f9f9f9" }}>
            <Typography variant="h5" gutterBottom className="sessionName">
              Download Fine-Tuned Model
            </Typography>
            <Button
              variant="contained"
              onClick={downloadWeights}
              startIcon={<GetAppIcon />}
              sx={{ 
                backgroundColor: "#6200ee", 
                "&:hover": { backgroundColor: "#3700b3" } 
              }}
            >
              Download Weights
            </Button>
          </Paper>
        )}
        <TestLLM />
      </div>
    </div>
  );
}

export default App;
