import React from 'react';
import { ShieldCheck, X, ExternalLink, HelpCircle, AlertTriangle, CheckCircle2 } from 'lucide-react';

const STATUS_CONFIG = {
  VERIFIED: {
    bg: 'rgba(52, 211, 153, 0.2)',
    text: '#34d399',
    border: '1px solid #34d399',
    label: '✓ VERIFIED',
    icon: CheckCircle2
  },
  EXTERNAL: {
    bg: 'rgba(244, 114, 182, 0.2)',
    text: '#f472b6',
    border: '1px dashed #f472b6',
    label: '↗ EXTERNAL',
    icon: ExternalLink
  },
  UNRESOLVED: {
    bg: 'rgba(251, 146, 60, 0.2)',
    text: '#fb923c',
    border: '1px dotted #fb923c',
    label: '? UNRESOLVED',
    icon: HelpCircle
  },
  AMBIGUOUS: {
    bg: 'rgba(248, 113, 113, 0.2)',
    text: '#f87171',
    border: '2px dashed #f87171',
    label: '⚠ AMBIGUOUS',
    icon: AlertTriangle
  },
};

export default function EvidencePanel({ selectedEdge, onClose }) {
  if (!selectedEdge) return null;

  const status = STATUS_CONFIG[selectedEdge.resolution_status] || STATUS_CONFIG.UNRESOLVED;
  const StatusIcon = status.icon;

  const sourceName = typeof selectedEdge.source === 'object' ? selectedEdge.source.name || selectedEdge.source.id : selectedEdge.source;
  const targetName = typeof selectedEdge.target === 'object' ? selectedEdge.target.name || selectedEdge.target.id : selectedEdge.target;

  return (
    <div style={{
      position: 'absolute',
      bottom: '20px',
      left: '20px',
      background: 'rgba(15, 23, 42, 0.95)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255, 255, 255, 0.15)',
      padding: '16px',
      borderRadius: '10px',
      width: '360px',
      color: '#f8fafc',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
      zIndex: 30
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
          <ShieldCheck size={18} color="#34d399" /> Relationship Evidence
        </div>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
        >
          <X size={16} />
        </button>
      </div>

      <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ color: '#94a3b8' }}>Type:</span>{' '}
            <span style={{ color: '#818cf8', fontWeight: 600 }}>{selectedEdge.type}</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 8px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontWeight: 700,
            backgroundColor: status.bg,
            color: status.text,
            border: status.border
          }}>
            <StatusIcon size={12} />
            {selectedEdge.resolution_status}
          </div>
        </div>

        <div style={{ fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: '6px' }}>
          <span style={{ color: '#38bdf8' }}>{sourceName}</span>
          {' → '}
          <span style={{ color: '#a78bfa' }}>{targetName}</span>
        </div>

        {selectedEdge.reasoning && (
          <div style={{ fontSize: '0.75rem', color: '#cbd5e1', fontStyle: 'italic' }}>
            {selectedEdge.reasoning}
          </div>
        )}

        {selectedEdge.evidence && (
          <div style={{ marginTop: '4px', background: 'rgba(0,0,0,0.5)', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ color: '#38bdf8', marginBottom: '4px', fontSize: '0.75rem', fontWeight: 600, fontFamily: 'monospace' }}>
              📍 {selectedEdge.evidence.file || 'Unknown'}:{selectedEdge.evidence.line || '?'}
            </div>
            {selectedEdge.evidence.expression && (
              <code style={{ fontSize: '0.75rem', color: '#f1f5f9', wordBreak: 'break-all', display: 'block', background: 'rgba(0,0,0,0.3)', padding: '6px', borderRadius: '4px' }}>
                {selectedEdge.evidence.expression}
              </code>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
