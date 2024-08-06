import sqlite3

# Path to your SQLite database
db_path = 'D:/OneDrive - University of the People/Desktop/GITHUB CLONED/Best-AI-Finder/bestaifinder/db.sqlite3'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# SQL query to update the paths
update_query = """
UPDATE ai_tools
SET ai_image = SUBSTR(ai_image, INSTR(ai_image, 'images')),
    ai_tool_logo = SUBSTR(ai_tool_logo, INSTR(ai_tool_logo, 'images'));
"""

# Execute the update query directly in the SQLite database
cursor.execute(update_query)

# Commit the changes
conn.commit()

# SQL query to select the updated paths
select_query = """
SELECT ai_image, ai_tool_logo
FROM ai_tools;
"""

# Execute the query to select the updated paths
cursor.execute(select_query)
updated_paths = cursor.fetchall()

# Print the updated paths for verification
print("Updated Paths:")
for row in updated_paths:
    print(f"Updated AI Image Path: {row[0]}")
    print(f"Updated AI Tool Logo Path: {row[1]}")

# Close the connection
conn.close()

print("Paths updated successfully.")
