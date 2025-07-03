import React from "react";
import GraphViewer from "./GraphViewer";
import NodeDetails from "./NodeDetails";

const GraphDetail = ({
    graphId,
    graph,
    onBack,
    onNodeClick,
    selectedNodeData,
}) => {
    return (
        <div className="graph-detail">
            <div className="graph-detail-header">
                <button className="back-btn" onClick={onBack}>
                    ← Back to Graphs
                </button>
                <div className="graph-info">
                    <p>Graph: {graphId}</p>
                    <div className="graph-meta">
                        <span>Alerts: {graph.nodes.length}</span>&nbsp;
                        <span>Edges: {graph.edges.length}</span>&nbsp;
                        <span>Created: {new Date(graph.createdAt).toLocaleString()}</span>
                    </div>
                </div>
            </div>

            <div className="graph-detail-content">
                <div className="graph-viewer-section">
                    <GraphViewer
                        graphId={graphId}
                        nodes={graph.nodes}
                        edges={graph.edges}
                        onNodeClick={onNodeClick}
                        selectedNodeData={selectedNodeData}
                        isNewNode={graph.nodes.some((node) => node.data.isNew)}
                        isNewEdge={graph.edges.some((edge) => edge.data.isNew)}
                    />
                </div>

                <div className="node-details-section">
                    <NodeDetails nodeData={selectedNodeData} />
                </div>
            </div>
        </div>
    );
};

export default GraphDetail;

