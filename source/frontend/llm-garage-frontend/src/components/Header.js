// Header.js
import React from "react";
import "../style/Header.css";  // Make sure to create/update this CSS file accordingly

const Header = () => {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <h1 className="navbar-title">
          Gemma Garage <span role="img" aria-label="diamond">💎</span>
        </h1>
        <p className="navbar-subtitle">
          The go-to place for fine-tuning your LLMs 🤖
        </p>
      </div>
    </nav>
  );
};

export default Header;
