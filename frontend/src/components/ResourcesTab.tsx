import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Resource {
  id: string;
  metadata: {
    title: string;
    author: string;
    url?: string;
    year?: string;
  };
}

const ResourcesTab: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get('/resources');
      setResources(response.data.resources || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const filteredResources = resources.filter(resource => {
    if (!filter) return true;
    const searchTerm = filter.toLowerCase();
    const title = (resource.metadata.title || '').toLowerCase();
    const author = (resource.metadata.author || '').toLowerCase();
    return title.includes(searchTerm) || author.includes(searchTerm);
  });

  return (
    <div className="card">
      <h2>📋 All Resources</h2>
      
      <div className="form-group">
        <label>Filter by title or author</label>
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Search resources..."
        />
      </div>

      <button onClick={loadResources} className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
        🔄 Refresh
      </button>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Loading resources...</div>
      ) : (
        <>
          <div style={{ marginBottom: '1rem', color: '#666' }}>
            Showing {filteredResources.length} of {resources.length} resources
          </div>

          <div className="resource-list">
            {filteredResources.length === 0 ? (
              <div className="loading">No resources found</div>
            ) : (
              filteredResources.map((resource) => (
                <div key={resource.id} className="resource-item">
                  <h3>{resource.metadata.title || 'Untitled'}</h3>
                  <div className="meta">
                    <strong>Author:</strong> {resource.metadata.author || 'Unknown'}
                    {resource.metadata.year && (
                      <> | <strong>Year:</strong> {resource.metadata.year}</>
                    )}
                    {resource.metadata.url && (
                      <>
                        <br />
                        <strong>URL:</strong>{' '}
                        <a href={resource.metadata.url} target="_blank" rel="noopener noreferrer">
                          {resource.metadata.url}
                        </a>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ResourcesTab;

