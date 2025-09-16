
import React, { useState } from "react";
import ChatBox from "./components/ChatBox";

function App() {
  return (
    <div className="w-full h-screen flex flex-col items-center justify-between">
      {/* Header */}
      <header className="text-center py-4 bg-white/70 w-full shadow-md">
        <h1 className="text-2xl font-bold text-green-800">AI-Driven Public Health Chatbot</h1>
        <p className="text-sm text-gray-600">By Government of Odisha</p>
      </header>

      {/* Chatbox */}
      <div className="flex-grow flex justify-center items-center w-full px-4">
        <ChatBox />
      </div>

      {/* Footer */}
      <footer className="text-xs text-gray-700 py-3 bg-white/70 w-full text-center">
        <a href="#">About</a> | <a href="#">Contact</a> | <a href="#">Disclaimer</a>
      </footer>
    </div>
  );
}

export default App;
