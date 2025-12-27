import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { marked } from 'marked';

interface GenerationResult {
  content: string;
  resources: Array<{
    number: number;
    title: string;
    author: string;
    url?: string;
    relevance?: number;
    citation: string;
    document?: string;
  }>;
  num_resources_used: number;
  prompt: string;
  error?: string;
  llm_used?: boolean;
  quota_error?: boolean;
  note?: string;
}

const PromptGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [history, setHistory] = useState<Array<{ prompt: string; result: GenerationResult }>>([]);
  const [currentResult, setCurrentResult] = useState<GenerationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const contentEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (contentEndRef.current) {
      contentEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentResult, history]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setCurrentResult(null);
    
    try {
      const response = await axios.post('/api/generate-from-prompt', {
        prompt: prompt.trim(),
        max_tokens: 4096,
        use_llm: true  // Will automatically fallback if quota exceeded
      });

      if (response.data.error) {
        setError(response.data.error);
        setCurrentResult(null);
      } else {
        setCurrentResult(response.data);
        setHistory(prev => [...prev, { prompt: prompt.trim(), result: response.data }]);
        setPrompt(''); // Clear prompt after successful generation
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate content');
      setCurrentResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (content: string, prompt: string) => {
    const dataStr = content;
    const dataBlob = new Blob([dataStr], { type: 'text/plain' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `content_${prompt.substring(0, 30).replace(/\s+/g, '_')}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const examplePrompts = [
    "Create a 2-hour workshop on AI ethics for middle school students. Include interactive activities about bias in AI systems.",
    "Design a curriculum for elementary students to learn about machine learning through hands-on activities.",
    "Create educational content about supervised learning for high school students with practical examples.",
    "Develop a workshop on AI bias and fairness for university students, including case studies and discussions."
  ];

  return (
    <div className="card">
      <h2>✨ AI Content Generator</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Describe what educational content you want to create. The AI will comprehensively search our database for all related resources and generate content for you.
      </p>

      {/* Example Prompts */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', color: '#555', fontWeight: 500 }}>
          Example Prompts (click to use):
        </label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {examplePrompts.map((example, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setPrompt(example)}
              style={{
                background: '#f0f0f0',
                border: '1px solid #ddd',
                padding: '0.75rem',
                borderRadius: '5px',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: '0.9rem',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#e8e8e8';
                e.currentTarget.style.borderColor = '#667eea';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#f0f0f0';
                e.currentTarget.style.borderColor = '#ddd';
              }}
            >
              💡 {example}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleGenerate}>
        <div className="form-group">
          <label>Your Prompt *</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Create a 2-hour workshop on AI ethics for middle school students at MIT. Include interactive activities about bias in AI systems, hands-on exercises, and discussion topics."
            required
            rows={5}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '2px solid #e0e0e0',
              borderRadius: '5px',
              fontSize: '1rem',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
        </div>


        <button type="submit" className="btn" disabled={loading || !prompt.trim()}>
          {loading ? '🤖 Generating...' : '✨ Generate Content'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {currentResult && currentResult.quota_error && (
        <div style={{
          background: '#fff3cd',
          border: '1px solid #ffc107',
          padding: '1rem',
          borderRadius: '5px',
          margin: '1rem 0',
          color: '#856404'
        }}>
          <strong>⚠️ Quota Notice:</strong> {currentResult.note || 'LLM quota exceeded. Showing curated resources from database.'}
        </div>
      )}

      {currentResult && currentResult.llm_used === false && !currentResult.quota_error && (
        <div style={{
          background: '#d1ecf1',
          border: '1px solid #bee5eb',
          padding: '1rem',
          borderRadius: '5px',
          margin: '1rem 0',
          color: '#0c5460'
        }}>
          <strong>ℹ️ Info:</strong> Content generated from database resources only (LLM not used).
        </div>
      )}

      {/* Current Result */}
      {currentResult && !currentResult.error && (
        <div className="results" style={{ marginTop: '2rem' }}>
          <div className="success" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>✅ Content generated successfully!</span>
            <button
              onClick={() => handleDownload(currentResult.content, currentResult.prompt)}
              className="btn btn-secondary"
            >
              📥 Download
            </button>
          </div>

          <div style={{ marginTop: '1rem', marginBottom: '1rem', color: '#666' }}>
            <strong>Resources Used:</strong> {currentResult.num_resources_used} resources from database
          </div>

          {currentResult.resources.length > 0 && (
            <details style={{ marginBottom: '1rem' }} open>
              <summary style={{ cursor: 'pointer', fontWeight: 500, color: '#667eea', fontSize: '1.1rem' }}>
                📚 Sources Used in Content ({currentResult.resources.length})
              </summary>
              <div style={{ marginTop: '1rem', display: 'grid', gap: '0.75rem' }}>
                {currentResult.resources.map((resource) => (
                  <div 
                    key={resource.number || resource.citation} 
                    style={{ 
                      padding: '1rem', 
                      background: '#f8f9fa', 
                      borderRadius: '5px',
                      borderLeft: '4px solid #667eea',
                      marginBottom: '0.75rem'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <span style={{ 
                        background: '#667eea', 
                        color: 'white', 
                        padding: '0.25rem 0.75rem', 
                        borderRadius: '4px',
                        fontWeight: 'bold',
                        fontSize: '0.9rem'
                      }}>
                        {resource.citation || `[Source ${resource.number}]`}
                      </span>
                      <strong style={{ fontSize: '1.05rem' }}>{resource.title || 'Untitled Resource'}</strong>
                    </div>
                    <div style={{ color: '#666', marginLeft: '1rem' }}>
                      <div><strong>Author:</strong> {resource.author || 'Unknown'}</div>
                      {resource.url && resource.url.trim() && (
                        <div style={{ marginTop: '0.25rem' }}>
                          <strong>URL:</strong>{' '}
                          <a href={resource.url} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>
                            {resource.url}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </details>
          )}
          <div
            style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '8px',
              border: '2px solid #e0e0e0',
              lineHeight: '1.8',
              fontSize: '1rem',
              color: '#333',
              maxHeight: '600px',
              overflowY: 'auto',
              fontFamily: 'Georgia, serif'
            }}
            className="markdown-content"
          >
            <div dangerouslySetInnerHTML={{ __html: marked.parse(String(currentResult.content || '')) as string }} />
          </div>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="results" style={{ marginTop: '2rem' }}>
          <h3>📜 Generation History</h3>
          {history.slice().reverse().map((item, idx) => (
            <details key={idx} style={{ marginBottom: '1rem' }}>
              <summary style={{ cursor: 'pointer', fontWeight: 500, color: '#667eea', padding: '0.5rem' }}>
                {item.prompt.substring(0, 80)}...
              </summary>
              <div style={{ marginTop: '1rem', padding: '1rem', background: '#f8f9fa', borderRadius: '5px' }}>
                <div style={{ marginBottom: '1rem', color: '#666', fontSize: '0.9rem' }}>
                  <strong>Prompt:</strong> {item.prompt}
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Resources Used:</strong> {item.result.num_resources_used}
                </div>
                <div
                  style={{
                    background: 'white',
                    padding: '1.5rem',
                    borderRadius: '5px',
                    lineHeight: '1.6',
                    maxHeight: '400px',
                    overflowY: 'auto',
                    border: '1px solid #ddd'
                  }}
                  className="markdown-content"
                >
                  <div dangerouslySetInnerHTML={{ __html: marked.parse(item.result.content ? String(item.result.content.substring(0, 1000) + (item.result.content.length > 1000 ? '...' : '')) : '') as string }} />
                </div>
                <button
                  onClick={() => handleDownload(item.result.content || '', item.prompt)}
                  className="btn btn-secondary"
                  style={{ marginTop: '1rem' }}
                >
                  📥 Download Full Content
                </button>
              </div>
            </details>
          ))}
        </div>
      )}

      <div ref={contentEndRef} />
    </div>
  );
};

export default PromptGenerator;

