import { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  evaluation?: {
    spec_accuracy: number;
    pricing_accuracy: number;
    hallucination_check: number;
    overall_score: number;
  };
  timestamp: Date;
}

interface Props {
  onMessageSent: () => void;
}

const ChatInterface = ({ onMessageSent }: Props) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'fixed' | 'buggy'>('fixed');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sample questions
  const sampleQuestions = [
    "What's the yield strength of Fe 550D 16mm?",
    "What's the current price of TMT 12mm?",
    "What's the delivery time to Ranchi?",
    "What's the difference between Fe 500 and Fe 550D?",
  ];

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Use streaming endpoint
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input, mode }),
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.type === 'token') {
              assistantMessage.content += data.content;
              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = { ...assistantMessage };
                return newMessages;
              });
            } else if (data.type === 'evaluation') {
              assistantMessage.evaluation = data.content;
              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = { ...assistantMessage };
                return newMessages;
              });
            } else if (data.type === 'done') {
              onMessageSent();
            } else if (data.type === 'error') {
              console.error('Stream error:', data.content);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSampleClick = (question: string) => {
    setInput(question);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Chat</h2>
        <div className="mode-toggle">
          <button
            className={`mode-btn ${mode === 'fixed' ? 'active' : ''}`}
            onClick={() => setMode('fixed')}
          >
            ✅ Current Docs
          </button>
          <button
            className={`mode-btn ${mode === 'buggy' ? 'active' : ''}`}
            onClick={() => setMode('buggy')}
          >
            ❌ Outdated Docs
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>👋 Welcome to ZenBot!</h3>
            <p>Ask me about steel specifications, pricing, and delivery.</p>
            <div className="sample-questions">
              <p className="sample-label">Try these questions:</p>
              {sampleQuestions.map((question, idx) => (
                <button
                  key={idx}
                  className="sample-btn"
                  onClick={() => handleSampleClick(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              {message.evaluation && (
                <div className="message-evaluation">
                  <div className="eval-scores">
                    <span className="eval-badge" data-score={message.evaluation.spec_accuracy >= 0.8 ? 'high' : 'low'}>
                      📊 Spec: {(message.evaluation.spec_accuracy * 100).toFixed(0)}%
                    </span>
                    <span className="eval-badge" data-score={message.evaluation.pricing_accuracy >= 0.8 ? 'high' : 'low'}>
                      💰 Price: {(message.evaluation.pricing_accuracy * 100).toFixed(0)}%
                    </span>
                    <span className="eval-badge" data-score={message.evaluation.hallucination_check >= 0.8 ? 'high' : 'low'}>
                      ✨ Safety: {(message.evaluation.hallucination_check * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about steel specifications..."
          rows={2}
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="send-btn"
        >
          {isLoading ? '⏳' : '📤'} Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
