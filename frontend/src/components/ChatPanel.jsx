import React, { useState, useRef, useEffect } from 'react';
import { Bot, ShieldCheck, Sparkles, Key, Check, Send } from 'lucide-react';
import { chatWithRepo } from '../services/api';

export default function ChatPanel({ repoId, repoUrl, selectedNode }) {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: 'Select any node in the architecture graph to ask structural or open-ended questions about it.',
      type: 'system',
      llm_used: false
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [showKeyInput, setShowKeyInput] = useState(!localStorage.getItem('gemini_api_key'));
  const [savedKey, setSavedKey] = useState(!!localStorage.getItem('gemini_api_key'));
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSaveKey = (e) => {
    e.preventDefault();
    if (apiKey.trim()) {
      localStorage.setItem('gemini_api_key', apiKey.trim());
      setSavedKey(true);
      setShowKeyInput(false);
    } else {
      localStorage.removeItem('gemini_api_key');
      setSavedKey(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || (!repoId && !repoUrl)) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    setLoading(true);

    try {
      const data = await chatWithRepo(
        repoId,
        selectedNode ? selectedNode.id : null,
        userMessage,
        apiKey.trim() || null
      );

      const { answer, answer_type, response_source, verification_level, llm_used } = data;

      setMessages(prev => [...prev, {
        role: 'ai',
        content: answer,
        answer_type: answer_type,
        response_source: response_source,
        verification_level: verification_level,
        llm_used: llm_used
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'ai',
        content: 'Error: ' + (error.response?.data?.detail || error.message),
        type: 'error'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-panel h-full" style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'rgba(15, 23, 42, 0.95)', color: '#f8fafc' }}>
      <div className="panel-header" style={{ padding: '16px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <Bot size={18} color="#38bdf8" /> Architecture Assistant
          </h2>
          <button
            onClick={() => setShowKeyInput(!showKeyInput)}
            style={{
              background: savedKey ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              border: `1px solid ${savedKey ? '#34d399' : '#ef4444'}`,
              color: savedKey ? '#34d399' : '#ef4444',
              borderRadius: '6px',
              padding: '4px 8px',
              fontSize: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer'
            }}
            title="Configure Gemini API Key"
          >
            <Key size={12} /> {savedKey ? 'Key Configured' : 'Set API Key'}
          </button>
        </div>

        {showKeyInput && (
          <form onSubmit={handleSaveKey} style={{
            marginTop: '10px',
            background: 'rgba(0,0,0,0.3)',
            padding: '10px',
            borderRadius: '6px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            gap: '6px'
          }}>
            <input
              type="password"
              placeholder="Paste Gemini API Key here..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              style={{
                flex: 1,
                fontSize: '0.8rem',
                padding: '6px 8px',
                background: '#0f172a',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '4px',
                color: 'white',
                outline: 'none'
              }}
            />
            <button
              type="submit"
              style={{
                background: '#38bdf8',
                color: '#0f172a',
                border: 'none',
                padding: '6px 10px',
                borderRadius: '4px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Check size={14} /> Save
            </button>
          </form>
        )}

        {selectedNode && (
          <div style={{ marginTop: '10px', fontSize: '0.8rem', color: '#94a3b8' }}>
            Target node: <span style={{ color: '#38bdf8', fontWeight: 600 }}>{selectedNode.name}</span>
          </div>
        )}
      </div>

      <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              background: msg.role === 'user' ? '#0284c7' : 'rgba(255, 255, 255, 0.05)',
              border: msg.role === 'user' ? 'none' : '1px solid rgba(255, 255, 255, 0.08)',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem'
            }}
          >
            {msg.role === 'ai' && msg.type !== 'system' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', marginBottom: '8px', fontWeight: 'bold' }}>
                {msg.llm_used ? (
                  <span style={{ color: '#f472b6', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={13} /> LLM EXPLANATION (GRAPH GROUNDED)
                  </span>
                ) : (
                  <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ShieldCheck size={13} /> GRAPH ANSWER (verified directly from static-analysis graph)
                  </span>
                )}
              </div>
            )}
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{ color: '#94a3b8', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Analyzing repository graph...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} style={{ padding: '12px 16px', borderTop: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0,0,0,0.2)' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder={selectedNode ? `Ask about ${selectedNode.name}...` : "Select a node first..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!repoId || loading}
            style={{
              flex: 1,
              background: '#0f172a',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '6px',
              padding: '8px 12px',
              color: 'white',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
          <button
            type="submit"
            disabled={!repoId || loading || !input.trim()}
            style={{
              background: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 14px',
              cursor: 'pointer',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  );
}
