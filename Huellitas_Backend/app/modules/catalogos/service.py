from app.core.database import supabase

def get_tipos_animal():
    return supabase.table("tipoanimal").select("*").execute().data

def get_tipos_reporte():
    return supabase.table("tiporeporte").select("*").execute().data

def get_urgencias():
    return supabase.table("urgencia").select("*").execute().data