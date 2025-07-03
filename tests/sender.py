# all the alerts should relate to the same service is not working.
import requests

alerts_with_noise = [
    # === Scenario 1 ===
    [
        # Base
        [
            {
                "labels": {
                    "job": "product-catalog-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:00:00",
                "endsAt": "2025-06-29T00:03:00",
                "status": "firing",
                "annotations": {
                    "description": "Metadata sync delay",
                    "summary": "product-catalog-service experienced 'Metadata sync delay'",
                },
            },
            {
                "labels": {
                    "job": "inventory-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:00:30",
                "endsAt": "2025-06-29T00:03:30",
                "status": "firing",
                "annotations": {
                    "description": "Update failure increase",
                    "summary": "inventory-service experienced 'Update failure increase'",
                },
            },
            {
                "labels": {
                    "job": "order-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:01:00",
                "endsAt": "2025-06-29T00:04:00",
                "status": "firing",
                "annotations": {
                    "description": "Order backlog risk",
                    "summary": "order-service experienced 'Order backlog risk'",
                },
            },
            {
                "labels": {
                    "job": "payment-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:01:30",
                "endsAt": "2025-06-29T00:04:30",
                "status": "firing",
                "annotations": {
                    "description": "Gateway timeout spike",
                    "summary": "payment-service experienced 'Gateway timeout spike'",
                },
            },
        ],
        # + Type 1 # remove this this is a alert which is correlated.
        [
            {
                "labels": {
                    "job": "shipping-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:02:00",
                "endsAt": "2025-06-29T00:05:00",
                "status": "firing",
                "annotations": {
                    "description": "Shipping delay warning",
                    "summary": "shipping-service experienced 'Shipping delay warning'",
                },
            }
        ],
        # + Type 2
        [
            {
                "labels": {
                    "job": "user-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:02:30",
                "endsAt": "2025-06-29T00:05:30",
                "status": "firing",
                "annotations": {
                    "description": "Session latency high",
                    "summary": "user-service experienced 'Session latency high'",
                },
            }
        ],
    ],
    # === Scenario 2 ===
    [
        # Base
        [
            {
                "labels": {
                    "job": "user-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T01:00:00",
                "endsAt": "2025-06-29T01:03:00",
                "status": "firing",
                "annotations": {
                    "description": "Auth failure spike",
                    "summary": "user-service experienced 'Auth failure spike'",
                },
            },
            {
                "labels": {
                    "job": "order-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T01:00:30",
                "endsAt": "2025-06-29T01:03:30",
                "status": "firing",
                "annotations": {
                    "description": "Validation error surge",
                    "summary": "order-service experienced 'Validation error surge'",
                },
            },
            {
                "labels": {
                    "job": "payment-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T01:01:00",
                "endsAt": "2025-06-29T01:04:00",
                "status": "firing",
                "annotations": {
                    "description": "Gateway timeout spike",
                    "summary": "payment-service experienced 'Gateway timeout spike'",
                },
            },
        ],
        # + Type 1
        [
            {
                "labels": {
                    "job": "shipping-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T01:01:30",
                "endsAt": "2025-06-29T01:04:30",
                "status": "firing",
                "annotations": {
                    "description": "Carrier API failure surge",
                    "summary": "shipping-service experienced 'Carrier API failure surge'",
                },
            }
        ],
        # + Type 2
        [
            {
                "labels": {
                    "job": "inventory-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T01:02:00",
                "endsAt": "2025-06-29T01:05:00",
                "status": "firing",
                "annotations": {
                    "description": "Stock consistency warning",
                    "summary": "inventory-service experienced 'Stock consistency warning'",
                },
            }
        ],
    ],
    # === Scenario 3 ===
    [
        # Base
        [
            {
                "labels": {
                    "job": "product-catalog-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T03:00:00",
                "endsAt": "2025-06-29T03:03:00",
                "status": "firing",
                "annotations": {
                    "description": "Read error surge",
                    "summary": "product-catalog-service experienced 'Read error surge'",
                },
            },
            {
                "labels": {
                    "job": "inventory-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T03:00:30",
                "endsAt": "2025-06-29T03:03:30",
                "status": "firing",
                "annotations": {
                    "description": "Update failure increase",
                    "summary": "inventory-service experienced 'Update failure increase'",
                },
            },
            {
                "labels": {
                    "job": "order-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T03:01:00",
                "endsAt": "2025-06-29T03:04:00",
                "status": "firing",
                "annotations": {
                    "description": "Order backlog risk",
                    "summary": "order-service experienced 'Order backlog risk'",
                },
            },
        ],
        # + Type 1
        [
            {
                "labels": {
                    "job": "recommendation-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T03:01:30",
                "endsAt": "2025-06-29T03:04:30",
                "status": "firing",
                "annotations": {
                    "description": "Recommendation latency warning",
                    "summary": "recommendation-service experienced 'Recommendation latency warning'",
                },
            }
        ],
        # + Type 2
        [
            {
                "labels": {
                    "job": "user-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T03:02:00",
                "endsAt": "2025-06-29T03:05:00",
                "status": "firing",
                "annotations": {
                    "description": "Session latency high",
                    "summary": "user-service experienced 'Session latency high'",
                },
            }
        ],
    ],
]

SCENARIO = 0
pattren = [
    *alerts_with_noise[SCENARIO][0],
    *alerts_with_noise[SCENARIO][2],
]

requests.post("http://localhost:8080/alerts", json={"alerts": pattren})
