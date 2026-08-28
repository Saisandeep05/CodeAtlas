import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300000, // 5 minutes for large repos
});

/**
 * Analyze a GitHub repository.
 * @param {string} repoUrl - Public GitHub repository URL
 * @returns {Promise<{repo_id, repository_name, status, commit_hash, graph, statistics, file_tree}>}
 */
export const analyzeRepo = (repoUrl) =>
  api.post('/analyze', { repo_url: repoUrl }).then(res => res.data);

/**
 * Get the architecture graph for a repository.
 * @param {number} repoId
 * @param {string} mode - One of: FILES, CLASSES, FUNCTIONS, FULL
 * @returns {Promise<{nodes, links}>}
 */
export const getRepoGraph = (repoId, mode = 'FULL') =>
  api.get(`/repo/${repoId}/graph`, { params: { mode } }).then(res => res.data);

/**
 * Get repository metadata.
 * @param {number} repoId
 * @returns {Promise<{id, url, repository_name, commit_hash, status, analysis_duration, analyzed_at, statistics}>}
 */
export const getRepoMeta = (repoId) =>
  api.get(`/repo/${repoId}`).then(res => res.data);

/**
 * Get the hierarchical file tree for a repository.
 * @param {number} repoId
 * @returns {Promise<{name, type, children}>}
 */
export const getRepoTree = (repoId) =>
  api.get(`/repo/${repoId}/tree`).then(res => res.data);

/**
 * Get a focused subgraph around node_id up to depth.
 */
export const getSubGraph = (repoId, nodeId, depth = 2) =>
  api.get(`/repo/${repoId}/subgraph/${encodeURIComponent(nodeId)}`, { params: { depth } }).then(res => res.data);

/**
 * Get details for a single node.
 */
export const getNodeDetails = (repoId, nodeId) =>
  api.get(`/repo/${repoId}/node/${encodeURIComponent(nodeId)}`).then(res => res.data);

/**
 * Get evidence details for an edge.
 */
export const getEdgeEvidence = (repoId, edgeId) =>
  api.get(`/repo/${repoId}/evidence/${encodeURIComponent(edgeId)}`).then(res => res.data);

/**
 * Get outgoing dependencies for a node.
 */
export const getDependencies = (repoId, nodeId, transitive = false) =>
  api.get(`/repo/${repoId}/dependencies/${encodeURIComponent(nodeId)}`, { params: { transitive } }).then(res => res.data);

/**
 * Get incoming callers/dependents for a node.
 */
export const getCallers = (repoId, nodeId, transitive = false) =>
  api.get(`/repo/${repoId}/callers/${encodeURIComponent(nodeId)}`, { params: { transitive } }).then(res => res.data);

/**
 * Get shortest path between source_id and target_id.
 */
export const getShortestPath = (repoId, sourceId, targetId) =>
  api.get(`/repo/${repoId}/path`, { params: { source: sourceId, target: targetId } }).then(res => res.data);

/**
 * Chat with the architecture assistant about a repository.
 * @param {number} repoId
 * @param {string|null} nodeId - Selected graph node ID
 * @param {string} question
 * @param {string|null} apiKey - Optional Gemini API key
 * @returns {Promise<{answer, answer_type, response_source, verification_level, llm_used, verified_context_used?}>}
 */
export const chatWithRepo = (repoId, nodeId, question, apiKey) =>
  api.post('/chat', {
    repo_id: repoId,
    node_id: nodeId || null,
    question,
    api_key: apiKey || undefined,
  }).then(res => res.data);

export default api;
