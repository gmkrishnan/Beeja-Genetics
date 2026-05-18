import React, { useState, useEffect, useRef } from 'react';
import '../styles/Helix.css';

const HelixView = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am Beeja Helix, your conversational genetic analyst. To begin, please upload your genomic file (.txt or .vcf).' }
  ]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('WAITING_FOR_FILE'); // WAITING_FOR_FILE, WAITING_FOR_AGE, WAITING_FOR_DIET, READY
  const [sessionData, setSessionData] = useState({ file: null, age: '', diet: 'Standard', mode: 'supportive' });
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    if (status === 'WAITING_FOR_AGE') {
      const ageVal = parseInt(input);
      if (isNaN(ageVal)) {
        addAssistantMsg("I'm sorry, could you please provide a valid number for your age?");
      } else {
        setSessionData(prev => ({ ...prev, age: ageVal }));
        setStatus('WAITING_FOR_DIET');
        addAssistantMsg("Thank you. And what is your current diet? (Standard, Vegan, Keto, Paleo, etc.)");
      }
      setIsTyping(false);
      return;
    }

    if (status === 'WAITING_FOR_DIET') {
      setSessionData(prev => ({ ...prev, diet: input }));
      setStatus('READY');
      addAssistantMsg(`Perfect. I've initialized your clinical profile. I am currently in **${sessionData.mode === 'medical' ? 'Medical' : 'Supportive'}** mode. How can I help you explore your DNA today?`);
      setIsTyping(false);
      return;
    }

    if (status === 'READY') {
      try {
        const response = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: input,
            mode: sessionData.mode,
            file_path: sessionData.file ? sessionData.file.name : "James_Jones_v5_Full.txt",
            patient_context: { age: sessionData.age, diet: sessionData.diet }
          })
        });
        const data = await response.json();
        
        // Handle logs if present
        if (data.logs) {
           data.logs.forEach((log, i) => {
             setTimeout(() => {
                // We could show logs in a special way, but for now we'll just show the final answer
             }, i * 500);
           });
        }

        addAssistantMsg(data.answer);
      } catch (err) {
        addAssistantMsg("I'm having trouble connecting to the specialist swarm. Please ensure the backend is running.");
      }
      setIsTyping(false);
    }
  };

  const addAssistantMsg = (content) => {
    setMessages(prev => [...prev, { role: 'assistant', content }]);
  };

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setSessionData(prev => ({ ...prev, file: uploadedFile }));
      setMessages(prev => [...prev, { role: 'user', content: `Uploaded: ${uploadedFile.name}` }]);
      setIsTyping(true);
      setTimeout(() => {
        addAssistantMsg("File received and indexed. How old are you?");
        setStatus('WAITING_FOR_AGE');
        setIsTyping(false);
      }, 1000);
    }
  };

  return (
    <div className="helix-view fade-in">
      <div className="helix-header">
        <div className="helix-status">
           <div className={`status-dot ${status === 'READY' ? 'online' : 'busy'}`}></div>
           <span>Beeja Helix: {status.replace(/_/g, ' ')}</span>
        </div>
        <div className="helix-modes">
           <button 
             className={sessionData.mode === 'supportive' ? 'active' : ''} 
             onClick={() => setSessionData(prev => ({...prev, mode: 'supportive'}))}
           >
             Supportive
           </button>
           <button 
             className={sessionData.mode === 'medical' ? 'active' : ''} 
             onClick={() => setSessionData(prev => ({...prev, mode: 'medical'}))}
           >
             Medical
           </button>
        </div>
      </div>

      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            <div className="message-bubble">
              {msg.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message-row assistant">
            <div className="message-bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="chat-input-area">
        {status === 'WAITING_FOR_FILE' ? (
          <div className="upload-prompt">
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{display: 'none'}} 
              onChange={handleFileUpload} 
            />
            <button className="helix-upload-btn" onClick={() => fileInputRef.current.click()}>
              📁 Upload DNA File to Begin
            </button>
          </div>
        ) : (
          <div className="input-group">
            <input 
              type="text" 
              placeholder="Ask anything about your DNA..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend}>Send</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HelixView;
