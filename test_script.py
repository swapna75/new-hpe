import aiohttp
import asyncio
import sys
import datetime

alerts = [
    {
        "labels": {
            "job": "database",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 2).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 30, 53).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "temp description of database",
            "summary": "DatabaseDown",
        },
    },
    {
        "labels": {
            "job": "knn",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 10).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 30, 55).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "temp description of knn",
            "summary": "RPCFailure",
        },
    },
    {
        "labels": {
            "job": "backend",
            "severity": "critical",
        },
        "startsAt": datetime.datetime(2025, 3, 1, 12, 30, 20).isoformat() + "Z",
        "endsAt": datetime.datetime(2025, 3, 1, 12, 31, 10).isoformat() + "Z",
        "status": "firing",
        "annotations": {
            "description": "temp description of backend",
            "summary": "HttpFailure",
        },
    },
]


async def post_data():
    patterns = [
        alerts[:1],
        alerts[:2],
        alerts[:3],
        alerts[1:2],
        alerts[1:3],
        alerts[2:3],
    ]
    curr_pattern = int(sys.argv[2])
    port = sys.argv[1]
    url = f"http://localhost:{port}/"
    payload = {"alerts": patterns[curr_pattern]}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            print("Status:", response.status)


async def test():
    await post_data()


if __name__ == "__main__":
    asyncio.run(test())
