import React from "react";

const DarkModeToggle = ({ toggleDarkMode, darkMode }) => {
  return (
    <button className="dark-mode-toggle" onClick={toggleDarkMode}>
      {darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
    </button>
  );
};

export default DarkModeToggle;
