import axios from 'axios';
import React, { useState } from 'react';
import './App.css';

const ChatApp = () => {
  // State to store the messages (questions and responses)
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Handle input change
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // Send message to backend
  const sendMessage = async () => {
    if (input.trim() === '') return;

    // Add user's message to the chat history
    const newUserMessage = { text: input, sender: 'user' };
    setMessages([newUserMessage, ...messages]); // Add to the top

    setLoading(true);

    try {
      // Call the backend API
      const response = await axios.get(`http://localhost:8000/search?query=${input}`);
      const botMessage = formatResponse(input, response.data.recommendations);

      // Add bot's response to the chat history
      const newBotMessage = { text: botMessage, sender: 'bot' };
      setMessages([newBotMessage, newUserMessage, ...messages]); // Add to the top
    } catch (error) {
      console.error("Error fetching data:", error);
      const errorMessage = { text: "Sorry, something went wrong.", sender: 'bot' };
      setMessages([errorMessage, newUserMessage, ...messages]);
    }

    setLoading(false);
    setInput('');
  };

  // Format the AI's response for better display
  const formatResponse = (input, recommendations) => {
    // Map each recommendation to a list item
    const formattedRecommendations = recommendations.map(rec => `<li>${rec}</li>`).join('');
    return `
        <strong>Query</strong>: "${input}"
        <strong>AI Interpretation</strong>: Possible causes:
        <ul style="padding-top: 0;padding-bottom: 0; margin-top: 0; margin-bottom: 0;">
            ${formattedRecommendations}
        </ul>
      <strong>Suggested Tests</strong>: test1, test2, test3.
    `;
  };

  // Handle Enter key press to send message
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Prevent default behavior (new line in input)
      sendMessage(); // Trigger message send
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress} // Listen for Enter key press
          placeholder="Ask a question..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>

      <div className="chat-history">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender}`}
            style={{ textAlign: message.sender === 'user' ? 'right' : 'left' }}
          >
            {message.sender === 'bot' ? (
              <div className="bot-message">
                {/* Render the bot message with HTML using dangerouslySetInnerHTML */}
                <p dangerouslySetInnerHTML={{ __html: message.text }}></p>
              </div>
            ) : (
              <div className="user-message">
                <p>{message.text}</p>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message bot"><p>Thinking...</p></div>}
      </div>
    </div>
  );
};

export default ChatApp;
