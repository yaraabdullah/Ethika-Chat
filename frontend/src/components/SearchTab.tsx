import React, { useState } from 'react';
import axios from 'axios';
import { marked } from 'marked';

interface SearchResult {
  id: string;
  metadata: {
    title: string;
    author: string;
    url?: string;
    tags?: string;
    target_audience?: string;
  };
  document: string;
  distance?: number;
}

const SearchTab: React.FC = () => {
  const [query, setQuery] = useState('');
  const [institution, setInstitution] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [tags, setTags] = useState('');
  const [limit, setLimit] = useState(5);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/search', {
        query,
        limit,
        institution: institution || undefined,
        target_audience: targetAudience ? targetAudience.split(',').map(s => s.trim()) : undefined,
        tags: tags ? tags.split(',').map(s => s.trim()) : undefined,
      });

      setResults(response.data.results || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search resources');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>🔍 Search Resources</h2>
      
      <form onSubmit={handleSearch}>
        <div className="form-group">
          <label>Search Query *</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., machine learning activities for elementary students"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Institution (optional)</label>
            <input
              type="text"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="e.g., MIT"
            />
          </div>
          <div className="form-group">
            <label>Target Audience (optional)</label>
            <input
              type="text"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              placeholder="e.g., elementary,middle_school"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Tags (optional)</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="e.g., machine_learning,ethics"
            />
          </div>
          <div className="form-group">
            <label>Number of Results</label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 5)}
              min="1"
              max="20"
            />
          </div>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Searching...' : '🔍 Search'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {results.length > 0 && (
        <div className="results">
          <h3>Found {results.length} results:</h3>
          {results.map((result, index) => {
            // Extract title from document if metadata doesn't have it
            let displayTitle = result.metadata?.title || 'Untitled Resource';
            let displayAuthor = result.metadata?.author || 'Unknown Author';
            
            // Try to extract from document if still missing
            if ((!displayTitle || displayTitle === 'Untitled Resource') && result.document) {
              const titleMatch = result.document.match(/title:\s*"([^"]+)"/i) || 
                                result.document.match(/Title:\s*([^\n]+)/i);
              if (titleMatch) {
                displayTitle = titleMatch[1].trim().replace(/^["']|["']$/g, '');
              }
            }
            
            if ((!displayAuthor || displayAuthor === 'Unknown Author') && result.document) {
              const authorMatch = result.document.match(/author:\s*"([^"]+)"/i) ||
                                 result.document.match(/Author:\s*([^\n]+)/i);
              if (authorMatch) {
                displayAuthor = authorMatch[1].trim().replace(/^["']|["']$/g, '');
              }
            }

            // Extract URL from document if missing in metadata
            let displayUrl = result.metadata?.url || '';
            if (!displayUrl && result.document) {
              const urlMatch = result.document.match(/url:\s*"([^"]+)"/i) ||
                              result.document.match(/URL:\s*"([^"]+)"/i) ||
                              result.document.match(/url:\s*([^\n]+)/i);
              if (urlMatch) {
                displayUrl = urlMatch[1].trim().replace(/^["']|["']$/g, '');
              }
            }

            // Extract target audience from metadata or document
            let targetAudienceList: string[] = [];
            try {
              const audStr = result.metadata?.target_audience;
              if (audStr) {
                if (typeof audStr === 'string') {
                  // Try to parse as JSON first
                  try {
                    targetAudienceList = JSON.parse(audStr);
                  } catch {
                    // If not JSON, try to extract from string format
                    targetAudienceList = audStr.split(',').map(a => a.trim()).filter(a => a);
                  }
                } else if (Array.isArray(audStr)) {
                  targetAudienceList = audStr;
                }
              }
            } catch {
              // Fall through to document extraction
            }
            
            // Try to extract from document if still empty
            if (targetAudienceList.length === 0 && result.document) {
              // Match YAML array format: target_audience: ["elementary", "middle_school"]
              const audienceMatch = result.document.match(/target_audience:\s*\[(.*?)\]/s);
              if (audienceMatch) {
                const audienceStr = audienceMatch[1];
                // Extract quoted strings
                const quotedMatches = audienceStr.match(/"([^"]+)"/g);
                if (quotedMatches) {
                  targetAudienceList = quotedMatches.map(m => m.replace(/"/g, ''));
                } else {
                  // Fallback: split by comma
                  targetAudienceList = audienceStr
                    .split(',')
                    .map(a => a.trim().replace(/^["']|["']$/g, ''))
                    .filter(a => a);
                }
              }
            }

            // Build simple markdown content with title, author, target audience, and link
            const markdownContent = `## ${displayTitle}

**Author:** ${displayAuthor}

${targetAudienceList.length > 0 ? `**Target Audience:** ${targetAudienceList.join(', ')}\n\n` : ''}${displayUrl ? `**Link:** [${displayUrl}](${displayUrl})` : ''}`;

            return (
              <div key={result.id || index} className="result-item" style={{ marginBottom: '2rem' }}>
                <div className="markdown-content" style={{
                  background: 'white',
                  padding: '1.5rem',
                  borderRadius: '8px',
                  border: '1px solid #e0e0e0',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  <div dangerouslySetInnerHTML={{ __html: marked.parse(markdownContent) as string }} />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!loading && results.length === 0 && query && !error && (
        <div className="loading">No results found. Try a different query.</div>
      )}
    </div>
  );
};

export default SearchTab;

