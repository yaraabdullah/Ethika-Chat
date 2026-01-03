import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { marked } from 'marked';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

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

  const handleDownload = async (result: GenerationResult) => {
    try {
      // Get prompt from result or find it in history
      let promptText = result.prompt || '';
      if (!promptText) {
        const historyItem = history.find(item => item.result === result);
        if (historyItem) {
          promptText = historyItem.prompt;
        }
      }
      if (!promptText) {
        promptText = 'Generated Content';
      }

      // Create a temporary container for the PDF content
      const container = document.createElement('div');
      container.style.padding = '40px';
      container.style.fontFamily = 'Georgia, serif';
      container.style.color = '#333';
      container.style.lineHeight = '1.8';
      container.style.width = '800px';
      container.style.margin = '0 auto';
      container.style.background = 'white';

      // Add title
      const title = document.createElement('h1');
      title.textContent = 'Generated Educational Content';
      title.style.color = '#667eea';
      title.style.borderBottom = '3px solid #667eea';
      title.style.paddingBottom = '10px';
      title.style.marginBottom = '30px';
      container.appendChild(title);

      // Add prompt section
      const promptSection = document.createElement('div');
      promptSection.style.marginBottom = '30px';
      promptSection.style.padding = '15px';
      promptSection.style.background = '#f8f9fa';
      promptSection.style.borderRadius = '5px';
      promptSection.style.borderLeft = '4px solid #667eea';
      const promptLabel = document.createElement('strong');
      promptLabel.textContent = 'Original Prompt: ';
      promptLabel.style.color = '#555';
      promptSection.appendChild(promptLabel);
      promptSection.appendChild(document.createTextNode(promptText));
      container.appendChild(promptSection);

      // Add resources info
      const resourcesInfo = document.createElement('div');
      resourcesInfo.style.marginBottom = '20px';
      resourcesInfo.style.color = '#666';
      resourcesInfo.innerHTML = `<strong>Resources Used:</strong> ${result.num_resources_used} resources from database`;
      container.appendChild(resourcesInfo);

      // Add main content (markdown rendered)
      const contentDiv = document.createElement('div');
      const contentToParse = String(result.content || '');
      let markdownContent: string;
      
      // Use marked.parse - it can return string or Promise
      try {
        const parsed = marked.parse(contentToParse);
        if (typeof parsed === 'string') {
          markdownContent = parsed;
        } else if (parsed instanceof Promise) {
          markdownContent = await parsed;
        } else {
          markdownContent = contentToParse;
        }
      } catch (e) {
        console.error('Error parsing markdown:', e);
        markdownContent = contentToParse;
      }
      
      contentDiv.innerHTML = markdownContent;
      contentDiv.style.marginBottom = '30px';
      
      // Style markdown elements - add styles directly to container
      const style = document.createElement('style');
      style.textContent = `
        #pdf-container h1 { color: #667eea; font-size: 2em; margin-top: 30px; margin-bottom: 15px; }
        #pdf-container h2 { color: #667eea; font-size: 1.5em; margin-top: 25px; margin-bottom: 12px; }
        #pdf-container h3 { color: #555; font-size: 1.3em; margin-top: 20px; margin-bottom: 10px; }
        #pdf-container p { margin-bottom: 15px; }
        #pdf-container ul, #pdf-container ol { margin-bottom: 15px; padding-left: 30px; }
        #pdf-container li { margin-bottom: 8px; }
        #pdf-container strong { color: #333; }
        #pdf-container code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
        #pdf-container pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; margin-bottom: 15px; }
        #pdf-container blockquote { border-left: 4px solid #667eea; padding-left: 15px; margin-left: 0; color: #666; font-style: italic; }
        #pdf-container table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        #pdf-container th, #pdf-container td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        #pdf-container th { background: #667eea; color: white; }
      `;
      container.id = 'pdf-container';
      container.insertBefore(style, container.firstChild);
      container.appendChild(contentDiv);

      // Add sources section
      if (result.resources && result.resources.length > 0) {
        const sourcesTitle = document.createElement('h2');
        sourcesTitle.textContent = `📚 Sources Used in Content (${result.resources.length})`;
        sourcesTitle.style.marginTop = '40px';
        sourcesTitle.style.paddingTop = '20px';
        sourcesTitle.style.borderTop = '2px solid #e0e0e0';
        container.appendChild(sourcesTitle);

        result.resources.forEach((resource) => {
          const sourceDiv = document.createElement('div');
          sourceDiv.style.marginBottom = '20px';
          sourceDiv.style.padding = '15px';
          sourceDiv.style.background = '#f8f9fa';
          sourceDiv.style.borderRadius = '5px';
          sourceDiv.style.borderLeft = '4px solid #667eea';

          const citation = document.createElement('div');
          citation.style.marginBottom = '10px';
          citation.innerHTML = `<strong style="background: #667eea; color: white; padding: 5px 12px; border-radius: 4px; display: inline-block; margin-right: 10px;">${resource.citation || `[Source ${resource.number}]`}</strong><strong style="font-size: 1.1em;">${resource.title || 'Untitled Resource'}</strong>`;
          sourceDiv.appendChild(citation);

          const authorDiv = document.createElement('div');
          authorDiv.style.color = '#666';
          authorDiv.style.marginLeft = '10px';
          authorDiv.innerHTML = `<strong>Author:</strong> ${resource.author || 'Unknown'}`;
          sourceDiv.appendChild(authorDiv);

          if (resource.url && resource.url.trim()) {
            const urlDiv = document.createElement('div');
            urlDiv.style.color = '#666';
            urlDiv.style.marginLeft = '10px';
            urlDiv.style.marginTop = '5px';
            urlDiv.innerHTML = `<strong>URL:</strong> ${resource.url}`;
            sourceDiv.appendChild(urlDiv);
          }

          container.appendChild(sourceDiv);
        });
      }

      // Add to DOM - position off-screen but visible for html2canvas
      container.style.position = 'fixed';
      container.style.top = '0';
      container.style.left = '0';
      container.style.width = '800px';
      container.style.maxWidth = '100vw';
      container.style.height = 'auto';
      container.style.visibility = 'visible';
      container.style.opacity = '1';
      container.style.zIndex = '-1';
      container.style.background = 'white';
      document.body.appendChild(container);

      // Wait for rendering
      await new Promise(resolve => requestAnimationFrame(resolve));
      await new Promise(resolve => requestAnimationFrame(resolve));
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Verify content exists
      const hasText = container.textContent && container.textContent.trim().length > 0;
      const hasHTML = container.innerHTML && container.innerHTML.trim().length > 100;
      if (!hasText && !hasHTML) {
        console.error('PDF container is empty!', {
          textContent: container.textContent?.substring(0, 100),
          innerHTML: container.innerHTML.substring(0, 200),
          contentLength: result.content?.length
        });
        document.body.removeChild(container);
        alert('Error: Content is empty. Please try generating content again.');
        return;
      }

      // Use html2canvas to capture the container
      const canvas = await html2canvas(container, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        width: container.scrollWidth,
        height: container.scrollHeight,
        windowWidth: container.scrollWidth,
        windowHeight: container.scrollHeight
      });

      // Clean up container
      document.body.removeChild(container);

      // Calculate PDF dimensions (A4 in mm)
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 297; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgData = canvas.toDataURL('image/png');

      // Add first page
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Add additional pages if content is taller than one page
      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Save PDF
      pdf.save(`content_${promptText.substring(0, 50).replace(/[^a-z0-9]/gi, '_')}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
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
              onClick={() => handleDownload(currentResult)}
              className="btn btn-secondary"
            >
              📥 Download PDF
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
                  onClick={() => handleDownload(item.result)}
                  className="btn btn-secondary"
                  style={{ marginTop: '1rem' }}
                >
                  📥 Download PDF
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

