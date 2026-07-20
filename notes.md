# Secure Cloud Storage
This project's aim is to provide a secure cloud storage solution that ensures data privacy and integrity. We are building and securing a cloud object storage environment using tools like MinIO, Docker, and OpenSSL. The project will focus on implementing ecrypted storage, access control, and secure data transfer protocols.

- **MinIO**: An open-source object storage server that is compatible with Amazon S3 APIs. It will be used to store and manage data securely.
- **Docker**: A platform for developing, shipping, and running applications in containers. It will be used to deploy the MinIO server and other components of the storage solution.
- **OpenSSL**: OpenSSL is a powerful toolkit used to implement SSL and TLS protocols. In this project, it will be used to encrypt data while it is being transmitted, ensuring secure communication between clients and the storage server.


## Step 1: Setting Up the Environment

1) **Generating the SSL/TLS Certificates**
```bash
mkdir -p minio-env/certs minio-env/data
cd minio-env
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/private.key \
  -out certs/public.crt \
  -subj "/CN=localhost"

```
- The above command generates a self-signed SSL/TLS certificate and a private key. The certificate is valid for 365 days and is stored in the `certs` directory.
- Why we do this: Generating SSL/TLS certificates is crucial for encrypting data in transit. It ensures that any data sent between the client and the server is secure and cannot be intercepted by malicious actors. 

2) **Creating the Docker Compose File**

We do this because:
- Docker Compose allows us to define and manage multi-container applications. By using a `docker-compose.yml` file, we can easily set up and configure the MinIO server along with any other necessary services in a single command. This simplifies deployment and ensures that all components are correctly configured to work together.

- Certificate Mounting: The `docker-compose.yml` file will include volume mounts for the SSL/TLS certificates. This ensures that the MinIO server can access the necessary certificates for secure communication. MinIO automatically looks in ~/.minio/certs for certificates on startup. Mounting our local directory there forces MinIO to boot in HTTPS mode

- Port separation: We explicitly define port 9000 for S3 API traffic and 9001 for the Web Management Console. This allows us to apply different network monitoring or firewall rules to API vs. human traffic later.

3) **Data Generation**
- We will use the `data_generator.py` script to create sample data for testing our secure cloud storage solution. The script generates random user data and saves it in a CSV file format. This data will be used to simulate real-world scenarios and test the functionality of our storage system.

---

## Phase 3: Security Controls (RBAC & Encryption)

For this phase, we will focus on implementing security controls to ensure that our cloud storage solution is secure and compliant with best practices. This includes setting up Role-Based Access Control (RBAC) and enabling Server-Side Encryption (SSE) for our storage buckets.

1. Install MinIO Client (mc) to manage the MinIO server and configure RBAC policies.
```bash
curl https://dl.min.io/client/mc/release/linux-amd64/mc \
  --create-dirs -o $HOME/minio-binaries/mc
chmod +x $HOME/minio-binaries/mc
export PATH=$PATH:$HOME/minio-binaries/

mc alias set localminio https://127.0.0.1:9000 admin4030 SuperSecurePassword123! --insecure
```

2. Create a new bucket and enable server-side encryption (SSE) using a KMS key.
```bash
mc mb localminio/hr-data --insecure
mc mb localminio/finance-data --insecure

mc admin user add localminio HR_User HRPwd123! --insecure
mc admin user add localminio Finance_User FinPwd123! --insecure
```
- We use the `mc` command-line tool to create buckets and manage users. The `--insecure` flag is used because we are using self-signed certificates for our MinIO server.
- A bucket is a logical container for storing objects (files) in MinIO. By creating separate buckets for different departments (HR and Finance), we can enforce access control policies and ensure that only authorized users can access the data.
- KMS (Key Management Service) is used to manage encryption keys for server-side encryption. By enabling SSE with a KMS key, we ensure that the data stored in the buckets is encrypted at rest, providing an additional layer of security.

3. Set up RBAC policies to restrict access to the buckets based on user roles.
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:*"],
    "Resource": ["arn:aws:s3:::hr-data/*", "arn:aws:s3:::hr-data"]
  }]
}
```
This JSON policy allows the HR_User to perform any action on the `hr-data` bucket and its contents. Similar policies can be created for the Finance_User to restrict access to the `finance-data` bucket. To apply these policies, we will use the `mc` command-line tool to set the policies for each user
```bash
mc admin policy create localminio hr-access hr-policy.json --insecure
mc admin policy attach localminio hr-access --user HR_User --insecure

mc admin policy create localminio finance-access finance-policy.json --insecure
mc admin policy attach localminio finance-access --user Finance_User --insecure
```

4. Enabling Server-Side Encryption (SSE) for the buckets ensures that all data stored in the buckets is encrypted at rest. This provides an additional layer of security, protecting sensitive information from unauthorized access. By using a KMS key for encryption, we can manage and rotate encryption keys as needed, further enhancing the security of our cloud storage solution.

- Stop running containers and remove the volumes to clear the data and certificates:
```bash
docker-compose down 
```

- Add the KMS key to the docker-compose.yml file and restart the containers:
```yaml
environment:
      - MINIO_ROOT_USER=admin4030
      - MINIO_ROOT_PASSWORD=SuperSecurePassword123!
      - MINIO_KMS_SECRET_KEY=my-minio-key:K7MDENG/bPxRfiCYzU+z7aQxYx1EXAMPLEKEY=
```

- Restart the containers:
```bash
docker-compose up -d
```

- Enforce automatic SSE on the buckets
```bash
mc encrypt set sse-s3 localminio/hr-data --insecure
mc encrypt set sse-s3 localminio/finance-data --insecure
```

- Verify that the buckets are encrypted:
```bash
mc encrypt info localminio/hr-data --insecure
mc encrypt info localminio/finance-data --insecure
```
