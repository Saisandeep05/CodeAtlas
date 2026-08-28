import React from 'react';
import { BarChart3, Clock, FileCode, Box, GitBranch, ShieldCheck, Globe, HelpCircle, AlertTriangle } from 'lucide-react';

const StatBadge = ({ label, count, color }) => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '6px 10px',
    borderRadius: '6px',
    background: `${color}15`,
    border: `1px solid ${color}30`,
  }}>
    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{label}</span>
    <span style={{ fontSize: '0.85rem', fontWeight: 600, color }}>{count}</span>
  </div>
);

export default function AnalysisStats({ statistics }) {
  if (!statistics) return null;

  return (
    <div style={{
      padding: '12px 20px',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    }}>
      <div style={{
        fontSize: '0.75rem',
        fontWeight: 600,
        color: 'var(--text-secondary)',
        display: 'flex',
        alignItems: 'center',
        gap: '6px'
      }}>
        <BarChart3 size={14} /> ANALYSIS STATISTICS
      </div>

      {/* Symbols Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
        <StatBadge label="Files" count={statistics.total_python_files} color="#38bdf8" />
        <StatBadge label="Classes" count={statistics.total_classes} color="#a78bfa" />
        <StatBadge label="Functions" count={statistics.total_functions} color="#34d399" />
        <StatBadge label="Imports" count={statistics.total_imports} color="#818cf8" />
      </div>

      {/* Resolution Breakdown */}
      <div style={{
        fontSize: '0.7rem',
        fontWeight: 600,
        color: 'var(--text-tertiary)',
        marginTop: '4px',
      }}>
        RELATIONSHIP RESOLUTION ({statistics.total_relationships})
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
        <StatBadge label="Verified" count={statistics.verified_count} color="#34d399" />
        <StatBadge label="External" count={statistics.external_count} color="#f472b6" />
        <StatBadge label="Unresolved" count={statistics.unresolved_count} color="#fb923c" />
        <StatBadge label="Ambiguous" count={statistics.ambiguous_count} color="#f87171" />
      </div>

      {/* Duration */}
      {statistics.analysis_duration_seconds > 0 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.75rem',
          color: 'var(--text-tertiary)',
          marginTop: '2px',
        }}>
          <Clock size={12} />
          Analyzed in {statistics.analysis_duration_seconds}s
        </div>
      )}

      {statistics.error_files > 0 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.75rem',
          color: '#fb923c',
        }}>
          <AlertTriangle size={12} />
          {statistics.error_files} file(s) had syntax errors
        </div>
      )}
    </div>
  );
}
