# app/API/update_records.py

from fastapi import APIRouter, HTTPException, Request
from typing import List
import logging
from dotenv import load_dotenv
import os, sys
import uuid