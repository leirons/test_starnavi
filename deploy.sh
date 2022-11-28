#!/bin/bash

echo "Creating the database credentials..."
kubectl apply -f ./src/kubernetes/postgresql-credentials.yml

echo "Creating the api server credentials..."
kubectl apply -f ./src/kubernetes/pet-secret.yml


echo "Creating the Postgres deployment and service..."
kubectl apply -f ./src/kubernetes/postgresql-deployment.yml
kubectl apply -f ./src/kubernetes/postgresql-service.yml

echo "Creating the FastAPI deployment and service..."
kubectl apply -f ./kubernetes/pet-deployment.yml
kubectl apply -f ./kubernetes/pet-service.yml


echo "Creating the redis deployment and service..."
kubectl apply -f ./kubernetes/redis-deployment.yml
kubectl apply -f ./kubernetes/redis-service.yml


echo "Adding the ingress..."
minikube addons enable ingress
kubectl apply -f ./src/kubernetes/minikube-ingress.yml
