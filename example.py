from google.cloud import secretmanager
import google_crc32c


# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()

# Build the resource name of the secret version.
name = f"projects/zuu-infra/secrets/my-secret/versions/3"

# Access the secret version.
response = client.access_secret_version(request={"name": name})

print(response)
# Verify payload checksum.
crc32c = google_crc32c.Checksum()
crc32c.update(response.payload.data)
if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
    print("Data corruption detected.")

# Print the secret payload.
#
# WARNING: Do not print the secret in a production environment - this
# snippet is showing how to access the secret material.
payload = response.payload.data.decode("UTF-8")
print(f"Plaintext: {payload}")