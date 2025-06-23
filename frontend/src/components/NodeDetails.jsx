import React from "react";

const NodeDetails = ({ nodeData }) => {
    if (!nodeData) {
        return (
            <div className="node-details empty">
                <h3>Node Details</h3>
                <p>Click on a node to view its details</p>
            </div>
        );
    }

    const formatValue = (value) => {
        if (typeof value === "object") {
            return JSON.stringify(value, null, 2);
        }
        return String(value);
    };

    const renderDataSection = (title, data) => {
        if (!data || Object.keys(data).length === 0) return null;

        return (
            <div className="data-section">
                <h4>{title}</h4>
                <div className="data-grid">
                    {Object.entries(data).map(([key, value]) => (
                        <div key={key} className="data-item">
                            <span className="data-key">{key}:</span>
                            <span className="data-value">{formatValue(value)}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="node-details">
            <div className="node-header">
                <h3>Node Details</h3>
                <div className="node-badge">
                    {nodeData.isRoot && <span className="root-badge">Root</span>}
                </div>
            </div>

            <div className="node-content">
                <div className="basic-info">
                    <h4>Basic Information</h4>
                    <div className="info-grid">
                        <div className="info-item">
                            <span className="info-label">ID:</span>
                            <span className="info-value">{nodeData.id}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Label:</span>
                            <span className="info-value">{nodeData.label}</span>
                        </div>
                        {nodeData.parentId && (
                            <div className="info-item">
                                <span className="info-label">Parent ID:</span>
                                <span className="info-value">{nodeData.parentId}</span>
                            </div>
                        )}
                    </div>
                </div>

                {renderDataSection("Properties", nodeData.properties)}
                {renderDataSection("Metadata", nodeData.metadata)}
                {renderDataSection("Additional Data", nodeData.additionalData)}

                {nodeData.timestamp && (
                    <div className="timestamp">
                        <span className="timestamp-label">Created:</span>
                        <span className="timestamp-value">
                            {new Date(nodeData.timestamp).toLocaleString()}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default NodeDetails;

