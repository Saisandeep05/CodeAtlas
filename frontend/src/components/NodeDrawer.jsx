import React, { useState, useEffect } from 'react';
import { X, ArrowUpRight, ArrowDownLeft, Network, MessageSquare, FileText, Code } from 'lucide-react';
import { getSubGraph, getDependencies, getCallers } from '../services/api';

const TYPE_COLORS = {
  FILE: '#38bdf8',
  CLASS: '#a78bfa',
  FUNCTION: '#34d399',
  EXTERNAL: '#f472b6',
  UNRESOLVED: '#fb923c',
  AMBIGUOUS: '#f87171',
};

export default function NodeDrawer({ selectedNode, repoId, onClose, onNodeSelect, onAskAI, onEvidenceClick }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [deps, setDeps] = useState(null);
  const [callers, setCallers] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedNode || !repoId) return;

    const fetchDetails = async () => {
      setLoading(true);
      try {
        const [depRes, callerRes] = await Promise.all([
          getDependencies(repoId, selectedNode.id),
          getCallers(repoId, selectedNode.id)
        ]);
        setDeps(depRes);
        setCallers(callerRes);
      } catch (err) {
        console.error('Failed to fetch node relationships:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [selectedNode, repoId]);

  if (!selectedNode) return null;

  const nodeColor = TYPE_COLORS[selectedNode.type] || '#94a3b8';

  return (
    <div style={{
      position: 'absolute',
      top: '16px',
      right: '16px',
      width: '360px',
      maxHeight: 'calc(100% - 32px)',
      background: 'rgba(15, 23, 42, 0.95)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
      color: '#f8fafc',
      zIndex: 30,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '0.7rem',
              fontWeight: 700,
              backgroundColor: `${nodeColor}22`,
              color: nodeColor,
              border: `1px solid ${nodeColor}44`
            }}>
              {selectedNode.type}
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'monospace' }}>
              {selectedNode.file || 'External'}
            </span>
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, wordBreak: 'break-all' }}>
            {selectedNode.name}
          </h3>
          <div style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace', marginTop: '4px', wordBreak: 'break-all' }}>
            {selectedNode.id}
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
        >
          <X size={18} />
        </button>
      </div>

      {/* Action Bar */}
      <div style={{
        padding: '8px 16px',
        background: 'rgba(0,0,0,0.2)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        gap: '8px'
      }}>
        <button
          onClick={() => onAskAI && onAskAI(selectedNode)}
          style={{
            flex: 1,
            padding: '6px 12px',
            borderRadius: '6px',
            border: '1px solid var(--accent-color)',
            background: 'rgba(56, 189, 248, 0.1)',
            color: '#38bdf8',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}
        >
          <MessageSquare size={14} /> Ask AI
        </button>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        fontSize: '0.8rem',
        background: 'rgba(0,0,0,0.1)'
      }}>
        {['overview', 'dependencies', 'callers'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: '10px 4px',
              border: 'none',
              background: 'none',
              color: activeTab === tab ? '#38bdf8' : '#94a3b8',
              borderBottom: activeTab === tab ? '2px solid #38bdf8' : '2px solid transparent',
              cursor: 'pointer',
              fontWeight: activeTab === tab ? 600 : 400,
              textTransform: 'capitalize'
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ padding: '16px', overflowY: 'auto', flex: 1, fontSize: '0.85rem' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: '#64748b', padding: '20px' }}>Loading relationships...</div>
        ) : activeTab === 'overview' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '4px' }}>CANONICAL ID</div>
              <code style={{ fontSize: '0.75rem', color: '#cbd5e1', background: 'rgba(0,0,0,0.4)', padding: '6px', borderRadius: '4px', display: 'block', wordBreak: 'break-all' }}>
                {selectedNode.id}
              </code>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '4px' }}>LOCATION</div>
              <div style={{ color: '#cbd5e1' }}>{selectedNode.file || 'External Symbol'}</div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '8px' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#38bdf8' }}>
                  {deps?.nodes ? deps.nodes.length - 1 : 0}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Dependencies</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#34d399' }}>
                  {callers?.nodes ? callers.nodes.length - 1 : 0}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Callers / Dependents</div>
              </div>
            </div>
          </div>
        ) : activeTab === 'dependencies' ? (
          <div>
            {!deps?.nodes || deps.nodes.length <= 1 ? (
              <div style={{ color: '#64748b' }}>No outgoing dependencies found.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {deps.nodes.filter(n => n.id !== selectedNode.id).map(node => (
                  <div
                    key={node.id}
                    onClick={() => onNodeSelect && onNodeSelect(node)}
                    style={{
                      padding: '8px 10px',
                      background: 'rgba(255,255,255,0.03)',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 500, color: '#f1f5f9' }}>{node.name}</div>
                      <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{node.type}</div>
                    </div>
                    <ArrowUpRight size={14} color="#94a3b8" />
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div>
            {!callers?.nodes || callers.nodes.length <= 1 ? (
              <div style={{ color: '#64748b' }}>No incoming callers or dependents.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {callers.nodes.filter(n => n.id !== selectedNode.id).map(node => (
                  <div
                    key={node.id}
                    onClick={() => onNodeSelect && onNodeSelect(node)}
                    style={{
                      padding: '8px 10px',
                      background: 'rgba(255,255,255,0.03)',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 500, color: '#f1f5f9' }}>{node.name}</div>
                      <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{node.type}</div>
                    </div>
                    <ArrowDownLeft size={14} color="#94a3b8" />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
