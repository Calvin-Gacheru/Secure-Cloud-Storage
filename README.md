# Secure Cloud Storage

Secure Cloud Storage is a small but realistic security lab for building and validating a protected MinIO object-storage environment. The project focuses on three core controls: encrypted transport with TLS, role-based access control for departmental data, and server-side encryption for data at rest. A synthetic dataset of 100,000 corporate document records is generated in Python and used to simulate storage and access patterns.

## What This Project Demonstrates

- Encrypted object storage with MinIO running in Docker.
- Self-signed TLS certificates for HTTPS access to the MinIO API and console.
- Department-scoped buckets for HR and Finance data.
- MinIO user and policy management through the `mc` client.
- Server-side encryption configured with a KMS secret key.
- Security validation through access-denied checks and audit trace review.

## Architecture Overview

The environment is intentionally simple so the security controls are easy to inspect:

- `data_generator.py` creates the synthetic metadata dataset.
- `minio-env/docker-compose.yml` starts a single MinIO container.
- `minio-env/certs/` stores the TLS certificate and private key.
- `minio-env/data/` persists bucket objects on the host.
- `minio-binaries/mc` is used to create buckets, users, policies, and encryption settings.
- `hr-policy.json` and `finance-policy.json` define bucket-level access controls.

## Repository Structure

- `data_generator.py` - Generates the 100,000-row CSV dataset.
- `document_metadata.csv` - Output dataset produced by the generator.
- `main.py` - Minimal entry point for the Python project.
- `hr-policy.json` - IAM policy for HR bucket access.
- `finance-policy.json` - IAM policy for Finance bucket access.
- `minio-env/docker-compose.yml` - MinIO container definition with TLS and KMS settings.
- `minio-binaries/mc` - MinIO client binary used for administration.
- `documentation/documentation.md` - Detailed project write-up and implementation notes.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenSSL
- MinIO Client (`mc`)

If you plan to regenerate the dataset, ensure the Python dependency used by `data_generator.py` is installed:

```bash
pip install faker
```

## Quick Start

### 1. Generate TLS certificates

From the project root:

```bash
mkdir -p minio-env/certs minio-env/data
cd minio-env
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/private.key \
  -out certs/public.crt \
  -subj "/CN=localhost"
```

This creates a self-signed certificate for HTTPS access to the MinIO API and console.

### 2. Start MinIO with Docker Compose

The MinIO service is defined in `minio-env/docker-compose.yml`.

```bash
cd minio-env
docker compose up -d
```

If your system only has the legacy binary, use `docker-compose up -d` instead.

### 3. Verify the service is running

```bash
docker ps
docker logs minio-secure
```

MinIO should be available at:

- https://127.0.0.1:9000 for the S3-compatible API
- https://127.0.0.1:9001 for the web console

## Data Generation

The dataset generator creates 100,000 synthetic document metadata records with the following fields:

- `Document_ID`
- `Author`
- `Department`
- `Sensitivity_Level`
- `File_Size_MB`
- `Upload_Date`

Run the generator from the project root:

```bash
python data_generator.py
```

The resulting CSV is written to `document_metadata.csv`.

## Security Configuration

### MinIO Client Setup

```bash
curl https://dl.min.io/client/mc/release/linux-amd64/mc \
  --create-dirs -o $HOME/minio-binaries/mc
chmod +x $HOME/minio-binaries/mc
export PATH=$PATH:$HOME/minio-binaries/

./mc alias set localminio https://127.0.0.1:9000 admin4030 SuperSecurePassword123! --insecure
```

### Create Department Buckets and Users

```bash
./mc mb localminio/hr-data --insecure
./mc mb localminio/finance-data --insecure

./mc admin user add localminio HR_User HRPwd123! --insecure
./mc admin user add localminio Finance_User FinPwd123! --insecure
```

### Apply RBAC Policies

The HR policy limits access to the HR bucket while still allowing the console to list buckets cleanly:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListAllMyBuckets"],
      "Resource": ["arn:aws:s3:::*"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::hr-data/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::hr-data"]
    }
  ]
}
```

Attach the policy with `mc`:

```bash
./minio-binaries/mc admin policy create localminio hr-access hr-policy.json --insecure
./minio-binaries/mc admin policy attach localminio hr-access --user HR_User --insecure
```

Repeat the same approach for the Finance user with `finance-policy.json`.

### Enable Server-Side Encryption

The Docker Compose file includes the KMS secret key needed for SSE-S3:

```yaml
environment:
  - MINIO_ROOT_USER=admin4030
  - MINIO_ROOT_PASSWORD=SuperSecurePassword123!
  - MINIO_KMS_SECRET_KEY=my-minio-key:XTp6urxoHlNxgBq5trWkKsV1k1HXZro358VQx4Mw97I=
```

After restarting the container, enable auto encryption on each bucket:

```bash
docker compose down
docker compose up -d
./minio-binaries/mc encrypt set sse-s3 localminio/hr-data --insecure
./minio-binaries/mc encrypt set sse-s3 localminio/finance-data --insecure
```

Confirm the encryption state with:

```bash
./minio-binaries/mc encrypt info localminio/hr-data --insecure
./minio-binaries/mc encrypt info localminio/finance-data --insecure
```

## Validation and Security Tests

The documentation demonstrates six checks that validate the environment:

1. Authorized upload to the HR bucket.
2. Unauthorized access blocked between buckets.
3. Invalid access denied by the server.
4. HTTPS enforced; HTTP requests are rejected.
5. SSE-S3 confirmed on both buckets.
6. Audit trace captures the 403 Forbidden event.

### Sample Verification Commands

```bash
./minio-binaries/mc alias set hruser https://127.0.0.1:9000 HR_User HRPwd123! --insecure
./minio-binaries/mc cp document_metadata.csv hruser/hr-data/ --insecure
./minio-binaries/mc ls hruser/finance-data/ --insecure
curl http://127.0.0.1:9000
./minio-binaries/mc admin trace localminio --insecure
```

## Screenshots

The following screenshots document the most important stages of the project.

### Dataset Generation

![Synthetic dataset loaded into a viewer showing 100,000 rows and the expected schema](documentation/image.png)

### Bucket and User Provisioning

![MinIO buckets and users created successfully with the mc client](documentation/image-2.png)

### Server-Side Encryption

![SSE-S3 enabled for the department buckets](documentation/image-5.png)

### Access Control Enforcement

![Unauthorized bucket access denied for a restricted user](documentation/image-8.png)

### HTTPS Enforcement

![Plain HTTP request rejected because the MinIO server requires HTTPS](documentation/image-10.png)

### Audit Trace Output

![403 Forbidden event captured in MinIO audit trace output](documentation/image-12.png)

## Known Limitations

- The environment is single-node and is intended for learning and validation rather than production use.
- Audit tracing is demonstrated interactively and should be forwarded to persistent logging in a real deployment.
- Self-signed certificates are useful for local testing but should be replaced with trusted CA-issued certificates in enterprise environments.

## Future Improvements

- Deploy MinIO in distributed mode for higher availability.
- Replace local users with centralized identity through OIDC or Active Directory.
- Forward traces to a log platform for persistent audit retention.
- Use enterprise-trusted certificates instead of self-signed certificates.

## Conclusion

Secure Cloud Storage shows how to combine MinIO, Docker, OpenSSL, and Python to build a secure object-storage lab with meaningful security controls. The project is useful as a reference implementation for encryption, access control, and security testing patterns in a local environment.
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": ["arn:aws:s3:::hr-data/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::hr-data"]
    }
  ]
}
```