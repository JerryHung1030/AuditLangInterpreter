"""
===============================================================================
    Program Name: app.py
    Description:  This script serves as the entry point for the RESTful API built 
                  using FastAPI. It configures the API application, sets up CORS 
                  middleware, and defines routing for API version 1. The application 
                  is designed to be run with Python 3.10.12 and provides a Swagger 
                  UI for API documentation.
                  
    Author:       Dickson
    Email:        Not Provided
    Created Date: 2024-08-12
    Last Updated: 2024-08-29
    Version:      1.0
    
    License:      Commercial License
                  This software is licensed under a commercial license. 
                  Redistribution and use in source and binary forms, with or 
                  without modification, are not permitted without explicit 
                  written permission from the author.
                  
                  You may use this software solely for internal business 
                  purposes within your organization. You may not distribute, 
                  sublicense, or resell this software or its modifications in 
                  any form.

                  Unauthorized copying of this software, via any medium, is 
                  strictly prohibited.

    Usage:        To run the API server, use the following command:
                  `python3 app.py`

                  The server will start on `http://0.0.0.0:8080` and serve the API 
                  endpoints under `/api/v1`. The Swagger UI documentation is available 
                  at `/docs`, and the OpenAPI schema is accessible at `/openapi.json`.

    Requirements: Python 3.10.12, FastAPI, Uvicorn
===============================================================================
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_v1 import router as v1_router

app = FastAPI(docs_url='/docs', redoc_url=None, openapi_url='/openapi.json')  # enable Swagger UI

# Route API
app.include_router(v1_router, prefix='/api/v1')

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    print('★★★★★★ 啟動FastAPI... port num : 8080')
    uvicorn.run(app,
                host='0.0.0.0',
                server_header=False,
                port=8080)
