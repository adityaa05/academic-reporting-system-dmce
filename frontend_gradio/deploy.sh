#!/bin/bash

# Deploy Gradio Frontend to Google Cloud Run
# Usage: ./deploy.sh [PROJECT_ID]

set -e

PROJECT_ID=${1:-$(gcloud config get-value project)}
REGION="asia-south1"
SERVICE_NAME="gradio-frontend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "Deploying Gradio Frontend to Google Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo ""

# Build the container
echo "Building container image..."
gcloud builds submit --tag $IMAGE_NAME --project $PROJECT_ID

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 7860 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --project $PROJECT_ID

echo ""
echo "Deployment complete!"
echo "Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID)
echo "Your Gradio frontend is now available at: $SERVICE_URL"
