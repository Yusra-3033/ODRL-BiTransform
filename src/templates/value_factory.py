# value_factory.py
# ----------------------------------------------------------------------------
# Generator for semantically appropriate rightOperand values based on operand type.
# This script enriches constraints in synthetic ODRL policies.
# ----------------------------------------------------------------------------

import random
from datetime import datetime, timedelta
import uuid

def generate_right_operand(operand):
    """Generate semantically appropriate right operand values."""
    fallback_uri = f"http://example.com/value/{operand}/{uuid.uuid4().hex[:8]}"

    # Spatial and location operands
    if operand in ["absoluteSpatialPosition"]:
        wikidata_entities = ["Q30", "Q142", "Q183", "Q145", "Q55", "Q38", "Q96", "Q668", "Q258", "Q205", "Q262", "Q927", "Q449", "Q358"]
        return f"http://www.wikidata.org/entity/{random.choice(wikidata_entities)}"

    elif operand == "relativeSpatialPosition":
        return random.choice(["left", "right", "above", "below", "inside", "outside"])

    elif operand == "virtualLocation":
        return f"http://example.com/virtual/location/{uuid.uuid4().hex[:8]}"

    elif operand == "recipient":
        recipient_type = random.choice(['user', 'org', 'group'])
        return f"http://example.com/recipient/{recipient_type}/{uuid.uuid4().hex[:8]}"

    elif operand in ["absolutePosition", "relativePosition"]:
        return f"http://example.com/value/{operand}/{uuid.uuid4().hex[:8]}"

    elif operand == "relativeTemporalPosition":
        return f"http://example.com/value/relativeTemporalPosition/{uuid.uuid4().hex[:8]}"

    # Numeric operands
    elif operand == "percentage":
        return random.randint(1, 100)

    elif operand in ["count", "unitOfCount"]:
        return random.randint(1, 1000)

    elif operand == "payAmount":
        return round(random.uniform(5.0, 500.0), 2)

    elif operand == "elapsedTime":
        return random.randint(10, 3600)  # seconds

    # Temporal operands
    elif operand in ["dateTime", "absoluteTemporalPosition"]:
        base_date = datetime(2025, 5, 23, 12, 32, 20)
        random_offset = timedelta(days=random.randint(-365, 365))
        return (base_date + random_offset).strftime("%Y-%m-%dT%H:%M:%SZ")

    elif operand == "timeInterval":
        start_date = datetime(2025, 5, 23, 12, 32, 20)
        end_date = start_date + timedelta(days=random.randint(1, 30))
        return f"{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    elif operand == "delayPeriod":
        duration_units = [
            f"P{random.randint(1, 30)}D",
            f"P{random.randint(1, 12)}M",
            f"P{random.randint(1, 5)}Y",
            f"PT{random.randint(1, 24)}H",
            f"PT{random.randint(1, 60)}M"
        ]
        return random.choice(duration_units)

    # Format and media operands
    elif operand == "fileFormat":
        formats = [
            "application/pdf", "text/html", "text/plain", "text/csv",
            "image/jpeg", "image/png", "image/gif", "image/bmp",
            "video/mp4", "video/avi", "video/mkv", "video/webm",
            "audio/mpeg", "audio/wav", "audio/flac", "audio/ogg"
        ]
        return random.choice(formats)

    elif operand == "resolution":
        return random.choice(["480p", "720p", "1080p", "2K", "4K", "8K"])

    elif operand in ["deliveryChannel", "media", "language", "purpose", "systemDevice"]:
        options = {
            "deliveryChannel": ["mobile", "web", "print", "broadcast", "email", "sms"],
            "media": ["digital", "physical", "online", "offline", "streaming", "download"],
            "language": ["en", "de", "fr", "es", "zh", "ja", "ar", "hi", "pt", "ru"],
            "purpose": ["research", "commercial", "educational", "personal", "non-commercial"],
            "systemDevice": ["mobile", "desktop", "server", "iot", "sensor", "tablet"]
        }
        return random.choice(options.get(operand, ["default"]))

    # Business and product operands
    elif operand == "product":
        return f"http://example.com/product/{uuid.uuid4().hex[:8]}"

    elif operand == "industry":
        industries = ['music', 'film', 'software', 'literature', 'data', 'gaming', 'education', 'healthcare']
        return f"http://example.com/industry/{random.choice(industries)}"

    # Technical operands
    elif operand == "metering":
        return random.choice(["enabled", "disabled"])

    elif operand == "version":
        major = random.randint(1, 5)
        minor = random.randint(0, 9)
        patch = random.randint(0, 9)
        return f"{major}.{minor}.{patch}"

    elif operand == "event":
        events = ["odrl:policyUsage", "odrl:offer", "odrl:agreement", "odrl:request", "odrl:permission"]
        return random.choice(events)

    # Spatial descriptors
    elif operand == "spatial":
        return f"http://example.com/value/spatial/{uuid.uuid4().hex[:8]}"

    # Fallback for unknown operands
    else:
        if "Amount" in operand or "Price" in operand:
            return round(random.uniform(1.0, 1000.0), 2)
        elif "Count" in operand or "Number" in operand:
            return random.randint(1, 100)
        elif "Time" in operand or "Date" in operand:
            return (datetime.utcnow() + timedelta(days=random.randint(-30, 30))).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif "Position" in operand or "Location" in operand:
            return f"http://example.com/value/{operand.lower()}/{uuid.uuid4().hex[:8]}"
        else:
            return fallback_uri
