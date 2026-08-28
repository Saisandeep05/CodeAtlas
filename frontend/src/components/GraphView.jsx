import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import EvidencePanel from './EvidencePanel';
import NodeDrawer from './NodeDrawer';
import { Search, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

export default function GraphView({ graphData, repoId, onNodeSelect, selectedNodeId, graphMode = 'FILES', onAskAI }) {
  const fgRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight
      });
    }

    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Compute connected node IDs for highlighting
  const connectedNodeIds = useMemo(() => {
    if (!selectedNodeId || !graphData) return new Set();
    const connected = new Set([selectedNodeId]);
    for (const link of (graphData.links || [])) {
      const srcId = typeof link.source === 'object' ? link.source.id : link.source;
      const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
      if (srcId === selectedNodeId) connected.add(tgtId);
      if (tgtId === selectedNodeId) connected.add(srcId);
    }
    return connected;
  }, [selectedNodeId, graphData]);

  // Compute matching search node IDs
  const matchingNodeIds = useMemo(() => {
    if (!searchQuery.trim() || !graphData?.nodes) return new Set();
    const q = searchQuery.toLowerCase().trim();
    const matches = new Set();
    for (const n of graphData.nodes) {
      if (n.name.toLowerCase().includes(q) || n.id.toLowerCase().includes(q)) {
        matches.add(n.id);
      }
    }
    return matches;
  }, [searchQuery, graphData]);

  // Filter graph based on mode
  const filteredData = useMemo(() => {
    if (!graphData || !graphData.nodes) return { nodes: [], links: [] };

    if (graphMode === 'FULL') return graphData;

    let allowedTypes = [];
    if (graphMode === 'FILES') allowedTypes = ['FILE'];
    if (graphMode === 'CLASSES') allowedTypes = ['FILE', 'CLASS'];
    if (graphMode === 'FUNCTIONS') allowedTypes = ['FILE', 'FUNCTION'];

    const validNodeIds = new Set(
      graphData.nodes.filter(n => allowedTypes.includes(n.type)).map(n => n.id)
    );

    const nodes = graphData.nodes.filter(n => validNodeIds.has(n.id));
    const links = graphData.links.filter(
      l => validNodeIds.has(typeof l.source === 'object' ? l.source.id : l.source) &&
           validNodeIds.has(typeof l.target === 'object' ? l.target.id : l.target)
    );

    return { nodes, links };
  }, [graphData, graphMode]);

  const selectedNode = useMemo(() => {
    if (!selectedNodeId || !graphData?.nodes) return null;
    return graphData.nodes.find(n => n.id === selectedNodeId) || null;
  }, [selectedNodeId, graphData]);

  const getNodeColor = useCallback((node) => {
    // If search active, dim non-matching
    if (searchQuery.trim() && !matchingNodeIds.has(node.id)) {
      return 'rgba(100, 116, 139, 0.15)';
    }

    // If a node is selected, dim unconnected nodes
    if (selectedNodeId && !connectedNodeIds.has(node.id)) {
      return 'rgba(100, 116, 139, 0.25)';
    }
    if (node.id === selectedNodeId) return '#ffffff';
    switch (node.type) {
      case 'FILE': return '#38bdf8';
      case 'CLASS': return '#a78bfa';
      case 'FUNCTION': return '#34d399';
      case 'EXTERNAL': return '#f472b6';
      case 'UNRESOLVED': return '#fb923c';
      case 'AMBIGUOUS': return '#f87171';
      default: return '#94a3b8';
    }
  }, [selectedNodeId, connectedNodeIds, searchQuery, matchingNodeIds]);

  const getNodeSize = useCallback((node) => {
    if (matchingNodeIds.has(node.id)) return 10;
    if (selectedNodeId && !connectedNodeIds.has(node.id)) return 3;
    if (node.id === selectedNodeId) return 8;
    return 6;
  }, [selectedNodeId, connectedNodeIds, matchingNodeIds]);

  const getLinkColor = useCallback((link) => {
    if (link === selectedEdge) return '#ffffff';

    if (selectedNodeId) {
      const srcId = typeof link.source === 'object' ? link.source.id : link.source;
      const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
      if (srcId !== selectedNodeId && tgtId !== selectedNodeId) {
        return 'rgba(255, 255, 255, 0.05)';
      }
    }

    switch (link.resolution_status) {
      case 'VERIFIED': return 'rgba(52, 211, 153, 0.6)';
      case 'EXTERNAL': return 'rgba(244, 114, 182, 0.6)';
      case 'UNRESOLVED': return 'rgba(251, 146, 60, 0.6)';
      case 'AMBIGUOUS': return 'rgba(248, 113, 113, 0.6)';
      default: return 'rgba(255, 255, 255, 0.2)';
    }
  }, [selectedEdge, selectedNodeId]);

  const getLinkWidth = useCallback((link) => {
    if (link === selectedEdge) return 3;
    if (selectedNodeId) {
      const srcId = typeof link.source === 'object' ? link.source.id : link.source;
      const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
      if (srcId === selectedNodeId || tgtId === selectedNodeId) return 2.5;
      return 0.5;
    }
    return 1.5;
  }, [selectedEdge, selectedNodeId]);

  const handleNodeClick = (node) => {
    onNodeSelect(node);
    setSelectedEdge(null);
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(2.5, 2000);
    }
  };

  const handleLinkClick = (link) => {
    setSelectedEdge(link);
  };

  const handleBackgroundClick = () => {
    onNodeSelect(null);
    setSelectedEdge(null);
  };

  const handleSearchSelect = (node) => {
    onNodeSelect(node);
    setSearchQuery(node.name);
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(3, 1500);
    }
  };

  const handleZoomIn = () => fgRef.current?.zoom(fgRef.current.zoom() * 1.3, 400);
  const handleZoomOut = () => fgRef.current?.zoom(fgRef.current.zoom() / 1.3, 400);
  const handleResetZoom = () => fgRef.current?.zoomToFit(400);

  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b' }}>No graph data to display. Paste a repo URL.</div>;
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Search Header Bar Overlay */}
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        zIndex: 20,
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: 'rgba(15, 23, 42, 0.9)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        padding: '6px 12px',
        borderRadius: '8px',
        width: '300px'
      }}>
        <Search size={16} color="#94a3b8" />
        <input
          type="text"
          placeholder="Search symbols or files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            background: 'none',
            border: 'none',
            color: '#f8fafc',
            fontSize: '0.85rem',
            width: '100%',
            outline: 'none'
          }}
        />
        {searchQuery && (
          <span style={{ fontSize: '0.7rem', color: '#38bdf8', fontWeight: 600 }}>
            {matchingNodeIds.size}
          </span>
        )}
      </div>

      {/* Zoom Controls Overlay */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '16px',
        zIndex: 20,
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        background: 'rgba(15, 23, 42, 0.9)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '6px',
        padding: '4px'
      }}>
        <button onClick={handleZoomIn} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '6px' }} title="Zoom In">
          <ZoomIn size={16} />
        </button>
        <button onClick={handleZoomOut} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '6px' }} title="Zoom Out">
          <ZoomOut size={16} />
        </button>
        <button onClick={handleResetZoom} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '6px' }} title="Fit View">
          <Maximize2 size={16} />
        </button>
      </div>

      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={filteredData}
        nodeLabel="name"
        nodeColor={getNodeColor}
        nodeRelSize={6}
        nodeVal={getNodeSize}
        linkColor={getLinkColor}
        linkWidth={getLinkWidth}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        onNodeClick={handleNodeClick}
        onLinkClick={handleLinkClick}
        onBackgroundClick={handleBackgroundClick}
        backgroundColor="transparent"
        linkCurvature={0.2}
      />

      {/* Node Drawer */}
      <NodeDrawer
        selectedNode={selectedNode}
        repoId={repoId}
        onClose={() => onNodeSelect(null)}
        onNodeSelect={handleNodeClick}
        onAskAI={onAskAI}
      />

      {/* Evidence Panel */}
      <EvidencePanel
        selectedEdge={selectedEdge}
        onClose={() => setSelectedEdge(null)}
      />

      {/* Legend */}
      <div className="graph-overlay">
        <h2>Legend</h2>
        <div className="node-legend">
          <div className="legend-item"><div className="legend-color" style={{ backgroundColor: '#38bdf8' }}></div> File</div>
          <div className="legend-item"><div className="legend-color" style={{ backgroundColor: '#a78bfa' }}></div> Class</div>
          <div className="legend-item"><div className="legend-color" style={{ backgroundColor: '#34d399' }}></div> Function</div>
          <div className="legend-item"><div className="legend-color" style={{ backgroundColor: '#f472b6' }}></div> External</div>
          <div className="legend-item"><div className="legend-color" style={{ backgroundColor: '#fb923c' }}></div> Unresolved</div>
          <div className="legend-item"><div className="legend-color" style={{ backgroundColor: '#f87171' }}></div> Ambiguous</div>
        </div>
      </div>
    </div>
  );
}
