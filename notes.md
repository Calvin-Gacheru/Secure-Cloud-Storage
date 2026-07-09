# Secure Cloud Storage
This project's aim is to provide a secure cloud storage solution that ensures data privacy and integrity. We are building and securing a cloud object storage environment using tools like MinIO, Docker, and OpenSSL. The project will focus on implementing ecrypted storage, access control, and secure data transfer protocols.

- **MinIO**: An open-source object storage server that is compatible with Amazon S3 APIs. It will be used to store and manage data securely.
- **Docker**: A platform for developing, shipping, and running applications in containers. It will be used to deploy the MinIO server and other components of the storage solution.
- **OpenSSL**: A robust toolkit for implementing SSL and TLS protocols. It will be used to encrypt data in transit and ensure secure communication between clients and the storage server.

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

