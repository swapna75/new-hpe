import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

const TestControls = ({ onSendMessage }) => {
    const [graphId, setGraphId] = useState('test-graph-1');
    const [nodeId, setNodeId] = useState('');
    const [nodeLabel, setNodeLabel] = useState('');
    const [parentId, setParentId] = useState('');
    const [isRoot, setIsRoot] = useState(false);

    const createGraph = () => {
        const newGraphId = `test-graph-${Date.now()}`;
        setGraphId(newGraphId);
        
        // Create sample alerts with parent-child relationships
        const alerts = [
            {
                id: "root-alert-1",
                parent_id: "", // Root alert (no parent)
                service: "main-service",
                summary: "Database connection timeout"
            },
            {
                id: "child-alert-1", 
                parent_id: "root-alert-1", // Child of root
                service: "database-service",
                summary: "Connection pool exhausted"
            },
            {
                id: "child-alert-2",
                parent_id: "root-alert-1", // Another child of root
                service: "network-service", 
                summary: "Network latency spike"
            },
            {
                id: "grandchild-alert-1",
                parent_id: "child-alert-1", // Child of child
                service: "cache-service",
                summary: "Cache miss rate increased"
            }
        ];
        
        const message = {
            type: 'create_graph',
            group_id: newGraphId,
            alerts: alerts
        };
        
        onSendMessage(message);
    };

    const addNode = () => {
        const newNodeId = nodeId || `node-${Date.now()}`;
        const newNodeLabel = nodeLabel || `Node ${newNodeId}`;
        
        const message = {
            type: 'add_node',
            graph_id: graphId,
            node_data: {
                id: newNodeId,
                label: newNodeLabel,
                parentId: parentId || null,
                isRoot: isRoot,
                timestamp: new Date().toISOString(),
                properties: {
                    service: 'test-service',
                    environment: 'development'
                },
                metadata: {
                    created_by: 'test-user',
                    version: '1.0.0'
                }
            }
        };
        
        onSendMessage(message);
        
        // Reset form
        setNodeId('');
        setNodeLabel('');
        setParentId('');
        setIsRoot(false);
    };

    const addEdge = () => {
        const message = {
            type: 'add_edge',
            graph_id: graphId,
            edge_data: {
                source: parentId || 'root',
                target: nodeId || `node-${Date.now()}`,
                label: `Edge ${parentId || 'root'} -> ${nodeId || 'new-node'}`,
                timestamp: new Date().toISOString()
            }
        };
        
        onSendMessage(message);
    };

    const sendTestSequence = () => {
        // Create a graph with all nodes and edges at once
        const testGraphId = `test-graph-${Date.now()}`;
        setGraphId(testGraphId);
        
        const alerts = [
            {
                id: 'root',
                parent_id: '', // Root alert
                service: 'main-service',
                summary: 'Root Cause Alert'
            },
            {
                id: 'child1',
                parent_id: 'root', // Child of root
                service: 'database-service',
                summary: 'Database Connection Issue'
            },
            {
                id: 'child2',
                parent_id: 'root', // Another child of root
                service: 'network-service',
                summary: 'Network Timeout'
            },
            {
                id: 'grandchild1',
                parent_id: 'child1', // Child of child1
                service: 'cache-service',
                summary: 'Cache Miss'
            }
        ];
        
        onSendMessage({
            type: 'create_graph',
            group_id: testGraphId,
            alerts: alerts
        });
    };

    const testSingleRootNode = () => {
        const testGraphId = `single-root-test-${Date.now()}`;
        setGraphId(testGraphId);
        
        const alerts = [
            {
                id: 'test-root',
                parent_id: '', // Root alert (no parent)
                service: 'test-service',
                summary: 'Test Root Alert'
            }
        ];
        
        // Create graph with single root node
        onSendMessage({
            type: 'create_graph',
            group_id: testGraphId,
            alerts: alerts
        });
    };

    const testComplexGraph = () => {
        const testGraphId = `complex-graph-${Date.now()}`;
        setGraphId(testGraphId);
        
        const alerts = [
            {
                id: 'root-1',
                parent_id: '', // Root alert
                service: 'main-service',
                summary: 'Primary Service Failure'
            },
            {
                id: 'root-2',
                parent_id: '', // Another root alert
                service: 'auth-service',
                summary: 'Authentication Service Down'
            },
            {
                id: 'child-1-1',
                parent_id: 'root-1', // Child of root-1
                service: 'database-service',
                summary: 'Database Connection Lost'
            },
            {
                id: 'child-1-2',
                parent_id: 'root-1', // Another child of root-1
                service: 'cache-service',
                summary: 'Cache Service Unavailable'
            },
            {
                id: 'child-2-1',
                parent_id: 'root-2', // Child of root-2
                service: 'ldap-service',
                summary: 'LDAP Server Unreachable'
            },
            {
                id: 'grandchild-1-1-1',
                parent_id: 'child-1-1', // Child of child-1-1
                service: 'storage-service',
                summary: 'Storage System Overloaded'
            },
            {
                id: 'grandchild-1-2-1',
                parent_id: 'child-1-2', // Child of child-1-2
                service: 'redis-service',
                summary: 'Redis Memory Full'
            }
        ];
        
        onSendMessage({
            type: 'create_graph',
            group_id: testGraphId,
            alerts: alerts
        });
    };

    return (
        <div className="test-controls">
            <h3>Test Controls</h3>
            
            <div className="control-section">
                <h4>Create Graph</h4>
                <button onClick={createGraph} className="test-btn">
                    Create New Graph
                </button>
            </div>

            <div className="control-section">
                <h4>Add Node</h4>
                <div className="form-group">
                    <label>Graph ID:</label>
                    <input
                        type="text"
                        value={graphId}
                        onChange={(e) => setGraphId(e.target.value)}
                        placeholder="Graph ID"
                    />
                </div>
                <div className="form-group">
                    <label>Node ID:</label>
                    <input
                        type="text"
                        value={nodeId}
                        onChange={(e) => setNodeId(e.target.value)}
                        placeholder="Node ID (optional)"
                    />
                </div>
                <div className="form-group">
                    <label>Label:</label>
                    <input
                        type="text"
                        value={nodeLabel}
                        onChange={(e) => setNodeLabel(e.target.value)}
                        placeholder="Node Label (optional)"
                    />
                </div>
                <div className="form-group">
                    <label>Parent ID:</label>
                    <input
                        type="text"
                        value={parentId}
                        onChange={(e) => setParentId(e.target.value)}
                        placeholder="Parent ID (optional)"
                    />
                </div>
                <div className="form-group">
                    <label>
                        <input
                            type="checkbox"
                            checked={isRoot}
                            onChange={(e) => setIsRoot(e.target.checked)}
                        />
                        Is Root Node (only one per graph)
                    </label>
                </div>
                <button onClick={addNode} className="test-btn">
                    Add Node
                </button>
            </div>

            <div className="control-section">
                <h4>Add Edge</h4>
                <button onClick={addEdge} className="test-btn">
                    Add Edge
                </button>
            </div>

            <div className="control-section">
                <h4>Test Sequence</h4>
                <button onClick={sendTestSequence} className="test-btn primary">
                    Run Test Sequence
                </button>
            </div>

            <div className="control-section">
                <h4>Test Single Root Node</h4>
                <button onClick={testSingleRootNode} className="test-btn primary">
                    Test Single Root Node
                </button>
            </div>

            <div className="control-section">
                <h4>Test Complex Graph</h4>
                <button onClick={testComplexGraph} className="test-btn primary">
                    Test Complex Graph
                </button>
            </div>
        </div>
    );
};

export default TestControls; 