import random
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import datetime as dt
import csv 

# === CONFIG ===
NUM_DAYS = 500
MIN_SCENARIOS_PER_DAY = 1
MAX_SCENARIOS_PER_DAY = 6
SCENARIO_GAP_RANGE_MINUTES = (20, 30)
ALERT_GAP_RANGE_SECONDS = (30, 50)
ALERT_DURATION_MINUTES = 3
OUTPUT_DIR = "./test_data/data/"
TYPE1_NOISE_DIR = "./test_data/type1_noise"
NOISE_DAY_PERCENT = 0.4  # Only 40% of days can have any noise

# === FIXED SCENARIOS ===
SCENARIOS = [
    ["2.2", "3.2", "4.1"],  # 7.1, 1.2
    ["1.1", "4.2", "5.1"],
    ["2.1", "3.2", "4.1", "5.1"],
    ["1.2", "4.1", "6.1", "6.2"],
    ["2.1", "3.1", "4.2", "7.2"],
    ["1.1", "4.1", "5.1", "4.2", "7.1"],
    ["2.2", "3.2", "4.1", "4.2", "7.1", "7.2"],
]

# === ALERT METADATA ===
alert_metadata = {
    "1.1": {"service": "user-service", "desc": "Auth failure spike"},
    "1.2": {"service": "user-service", "desc": "Session latency high"},
    "2.1": {"service": "product-catalog-service", "desc": "Metadata sync delay"},
    "2.2": {"service": "product-catalog-service", "desc": "Read error surge"},
    "3.1": {"service": "inventory-service", "desc": "Stock consistency warning"},
    "3.2": {"service": "inventory-service", "desc": "Update failure increase"},
    "4.1": {"service": "order-service", "desc": "Order backlog risk"},
    "4.2": {"service": "order-service", "desc": "Validation error surge"},
    "5.1": {"service": "payment-service", "desc": "Gateway timeout spike"},
    "5.2": {"service": "payment-service", "desc": "High retry rate"},
    "6.1": {"service": "shipping-service", "desc": "Shipping delay warning"},
    "6.2": {"service": "shipping-service", "desc": "Carrier API failure surge"},
    "7.1": {
        "service": "recommendation-service",
        "desc": "Recommendation latency warning",
    },
    "7.2": {"service": "recommendation-service", "desc": "Recommendation model errors"},
}

# === SERVICE GRAPH ===
service_graph = {
    "1": {"parents": [], "children": ["4", "5", "7"]},
    "2": {"parents": [], "children": ["3", "7"]},
    "3": {"parents": ["2"], "children": ["4", "6", "7"]},
    "4": {"parents": ["1", "3"], "children": ["5", "6", "7"]},
    "5": {"parents": ["4", "1"], "children": []},
    "6": {"parents": ["4", "3"], "children": []},
    "7": {"parents": ["1", "2", "3", "4"], "children": []},
}


def create_alert(alert_id, start_time):
    meta = alert_metadata[alert_id]
    service_id = alert_id.split(".")[1]
    end_time = start_time + timedelta(minutes=ALERT_DURATION_MINUTES)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return {
        "labels": {
            "job": meta["service"],
            "instance": service_id,
            "severity": "critical",
        },
        "startsAt": start_time.strftime(fmt),
        "endsAt": end_time.strftime(fmt),
        "status": "firing",
        "annotations": {
            "description": meta["desc"],
            "summary": f"{meta['service']} experienced '{meta['desc']}'",
        },
    }


def generate_day_alerts(day_index, base_date):
    alerts = []
    involved_services = set()
    scenario_count = random.randint(MIN_SCENARIOS_PER_DAY, MAX_SCENARIOS_PER_DAY)
    scenario_pool = random.sample(SCENARIOS, k=scenario_count)
    current_time = base_date.replace(hour=0, minute=0, second=0) + timedelta(
        minutes=random.randint(0, 60)
    )

    for scenario in scenario_pool:
        for alert_id in scenario:
            alert = create_alert(alert_id, current_time)
            alerts.append(alert)
            involved_services.add(alert_id.split(".")[0])
            current_time += timedelta(seconds=random.randint(*ALERT_GAP_RANGE_SECONDS))
        current_time += timedelta(minutes=random.randint(*SCENARIO_GAP_RANGE_MINUTES))

    return alerts, involved_services


def choose_linked_alerts(existing_services, count):
    valid = []
    for aid, meta in alert_metadata.items():
        sid = aid.split(".")[0]
        if sid in existing_services:
            continue
        if any(p in existing_services for p in service_graph[sid]["parents"]):
            valid.append(aid)
    return random.choices(valid, k=count) if valid else []


