import React, { useState } from "react";

function ChatBox() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! I’m your Public Health Assistant. How may I assist you today?" },
  ]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);

    // Call Flask backend
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });
      const data = await response.json();

      // Use structured HTML if provided
      if (data.html) {
        setMessages([...newMessages, { sender: "bot", html: data.html }]);
      } else {
        setMessages([...newMessages, { sender: "bot", text: data.response }]);
      }
    } catch (err) {
      setMessages([...newMessages, { sender: "bot", text: "Error: Could not connect to server." }]);
    }

    setInput("");
  };

  return (
    <div className="w-full max-w-lg h-[70vh] bg-white/80 backdrop-blur-md rounded-2xl shadow-lg flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => {
          const common = "p-3 rounded-lg max-w-[80%]";
          const userCls = "bg-blue-500 text-white self-end ml-auto";
          const botCls = "bg-white border border-green-500 text-gray-800 self-start mr-auto";
          return msg.sender === "bot" && msg.html ? (
            <div
              key={i}
              className={`${common} ${botCls}`}
              dangerouslySetInnerHTML={{ __html: msg.html }}
            />
          ) : (
            <div
              key={i}
              className={`${common} ${msg.sender === "user" ? userCls : botCls}`}
            >
              {msg.text}
            </div>
          );
        })}
      </div>

      {/* Input */}
      <div className="p-3 flex border-t border-gray-200">
        <input
          type="text"
          className="flex-1 px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-400"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask me about diseases, prevention, awareness..."
        />
        <button
          onClick={handleSend}
          className="ml-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;
