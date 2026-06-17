import os
from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv

# 1. Cargamos el archivo .env
load_dotenv()

# 2. Leemos las variables limpias
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"--- REVISAN