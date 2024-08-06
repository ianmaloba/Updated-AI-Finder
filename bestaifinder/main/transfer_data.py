# Transfering data from the SQLite database to Django model

import os
import django
import sqlite3

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bestaifinder.settings.py')
django.setup()

from main.models import AITool

def transfer_data():
    try:
        db_path = 'D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/db.sqlite3'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM ai_tools')
        rows = cursor.fetchall()
        
        for row in rows:
            ai_tool = AITool(
                ai_image=row[1],
                ai_name=row[2],
                ai_tool_logo=row[3],
                ai_short_description=row[4],
                ai_pricing_tag=row[5],
                ai_tags=row[6],
                ai_tool_link=row[7],
            )
            ai_tool.save()

        print("Data transfer completed successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        conn.close()

if __name__ == '__main__':
    transfer_data()
