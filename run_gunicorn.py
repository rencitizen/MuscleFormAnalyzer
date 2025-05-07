import uvicorn
import os
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, request, jsonify, render_template_string, url_for
import multiprocessing
import threading
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app for serving the frontend
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    """Simple frontend for the API"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Muscle-Form Analyzer MVP</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body {
                padding: 20px;
            }
            .container {
                max-width: 800px;
            }
            .mt-5 {
                margin-top: 3rem;
            }
            .mb-4 {
                margin-bottom: 1.5rem;
            }
        </style>
    </head>
    <body data-bs-theme="dark">
        <div class="container">
            <h1 class="mt-5 mb-4">Muscle-Form Analyzer MVP</h1>
            <p class="lead">Upload a workout video to analyze your exercise form.</p>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">API Documentation</h5>
                </div>
                <div class="card-body">
                    <p>The API documentation is available at:</p>
                    <a href="/api/docs" class="btn btn-primary">View API Docs</a>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Upload Video</h5>
                </div>
                <div class="card-body">
                    <form id="uploadForm">
                        <div class="mb-3">
                            <label for="videoFile" class="form-label">Select a video file (MP4 format, max 150MB)</label>
                            <input class="form-control" type="file" id="videoFile" accept="video/mp4">
                        </div>
                        <button type="submit" class="btn btn-success">Analyze Form</button>
                    </form>
                    <div id="uploadStatus" class="mt-3 d-none alert alert-info">
                        Uploading and analyzing video...
                    </div>
                </div>
            </div>
            
            <div id="resultsCard" class="card d-none">
                <div class="card-header">
                    <h5 class="mb-0">Analysis Results</h5>
                </div>
                <div class="card-body">
                    <div id="resultsContainer"></div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const fileInput = document.getElementById('videoFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a video file');
                    return;
                }
                
                document.getElementById('uploadStatus').classList.remove('d-none');
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    // Step 1: Extract landmarks
                    const extractResponse = await fetch('/api/extract', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!extractResponse.ok) {
                        throw new Error(`Error extracting landmarks: ${extractResponse.statusText}`);
                    }
                    
                    const extractData = await extractResponse.json();
                    
                    // Step 2: Compare landmarks
                    const compareResponse = await fetch('/api/compare', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(extractData)
                    });
                    
                    if (!compareResponse.ok) {
                        throw new Error(`Error comparing landmarks: ${compareResponse.statusText}`);
                    }
                    
                    const compareData = await compareResponse.json();
                    
                    // Display results
                    displayResults(compareData[0]); // Show the first frame's results
                    document.getElementById('uploadStatus').classList.add('d-none');
                    document.getElementById('resultsCard').classList.remove('d-none');
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('uploadStatus').classList.add('d-none');
                    alert(`Error analyzing video: ${error.message}`);
                }
            });
            
            function displayResults(data) {
                const resultsContainer = document.getElementById('resultsContainer');
                resultsContainer.innerHTML = '';
                
                // Create overall summary
                const summary = document.createElement('div');
                summary.className = 'mb-4';
                summary.innerHTML = `
                    <h4>Overall Form Assessment</h4>
                    <div class="alert ${data.is_ok ? 'alert-success' : 'alert-danger'}">
                        <strong>${data.is_ok ? 'Good Form!' : 'Form Needs Improvement'}</strong>
                        <p>${data.advice}</p>
                    </div>
                `;
                resultsContainer.appendChild(summary);
                
                // Create details section
                const details = document.createElement('div');
                details.innerHTML = `
                    <h4>Detailed Analysis</h4>
                    <p>Frame: ${data.frame}</p>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Body Part</th>
                                <th>Difference Score</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="detailsTableBody">
                        </tbody>
                    </table>
                `;
                resultsContainer.appendChild(details);
                
                // Populate details table
                const tableBody = document.getElementById('detailsTableBody');
                for (const [bodyPart, score] of Object.entries(data.diffs)) {
                    const row = document.createElement('tr');
                    // Determine if this body part's position is acceptable
                    const isOk = score < 0.05; // Using threshold of 0.05
                    row.innerHTML = `
                        <td>${bodyPart.replace('_', ' ')}</td>
                        <td>${score.toFixed(4)}</td>
                        <td><span class="badge ${isOk ? 'bg-success' : 'bg-danger'}">${isOk ? 'Good' : 'Needs Adjustment'}</span></td>
                    `;
                    tableBody.appendChild(row);
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

def start_fastapi():
    from main import app as fastapi_app
    
    # Mount Flask app under /api path in FastAPI
    fastapi_app.mount("/", WSGIMiddleware(flask_app))
    
    # Start FastAPI with uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Start the FastAPI app directly
    start_fastapi()