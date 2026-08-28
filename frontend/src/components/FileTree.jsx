import React from 'react';
import { File, Folder, Box, ChevronRight, Hash } from 'lucide-react';

export default function FileTree({ graphData, onNodeSelect, selectedNodeId }) {
  if (!graphData || !graphData.nodes) {
    return <div className="file-tree">No repository loaded.</div>;
  }

  // Extract just the files from graph data
  const fileNodes = graphData.nodes.filter(n => n.type === 'FILE');

  return (
    <div className="file-tree">
      {fileNodes.map(node => (
        <div 
          key={node.id} 
          className={`tree-item ${selectedNodeId === node.id ? 'active' : ''}`}
          onClick={() => onNodeSelect(node)}
        >
          <File size={16} color="var(--graph-node-file)" />
          <span>{node.name.split('/').pop()}</span>
        </div>
      ))}
      {fileNodes.length === 0 && <div className="text-sm text-gray-500">No Python files found.</div>}
    </div>
  );
}
