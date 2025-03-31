from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import csv
import os
from datetime import datetime
from user_agents import parse as parse_ua

app = FastAPI()

# Enable CORS (cross-origin for Webflow/PowerBI etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IPINFO_TOKEN = "8e738acc736b52"
CSV_FILE = "visitors.csv"

# Create CSV file with headers if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "ip", "company", "city", "country", "url", "device"])

# Get company/org data from IP using ipinfo.io
def lookup_company(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}")
        data = res.json()
        org = data.get("org", "")
        city = data.get("city", "")
        country = data.get("country", "")
        return org, city, country
    except Exception as e:
        print("IP Lookup failed:", e)
        return "", "", ""

# API to track a visit
@app.post("/track")
async def track(request: Request):
    client_ip = request.client.host
    body = await request.json()
    url = body.get("url", "")
    user_agent_str = body.get("userAgent", "")
    user_agent = parse_ua(user_agent_str)
    device = f"{user_agent.device.family} - {user_agent.os.family} - {user_agent.browser.family}"

    org, city, country = lookup_company(client_ip)
    timestamp = datetime.utcnow().isoformat()

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, client_ip, org, city, country, url, device])

    return {"status": "ok"}

# API to return visitor data as CSV
@app.get("/data")
def get_csv():
    if not os.path.exists(CSV_FILE):
        return {"error": "No visitor data available yet."}
    return FileResponse(CSV_FILE, media_type='text/csv', filename='visitors.csv')

# Health check
@app.get("/")
def root():
    return {"message": "Tracking backend is running."}

# Local run support (optional but helpful)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)



