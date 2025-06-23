import requests

pattren = [
    {
        "labels": {
            "job": "inventory-service",
            "instance": "2",
            "severity": "critical",
        },
        "startsAt": "2027-01-01T12:32:00",
        "endsAt": "2027-01-01T12:33:00",
        "status": "firing",
        "annotations": {
            "description": "Update failure increase",
            "summary": "'database instance 1 down'",
        },
    },
    {
        "labels": {
            "job": "shipping-service",
            "instance": "2",
            "severity": "critical",
        },
        "startsAt": "2027-01-01T12:34:00",
        "endsAt": "2027-01-01T12:35:00",
        "status": "firing",
        "annotations": {
            "description": "Carrier API failure surge",
            "summary": "'database instance 1 down'",
        },
    },
    {
        "labels": {
            "job": "inventory-service",
            "instance": "1",
            "severity": "critical",
        },
        "startsAt": "2027-01-01T12:36:00",
        "endsAt": "2027-01-01T12:37:00",
        "status": "firing",
        "annotations": {
            "description": "Stock consistency warning",
            "summary": "'database instance 1 down'",
        },
    },
    {
        "labels": {
            "job": "recommendation-service",
            "instance": "2",
            "severity": "critical",
        },
        "startsAt": "2027-01-01T12:38:00",
        "endsAt": "2027-01-01T12:39:00",
        "status": "firing",
        "annotations": {
            "description": "Recommendation model errors",
            "summary": "'database instance 1 down'",
        },
    },
    {
        "labels": {
            "job": "recommendation-service",
            "instance": "1",
            "severity": "critical",
        },
        "startsAt": "2027-01-01T12:38:00",
        "endsAt": "2027-01-01T12:39:00",
        "status": "firing",
        "annotations": {
            "description": "Recommendation latency warning",
            "summary": "'database instance 1 down'",
        },
    },
]

requests.post("http://localhost:8080/alerts", json={"alerts": pattren})
