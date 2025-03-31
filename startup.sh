#!/bin/bash
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

