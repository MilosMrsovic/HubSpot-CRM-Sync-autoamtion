import psycopg2
import requests
import json
import time


# 1️⃣ PostgreSQL configuration
PG_HOST = "localhost"
PG_DB = "********"
PG_USER = "********"
PG_PASSWORD = "********"

# 2️⃣ HubSpot configuration
HUBSPOT_TOKEN = "***********************"
HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_COMPANIES_URL = "https://api.hubapi.com/crm/v3/objects/companies"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}


# Helper function for requests with retry handling
def safe_request(method, url, headers=None, json_data=None, max_retries=3, sleep_time=1):
    for i in range(max_retries):
        try:
            if method.lower() == "post":
                resp = requests.post(url, headers=headers, json=json_data)
            elif method.lower() == "patch":
                resp = requests.patch(url, headers=headers, json=json_data)
            elif method.lower() == "put":
                resp = requests.put(url, headers=headers, json=json_data)
            else:
                raise ValueError("Unsupported method")
            
            resp.raise_for_status()
            return resp

        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                print(f"[Retry {i+1}] Request failed: {e}, Response body: {e.response.text}")
            else:
                print(f"[Retry {i+1}] Request failed: {e}")
            time.sleep(sleep_time)

    print(f"Request failed after {max_retries} attempts: {url}")
    return None


# Connect to PostgreSQL
conn = psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD)
cur = conn.cursor()

cur.execute("""
    SELECT id, company_name, domain, contact_name, email, phone, position, status, last_contacted, next_follow_up, source
    FROM leads
""")

leads = cur.fetchall()

dummy_counter = 1

for lead in leads:
    (id, company_name, domain, contact_name, email, phone, position, status,
     last_contacted, next_follow_up, source) = lead
    
    # Extract first and last name
    if contact_name:
        parts = contact_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
    else:
        first_name = ""
        last_name = ""
    
    # Generates dummy email if lead has no email
    if not email:
        email = f"noemail{dummy_counter}@example.com"
        print(f"Using dummy email for {company_name}: {email}")
        dummy_counter += 1
    
    # Create or update company
    company_data = {"properties": {"name": company_name, "domain": domain}}
    company_resp = safe_request("post", HUBSPOT_COMPANIES_URL, headers=HEADERS, json_data=company_data)
    company_id = company_resp.json()["id"] if company_resp else None

    # Contact properties preparation
    contact_props = {
        "firstname": first_name,
        "lastname": last_name,
        "email": email,
        "phone": phone or "",
        "jobtitle": position or "",
        "lead_status": status or "",
        "last_contacted": str(last_contacted) if last_contacted else "",
        "next_follow_up": str(next_follow_up) if next_follow_up else "",
        "source": source or ""
    }
    contact_data = {"properties": contact_props}

    # Check if contact already exists in HubSpot by email
    search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    search_payload = {
        "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}],
        "properties": ["email"]
    }
    search_resp = safe_request("post", search_url, headers=HEADERS, json_data=search_payload)

    if search_resp and search_resp.json().get("results"):
        contact_id = search_resp.json()["results"][0]["id"]
        update_url = f"{HUBSPOT_CONTACTS_URL}/{contact_id}"
        safe_request("patch", update_url, headers=HEADERS, json_data=contact_data)
    else:
        contact_resp = safe_request("post", HUBSPOT_CONTACTS_URL, headers=HEADERS, json_data=contact_data)
        contact_id = contact_resp.json().get("id") if contact_resp else None

    # Associate contact with the company
    if contact_id and company_id:
        assoc_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/company/{company_id}/contact_to_company"
        safe_request("put", assoc_url, headers=HEADERS)

cur.close()
conn.close()

print("All leads have been processed!")
