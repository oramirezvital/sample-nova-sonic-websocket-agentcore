import { useState, useEffect, useRef } from 'react';
import { useVoiceAgent } from './hooks/useVoiceAgent';
import './App.css';

/** Simple markdown-like formatter for chat bubbles */
function FormattedText({ text }: { text: string }) {
  // Split by newlines first
  const lines = text.split('\n');
  
  return (
    <div className="stori-formatted">
      {lines.map((line, i) => {
        if (!line.trim()) return <br key={i} />;
        
        // Process inline formatting: **bold**
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        const formatted = parts.map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={j}>{part.slice(2, -2)}</strong>;
          }
          return <span key={j}>{part}</span>;
        });
        
        // Check if it's a bullet point
        if (line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('·')) {
          return <div key={i} className="stori-formatted__bullet">{formatted}</div>;
        }
        
        return <div key={i} className="stori-formatted__line">{formatted}</div>;
      })}
    </div>
  );
}

function App() {
  const voiceAgent = useVoiceAgent();
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  // Auto-scroll to bottom when conversation history changes
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [voiceAgent.conversationHistory, voiceAgent.isSpeaking]);

  const handleStart = async () => {
    if (!voiceAgent.isConnected && !isConnecting) {
      setIsConnecting(true);
      try {
        await voiceAgent.connect();
        setTimeout(() => {
          voiceAgent.startRecording();
        }, 1000);
      } finally {
        setIsConnecting(false);
      }
    }
  };

  const handleStop = () => {
    voiceAgent.disconnect();
  };

  const hasMessages = voiceAgent.conversationHistory.length > 0;

  return (
    <div className="stori-app">
      {/* Navigation */}
      <nav className="stori-nav">
        <div className="stori-nav__brand">
          <img 
            src="/stori-logo-vector.fd330f3f.svg" 
            alt="Stori" 
            className="stori-nav__logo" 
          />
          <div className="stori-nav__divider" />
          <div>
            <div className="stori-nav__title">Coach Financiero</div>
            <div className="stori-nav__subtitle">Asistente de voz con IA</div>
          </div>
        </div>
        <div className="stori-nav__badge">
          PoC Demo
        </div>
      </nav>

      {/* Main Content */}
      <main className="stori-main">
        {!hasMessages && !voiceAgent.isRecording ? (
          /* Welcome State */
          <div className="stori-welcome">
            <div className="stori-welcome__icon">🎙️</div>
            <h1 className="stori-welcome__heading">
              Tu <span>Coach Financiero</span><br />siempre disponible
            </h1>
            <p className="stori-welcome__description">
              Habla con tu asistente de voz para consultar tu saldo, 
              recibir tips para mejorar tu historial crediticio, 
              y aprovechar al máximo tu Stori.
            </p>
            <div className="stori-welcome__features">
              <div className="stori-welcome__feature">
                <span className="stori-welcome__feature-icon">💳</span>
                Consulta tu saldo y pagos
              </div>
              <div className="stori-welcome__feature">
                <span className="stori-welcome__feature-icon">📈</span>
                Mejora tu score crediticio
              </div>
              <div className="stori-welcome__feature">
                <span className="stori-welcome__feature-icon">💰</span>
                Maximiza tu cashback
              </div>
              <div className="stori-welcome__feature">
                <span className="stori-welcome__feature-icon">🎓</span>
                Tips financieros personalizados
              </div>
            </div>
          </div>
        ) : (
          /* Chat Area */
          <div className="stori-chat">
            <div className="stori-chat__messages" ref={chatContainerRef}>
              {voiceAgent.conversationHistory.map((turn, index) => (
                <div
                  key={`msg-${index}`}
                  className={`stori-bubble stori-bubble--${turn.role}`}
                >
                  <div className="stori-bubble__avatar">
                    {turn.role === 'assistant' ? 'S' : '👤'}
                  </div>
                  <div className="stori-bubble__content">
                    <FormattedText text={turn.transcript} />
                  </div>
                </div>
              ))}
              {voiceAgent.isSpeaking && (
                <div className="stori-bubble stori-bubble--assistant">
                  <div className="stori-bubble__avatar">S</div>
                  <div className="stori-bubble__content">
                    <div className="stori-typing">
                      <div className="stori-typing__dot" />
                      <div className="stori-typing__dot" />
                      <div className="stori-typing__dot" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Bottom Controls */}
      <div className="stori-controls">
        <div className="stori-controls__inner">
          {!voiceAgent.isRecording ? (
            <button
              className="stori-btn-start"
              onClick={handleStart}
              disabled={isConnecting || voiceAgent.isConnected}
            >
              {isConnecting || (voiceAgent.isConnected && !voiceAgent.isRecording) ? (
                <>
                  <span>⏳</span> Conectando...
                </>
              ) : (
                <>
                  <span>🎙️</span> Hablar con mi Coach Financiero
                </>
              )}
            </button>
          ) : (
            <div className="stori-recording-bar">
              <div className="stori-recording-bar__indicator">
                <div className="stori-recording-bar__dot" />
                Escuchando
              </div>
              <div className="stori-recording-bar__visualizer">
                {Array.from({ length: 24 }).map((_, i) => (
                  <div
                    key={i}
                    className="stori-recording-bar__bar"
                    style={{ animationDelay: `${i * 0.05}s` }}
                  />
                ))}
              </div>
              <button className="stori-recording-bar__stop" onClick={handleStop}>
                <div className="stori-recording-bar__stop-icon" />
              </button>
            </div>
          )}
          <div className="stori-powered">
            Powered by <span className="stori-powered__aws">Amazon Bedrock AgentCore</span> + Nova Sonic
          </div>
        </div>
      </div>

      {/* Error Toast */}
      {voiceAgent.error && (
        <div style={{
          position: 'fixed',
          top: '80px',
          left: '50%',
          transform: 'translateX(-50)',
          background: '#FFFFFF',
          border: '1px solid rgba(229, 57, 53, 0.2)',
          borderRadius: '12px',
          padding: '12px 20px',
          color: '#C62828',
          fontSize: '13px',
          zIndex: 200,
          maxWidth: '400px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        }}>
          <span>⚠️</span>
          {voiceAgent.error}
          <button
            onClick={voiceAgent.clearError}
            style={{
              background: 'none',
              border: 'none',
              color: '#8A9BA0',
              cursor: 'pointer',
              marginLeft: '8px',
              fontSize: '16px',
            }}
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
