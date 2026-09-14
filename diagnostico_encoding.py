import requests

CKAN_API = "https://datosabiertos.bogota.gov.co/api/3/action/resource_show"

RESOURCE_ID = "f93bb5af-c4c6-4301-b602-4cbed283134a"

response = requests.get(
    CKAN_API,
    params={"id": RESOURCE_ID},
    timeout=60,
)

response.raise_for_status()

payload = response.json()

url = payload["result"]["url"]

print("URL DEL RECURSO:")
print(url)

file_response = requests.get(url, timeout=120)
file_response.raise_for_status()

content = file_response.content

print("\nTAMAÑO:")
print(len(content), "bytes")

print("\nPRIMEROS 500 BYTES:")
print(content[:500])

print("\nPRIMERA PARTE DECODIFICADA COMO UTF-8:")
try:
    print(content[:3000].decode("utf-8"))
except UnicodeDecodeError as e:
    print("ERROR UTF-8:", e)

print("\nPRIMERA PARTE DECODIFICADA COMO CP1252:")
try:
    print(content[:3000].decode("cp1252"))
except UnicodeDecodeError as e:
    print("ERROR CP1252:", e)

print("\nPRIMERA PARTE DECODIFICADA COMO LATIN-1:")
try:
    print(content[:3000].decode("latin-1"))
except UnicodeDecodeError as e:
    print("ERROR LATIN-1:", e)