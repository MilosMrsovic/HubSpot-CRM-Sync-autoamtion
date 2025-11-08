This script connects my PostgreSQL database with HubSpot and automatically sends all leads into HubSpot CRM. Every lead from the database is processed one by one. For each lead, the script checks if the contact already exists in HubSpot by searching based on email. If the contact exists, it updates the properties. If the contact does not exist, it creates a new one.

The script also creates a company in HubSpot and links the contact to the correct company. If the lead does not have an email, the script generates a temporary placeholder email so HubSpot can accept the contact. I also added retry logic for HubSpot API requests, so if something fails during the request, the script waits and tries again.

This project allows me to keep HubSpot always up to date with my leads without manual work. Everything is automated and synced directly from PostgreSQL into HubSpot.
