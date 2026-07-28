import sqlite3
import os

def connectToPrefixDatabase():
    db_path = os.path.join(os.path.dirname(__file__), "prefixes.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    return conn, cursor

def getPrefix(ctx):
    # print("Prefix call received.")
    try:
        serverID = ctx.guild.id if ctx.guild else None
        if serverID is None:
            return "+"
        
        conn, cursor = connectToPrefixDatabase()
        
        cursor.execute("SELECT prefix FROM serverPrefixes WHERE serverID = ?", (serverID,))
        result = cursor.fetchone()
        conn.close()
        
        return "+" if result is None else result[0]
    except Exception as e:
        return f"Um erro ocorreu: {e}"
    
def getTextFromFile(textFilePath):
    try:
        filepath = os.path.join(os.path.dirname(__file__), textFilePath)
        with open(filepath, "r", encoding = 'utf-8') as f:
            return f.read()
    except Exception as e:
        print("Error opening file.")
        return f"Ocorreu um erro ao abrir o arquivo: {e}"

