import React, { useState } from 'react';
import GraphView from './components/GraphView';
import ChatPanel from './components/ChatPanel';
import FileTreeView from './components/FileTreeView';
import AnalysisStats from './components/AnalysisStats';
import { analyzeRepo } from './services/api';
import { Layers, FolderGit2 } from 'lucide-react';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [graphMode, setGraphMode] = useState('FILES');
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;

    setAnalyzing(true);
    setError(null);
    setAnalysisResult(null);
    setSelectedNode(null);

    try {
      const data = await analyzeRepo(repoUrl.trim());
      setAnalysisResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileSelect = (filePath) => {
    if (!analysisResult || !analysisResult.graph) return;
    const fileNodeId = `file:${filePath}`;
    const foundNode = analysisResult.graph.nodes.find(n => n.id === fileNodeId);
    if (foundNode) {
      setSelectedNode(foundNode);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="panel-header">
          <h1><Layers size={18} style={{display: 'inline', marginRight: '6px', verticalAlign: 'text-bottom'}}/> CodeAtlas</h1>
          <p>Verified Architecture Explorer</p>
        </div>

        <div className="repo-loader">
          <form onSubmit={handleAnalyze} style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
            <input
              type="text"
              placeholder="GitHub Repo URL (Python)"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
            />
            <button type="submit" disabled={analyzing}>
              {analyzing ? 'Analyzing Architecture...' : 'Load Repository'}
            </button>
          </form>

          {/* Quick-Select Sample Repositories for Demo Frictionless Testing */}
          <div style={{ marginTop: '12px' }}>
            <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginBottom: '6px' }}>
              Quick Try Sample Repos:
            </div>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {[
                { name: 'flask', url: 'https://github.com/pallets/flask' },
                { name: 'requests', url: 'https://github.com/psf/requests' },
                { name: 'fastapi', url: 'https://github.com/fastapi/fastapi' }
              ].map(sample => (
                <button
                  key={sample.name}
                  type="button"
                  onClick={() => {
                    setRepoUrl(sample.url);
                    analyzeRepo(sample.url)
                      .then(data => {
                        setAnalysisResult(data);
                        setError(null);
                      })
                      .catch(err => setError(err.response?.data?.detail || err.message));
                  }}
                  style={{
                    background: 'rgba(56, 189, 248, 0.1)',
                    border: '1px solid rgba(56, 189, 248, 0.25)',
                    color: '#38bdf8',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  ⚡ {sample.name}
                </button>
              ))}
            </div>
          </div>

          {error && <div style={{color: '#ef4444', fontSize: '0.85rem', marginTop: '8px', padding: '8px', background: 'rgba(239,68,68,0.1)', borderRadius: '4px'}}>{error}</div>}
        </div>

        {/* Repository Metadata */}
        {analysisResult && (
          <div style={{
            padding: '10px 20px',
            background: 'rgba(255,255,255,0.02)',
            borderBottom: '1px solid var(--border-color)',
            fontSize: '0.8rem',
            color: 'var(--text-secondary)'
          }}>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FolderGit2 size={14} color="#38bdf8" /> {analysisResult.repository_name || 'Repository'}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginTop: '2px' }}>
              Commit: {analysisResult.commit_hash?.slice(0, 7)} ({analysisResult.status})
            </div>
          </div>
        )}

        {/* Analysis Statistics Sidebar Section */}
        {analysisResult && analysisResult.statistics && (
          <AnalysisStats statistics={analysisResult.statistics} />
        )}

        {/* Graph Mode Filter Controls */}
        {analysisResult && (
          <div style={{padding: '12px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px'}}>
            <div style={{fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)'}}>GRAPH MODE</div>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px'}}>
              {['FILES', 'CLASSES', 'FUNCTIONS', 'FULL'].map(mode => (
                <button
                  key={mode}
                  onClick={() => setGraphMode(mode)}
                  style={{
                    padding: '6px',
                    fontSize: '0.75rem',
                    borderRadius: '4px',
                    border: '1px solid var(--border-color)',
                    background: graphMode === mode ? 'var(--accent-color)' : 'var(--bg-card)',
                    color: graphMode === mode ? '#ffffff' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* File Tree View */}
        {analysisResult && analysisResult.file_tree && (
          <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '8px 20px 0 20px', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              FILE EXPLORER
            </div>
            <FileTreeView
              fileTree={analysisResult.file_tree}
              onFileClick={handleFileSelect}
            />
          </div>
        )}
      </div>

      <div className="main-content">
        {analyzing ? (
          <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '16px', color: '#94a3b8'}}>
            <div className="loader-spinner"></div>
            <div>Static Analysis & Symbol Resolution in Progress...</div>
          </div>
        ) : (
          <GraphView
            graphData={analysisResult?.graph}
            repoId={analysisResult?.repo_id}
            onNodeSelect={setSelectedNode}
            selectedNodeId={selectedNode?.id}
            graphMode={graphMode}
            onAskAI={(node) => setSelectedNode(node)}
          />
        )}
      </div>

      <ChatPanel
        repoId={analysisResult?.repo_id}
        repoUrl={analysisResult ? repoUrl : null}
        selectedNode={selectedNode}
      />
    </div>
  );
}

export default App;
