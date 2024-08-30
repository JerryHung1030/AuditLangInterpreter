import React, { useState, useEffect, useRef } from 'react';
import { BsStars } from "react-icons/bs";
import ReactMarkdown from 'react-markdown';
import styled from 'styled-components';
import './FloatingChat.css';

const StyledMarkdown = styled.div`
  h1 {
    color: #ffd700;
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
  
  h2 {
    color: #ffa500;
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
  }

  h3 {
    color: #ff8c00;
    font-size: 1.125rem;
    margin-bottom: 0.5rem;
  }

  p {
    color: #f0e68c;
    margin-bottom: 0.5rem;
    line-height: 1.6;
  }

  ul {
    color: #f5deb3;
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
  }

  li {
    margin-bottom: 0.25rem;
  }

  strong {
    color: #ff6347;
  }

  em {
    color: #dda0dd;
  }

  code {
    color: #00ffff;
    background-color: #333;
    padding: 0.2rem;
    border-radius: 0.3rem;
  }

  blockquote {
    color: #7fffd4;
    border-left: 4px solid #7fffd4;
    padding-left: 1rem;
    margin: 1rem 0;
  }

  a {
    color: #add8e6;
    text-decoration: underline;
  }
`;

const FloatingChat = () => {
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'other', text: 'How can I help you! 🐵' },
    { type: 'self', text: "mm... let me think about it." },
    { type: 'other', text: 'take your time!' }
  ]);
  const [inputText, setInputText] = useState('');
  const chatBoxRef = useRef(null);

  useEffect(() => {
    setTimeout(() => {
      setChatOpen(true);
    }, 1000);
  }, []);

  useEffect(() => {
    if (chatOpen && chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatOpen, messages]);

  const toggleChat = (e) => {
    e.stopPropagation();
    setChatOpen(!chatOpen);
  };

  const handleSendMessage = async () => {
    if (inputText.trim()) {
      setMessages([...messages, { type: 'self', text: inputText }]);
      const userMessage = inputText;
      setInputText('');

      try {
        const response = await fetch('http://127.0.0.1:8080/api/v1/qa/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: userMessage }),
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();

        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'other', text: data.answer },
        ]);
      } catch (error) {
        console.error('Error fetching data:', error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: 'other', text: 'Sorry, something went wrong.' },
        ]);
      }
    }
  };

  const handleKeyDown = (event) => {
    if ((event.metaKey || event.ctrlKey) && event.keyCode === 13) {
      handleSendMessage();
    }
  };

  return (
    <div
      className={`floating-chat ${chatOpen ? 'open' : ''}`}
      onClick={toggleChat}
    >
      {!chatOpen && <BsStars color="lightyellow" />}
      {chatOpen && (
        <div className="chat" onClick={(e) => e.stopPropagation()}>
          <div className="header">
            <span className="title">Q&A Beta</span>
            <button className="close-button" onClick={toggleChat}>
              <span></span>
            </button>
          </div>
          <ul className="messages" ref={chatBoxRef}>
            {messages.map((message, index) => (
              <li key={index} className={`message ${message.type}`}>
                <StyledMarkdown>
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </StyledMarkdown>
              </li>
            ))}
          </ul>
          <div className="footer">
            <textarea
              className="text-box"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows="2"
              placeholder="Type your message here..."
            />
            <button id="sendMessage" onClick={handleSendMessage}>
              send
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FloatingChat;
