#!/bin/bash

# Quick Start Script for Module 14
# This script helps you quickly test the BREAD functionality

echo "======================================="
echo "Module 14 - BREAD Functionality Setup"
echo "======================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down 2>/dev/null
echo ""

# Start the application
echo "🚀 Starting the application with Docker Compose..."
docker-compose up -d --build

# Wait for application to be ready
echo ""
echo "⏳ Waiting for application to be ready..."
sleep 10

# Check if application is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Application is running!"
else
    echo "❌ Application failed to start. Check Docker logs:"
    echo "   docker-compose logs"
    exit 1
fi

echo ""
echo "======================================="
echo "Application is ready! 🎉"
echo "======================================="
echo ""
echo "📝 Access the application:"
echo "   Registration: http://localhost:8000/static/register.html"
echo "   Login:        http://localhost:8000/static/login.html"
echo "   Calculations: http://localhost:8000/static/calculations.html"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "🧪 To run E2E tests:"
echo "   1. Make sure Playwright is installed: playwright install"
echo "   2. Run tests: pytest tests/test_calculations_e2e.py -v"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose down"
echo ""
echo "Happy testing! 🚀"
