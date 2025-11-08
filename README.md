# HubSpot CRM Sync Automation
## Overview

This script connects my PostgreSQL database with HubSpot and automatically sends all leads into HubSpot CRM. Each lead is processed individually. The script searches HubSpot by email to check if the contact already exists. If a contact exists, the data is updated. If not, a new contact is created.

## Company handling

For every lead, the script also creates a company in HubSpot and connects the contact with the correct company. If a lead does not have an email, the script generates a temporary placeholder email so that HubSpot can accept the contact.

## Error and retry logic

The script has retry logic for HubSpot API requests. If something fails because of a temporary network or HubSpot-side issue, the script automatically retries the request before continuing.

## Goal

The idea behind this project is to remove manual input and keep HubSpot always synced with my leads. Once the script runs, everything is automated and fully synchronized from PostgreSQL into HubSpot without needing any manual updates.
