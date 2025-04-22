
# 🚀 Deploy a Local Docker Container to AWS ECS (Fargate)

This guide walks you through deploying your local Docker container to AWS ECS using Fargate and storing your image in Amazon ECR.

---

## 🔧 Prerequisites

- Docker installed and running
- AWS CLI installed and configured with `aws configure`
- IAM user/role permissions for ECR, ECS, VPC, and EC2 Networking

---

## ✅ Step 1: Push Docker Image to Amazon ECR

### 1.1 Authenticate Docker to ECR
```bash
aws ecr get-login-password --region <your-region> \
  | docker login --username AWS \
  --password-stdin <aws_account_id>.dkr.ecr.<your-region>.amazonaws.com
```

### 1.2 Create an ECR Repository
```bash
aws ecr create-repository --repository-name my-app-repo
```

### 1.3 Tag Your Local Image
```bash
docker tag my-app-image:latest <aws_account_id>.dkr.ecr.<your-region>.amazonaws.com/my-app-repo:latest
```

### 1.4 Push the Image to ECR
```bash
docker push <aws_account_id>.dkr.ecr.<your-region>.amazonaws.com/my-app-repo:latest
```

---

## ✅ Step 2: Create an ECS Cluster

### Using AWS CLI:
```bash
aws ecs create-cluster --cluster-name my-cluster
```

### Or via Console:
- Navigate to [ECS Console](https://console.aws.amazon.com/ecs/)
- Click **Create Cluster**
- Choose **Networking only (Fargate)** → continue with setup

---

## ✅ Step 3: Register a Task Definition

### 3.1 Create a Task Definition JSON File (e.g. `task-definition.json`)
```json
{
  "family": "my-task-def",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "my-app",
      "image": "<aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-app-repo:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true
    }
  ]
}
```

### 3.2 Register the Task
```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json
```

---

## ✅ Step 4: Run the Service on ECS (Fargate)

Replace `subnet-xxxx` and `sg-xxxx` with valid values from your VPC.

```bash
aws ecs create-service \
  --cluster my-cluster \
  --service-name my-app-service \
  --task-definition my-task-def \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxx],securityGroups=[sg-xxxx],assignPublicIp=ENABLED}"
```

✅ Ensure that your security group (`sg-xxxx`) allows **inbound traffic on the app's port** (e.g., 80).

---

## 🌐 (Optional) Configure Load Balancer

1. Create an **Application Load Balancer (ALB)**.
2. Create a **Target Group** (protocol TCP or HTTP depending on your app).
3. Point the ECS Service to this Target Group.
4. Set up DNS using Route 53 or an external DNS provider.

---

## 🧪 Verifying Deployment

- Go to **ECS Console > Clusters > Tasks**.
- Look at the public IP (if `assignPublicIp=ENABLED`) or use your ALB.
- You should see your app running!

---

## 📌 Additional Tips

- You can scale your service:
  ```bash
  aws ecs update-service --cluster my-cluster --service my-app-service --desired-count 2
  ```
- Logs are sent to **CloudWatch Logs** by default.
- Use `aws logs` or the CloudWatch Console to view logs.
- Consider using [AWS Copilot CLI](https://docs.aws.amazon.com/copilot/latest/userguide/what-is-copilot.html) for simplified workflows.

---

## ✅ Done!

Your Docker container is now live on AWS ECS with Fargate 🚀
