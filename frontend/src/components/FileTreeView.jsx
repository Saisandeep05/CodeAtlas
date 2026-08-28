import React, { useState } from 'react';
import { ChevronRight, ChevronDown, File, Folder } from 'lucide-react';

function TreeNode({ node, depth = 0, onFileClick }) {
  const [expanded, setExpanded] = useState(depth < 2);

  if (node.type === 'file') {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          paddingLeft: `${depth * 16 + 8}px`,
          paddingTop: '3px',
          paddingBottom: '3px',
          cursor: 'pointer',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
          borderRadius: '4px',
          transition: 'background 0.15s',
        }}
        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        onClick={() => onFileClick && onFileClick(node.path)}
      >
        <File size={13} color="#38bdf8" />
        <span>{node.name}</span>
      </div>
    );
  }

  // Directory
  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          paddingLeft: `${depth * 16 + 8}px`,
          paddingTop: '3px',
          paddingBottom: '3px',
          cursor: 'pointer',
          fontSize: '0.75rem',
          fontWeight: 500,
          color: 'var(--text-primary)',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
        <Folder size={13} color="#fbbf24" />
        <span>{node.name}</span>
      </div>
      {expanded && node.children && (
        <div>
          {node.children.map((child, i) => (
            <TreeNode
              key={child.name + i}
              node={child}
              depth={depth + 1}
              onFileClick={onFileClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function FileTreeView({ fileTree, onFileClick }) {
  if (!fileTree || !fileTree.children || fileTree.children.length === 0) {
    return (
      <div style={{
        padding: '16px',
        fontSize: '0.75rem',
        color: 'var(--text-tertiary)'
      }}>
        No files analyzed yet.
      </div>
    );
  }

  return (
    <div style={{ padding: '8px 0', overflow: 'auto', maxHeight: '300px' }}>
      {fileTree.children.map((child, i) => (
        <TreeNode key={child.name + i} node={child} depth={0} onFileClick={onFileClick} />
      ))}
    </div>
  );
}
