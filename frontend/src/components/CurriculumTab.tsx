import React, { useState } from 'react';
import axios from 'axios';

interface Curriculum {
  institution: string;
  target_audience: string[];
  topics: string[];
  duration_hours: number;
  resources: Array<{
    metadata: {
      title: string;
      author: string;
      url?: string;
    };
  }>;
  detailed_content?: {
    overview?: string;
    learning_objectives?: string[];
    schedule?: Array<{
      time?: string;
      activity?: string;
    }>;
  };
}

const CurriculumTab: React.FC = () => {
  const [institution, setInstitution] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [topics, setTopics] = useState('');
  const [duration, setDuration] = useState(2.0);
  const [useAdvanced, setUseAdvanced] = useState(false);
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!institution || !targetAudience || !topics) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/curriculum', {
        institution,
        target_audience: targetAudience.split(',').map(s => s.trim()),
        topics: topics.split(',').map(s => s.trim()),
        duration_hours: duration,
        use_advanced: useAdvanced,
      });

      setCurriculum(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate curriculum');
      setCurriculum(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!curriculum) return;
    
    const dataStr = JSON.stringify(curriculum, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `curriculum_${institution.replace(/\s+/g, '_')}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card">
      <h2>📚 Generate Curriculum</h2>
      
      <form onSubmit={handleGenerate}>
        <div className="form-row">
          <div className="form-group">
            <label>Institution *</label>
            <input
              type="text"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="e.g., MIT"
              required
            />
          </div>
          <div className="form-group">
            <label>Target Audience *</label>
            <input
              type="text"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              placeholder="e.g., elementary,middle_school"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Topics *</label>
            <input
              type="text"
              value={topics}
              onChange={(e) => setTopics(e.target.value)}
              placeholder="e.g., machine_learning,ethics"
              required
            />
          </div>
          <div className="form-group">
            <label>Duration (hours)</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseFloat(e.target.value) || 2.0)}
              min="0.5"
              max="8"
              step="0.5"
            />
          </div>
        </div>

        <div className="checkbox-group">
          <input
            type="checkbox"
            id="advanced"
            checked={useAdvanced}
            onChange={(e) => setUseAdvanced(e.target.checked)}
          />
          <label htmlFor="advanced">Use advanced LLM generation (with Gemini API)</label>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Generating...' : '📚 Generate Curriculum'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {curriculum && (
        <div className="results">
          <div className="success">
            ✅ Curriculum generated successfully!
            <button onClick={handleDownload} className="btn btn-secondary" style={{ marginLeft: '1rem' }}>
              📥 Download JSON
            </button>
          </div>

          <h3>Curriculum Summary</h3>
          <div className="form-row" style={{ marginBottom: '1rem' }}>
            <div><strong>Institution:</strong> {curriculum.institution}</div>
            <div><strong>Duration:</strong> {curriculum.duration_hours} hours</div>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <strong>Target Audience:</strong> {curriculum.target_audience.join(', ')}
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <strong>Topics:</strong> {curriculum.topics.join(', ')}
          </div>

          <h3>Selected Resources ({curriculum.resources.length})</h3>
          {curriculum.resources.map((resource, index) => (
            <div key={index} className="result-item">
              <h4>{resource.metadata.title || 'Untitled'}</h4>
              <div className="meta">
                <strong>Author:</strong> {resource.metadata.author || 'Unknown'}
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
          ))}

          {curriculum.detailed_content && (
            <>
              <h3>Detailed Content</h3>
              {curriculum.detailed_content.overview && (
                <div className="result-item">
                  <h4>Overview</h4>
                  <p>{curriculum.detailed_content.overview}</p>
                </div>
              )}
              {curriculum.detailed_content.learning_objectives && (
                <div className="result-item">
                  <h4>Learning Objectives</h4>
                  <ul>
                    {curriculum.detailed_content.learning_objectives.map((obj, i) => (
                      <li key={i}>{obj}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default CurriculumTab;