# === MAIN ===
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    Path(TYPE1_NOISE_DIR).mkdir(exist_ok=True)
    base_date = datetime.now(dt.UTC) - timedelta(days=NUM_DAYS)

    alerts_by_day = {}
    involved_services_by_day = {}
    all_alerts_flat = []
    type1_noise_by_day_pattern = defaultdict(lambda: defaultdict(list))

    # Days allowed to have any noise
    allowed_noise_days = set(
        random.sample(range(NUM_DAYS), int(NUM_DAYS * NOISE_DAY_PERCENT))
    )
    used_noise_days = set()

    # === Step 1a: Force include all scenarios once
    for day, scenario in enumerate(SCENARIOS):
        day_time = base_date + timedelta(days=day)
        alerts = []
        involved_services = set()
        current_time = day_time.replace(hour=0, minute=0, second=0) + timedelta(
            minutes=random.randint(0, 60)
        )
        for alert_id in scenario:
            alert = create_alert(alert_id, current_time)
            alerts.append(alert)
            involved_services.add(alert_id.split(".")[0])
            current_time += timedelta(seconds=random.randint(*ALERT_GAP_RANGE_SECONDS))
        alerts_by_day[day] = alerts
        involved_services_by_day[day] = involved_services
        all_alerts_flat.extend(alerts)

    # === Step 1b: Generate remaining days
    for day in range(len(SCENARIOS), NUM_DAYS):
        day_time = base_date + timedelta(days=day)
        alerts, services = generate_day_alerts(day, day_time)
        alerts_by_day[day] = alerts
        involved_services_by_day[day] = services
        all_alerts_flat.extend(alerts)

    # === Step 2: Determine total noise
    total_scenario_alerts = len(all_alerts_flat)
    total_noise_alerts = int(total_scenario_alerts * 0.2)
    half = total_noise_alerts // 2

    # === Step 3: Type 1 noise (correlated)
    correlated_inserted = 0
    attempts = 0
    while correlated_inserted < half and attempts < half * 10:
        unused = allowed_noise_days - used_noise_days
        if not unused:
            break
        day = random.choice(list(unused))
        service_set = involved_services_by_day[day]
        new_alert_ids = choose_linked_alerts(service_set, 1)
        if not new_alert_ids:
            attempts += 1
            continue
        ts = datetime.fromisoformat(alerts_by_day[day][-1]["startsAt"]) + timedelta(
            minutes=random.randint(1, 5)
        )
        for aid in new_alert_ids:
            alert = create_alert(aid, ts)
            alerts_by_day[day].append(alert)
            for pattern_idx, pattern in enumerate(SCENARIOS):
                pattern_services = {pid.split(".")[0] for pid in pattern}
                if any(p in service_set for p in pattern_services):
                    day_key = f"day_{day + 1:04d}"
                    pattern_key = f"pattern_{pattern_idx}"
                    type1_noise_by_day_pattern[day_key][pattern_key].append(alert)
                    break
            correlated_inserted += 1
        used_noise_days.add(day)
        attempts += 1

    # === Step 4: Type 2 noise (independent scenarios)
    independent_inserted = 0
    fake_scenarios = [
        ["5.2", "6.1"],
        ["1.2", "5.2", "6.2"],
        ["2.1", "6.1"],
        ["3.1", "5.2", "7.1"],
    ]
    while independent_inserted < (total_noise_alerts - half):
        unused = allowed_noise_days - used_noise_days
        if not unused:
            break
        day = random.choice(list(unused))
        scenario = random.choice(fake_scenarios)
        ts = datetime.now(dt.UTC).replace(hour=3, minute=0, second=0) + timedelta(
            days=day
        )
        for aid in scenario:
            alert = create_alert(aid, ts)
            alerts_by_day[day].append(alert)
            ts += timedelta(seconds=random.randint(30, 50))
            independent_inserted += 1
        used_noise_days.add(day)

    # === Step 5: Save alerts by day
    for day, alerts in alerts_by_day.items():
        filename = os.path.join(OUTPUT_DIR, f"alerts_day_{day + 1:04d}.csv")
        with open(filename, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(["job", "instance", "severity", "startsAt", "endsAt", "status", "description", "summary"])
            for alert in alerts:
                writer.writerow([
                    alert["labels"]["job"],
                    alert["labels"]["instance"],
                    alert["labels"]["severity"],
                    alert["startsAt"],
                    alert["endsAt"],
                    alert["status"],
                    alert["annotations"]["description"],
                    alert["annotations"]["summary"]
                ])


    # === Step 6: Save Type 1 noise by day & pattern
    for day_key, patterns in type1_noise_by_day_pattern.items():
        day_dir = Path(TYPE1_NOISE_DIR) / day_key
        day_dir.mkdir(parents=True, exist_ok=True)
        for pattern_key, alerts in patterns.items():
            with open(day_dir / f"{pattern_key}.csv", "w", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["job", "instance", "severity", "startsAt", "endsAt", "status", "description", "summary"])
                for alert in alerts:
                    writer.writerow([
                        alert["labels"]["job"],
                        alert["labels"]["instance"],
                        alert["labels"]["severity"],
                        alert["startsAt"],
                        alert["endsAt"],
                        alert["status"],
                        alert["annotations"]["description"],
                        alert["annotations"]["summary"]
                    ])


    # === Summary
    print(f"Generated {NUM_DAYS} days.")
    print(f"Scenario alerts: {len(all_alerts_flat)}")
    print(f"Type 1 noise alerts: {correlated_inserted}")
    print(f"Type 2 noise alerts: {independent_inserted}")
    print(f"Output in '{OUTPUT_DIR}/' and '{TYPE1_NOISE_DIR}/'")


if __name__ == "__main__":
    main()
