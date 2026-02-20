import sqlite3
import json
from datetime import datetime

DB_NAME = "honeypot.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      session_id TEXT,
                      role TEXT,
                      content TEXT,
                      meta TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()

def save_message(session_id, role, content, meta=None):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO chat_sessions (session_id, role, content, meta) VALUES (?, ?, ?, ?)",
                  (session_id, role, content, json.dumps(meta) if meta else None))
        conn.commit()

def get_history(session_id, limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT role, content FROM chat_sessions WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit))
        rows = c.fetchall()
    return [{"role": r[0], "parts": [r[1]]} for r in rows][::-1]

def get_full_history(session_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM chat_sessions WHERE session_id = ? ORDER BY id ASC", (session_id,))
        rows = c.fetchall()
    return [dict(r) for r in rows]

def clear_session(session_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()

def get_all_extracted_info(session_id):
    """Aggregates all extracted info from past messages in the session."""
    aggregated = {
        "upi_ids": [],
        "phone_numbers": [],
        "bank_accounts": [],
        "sus_links": [],
        "amounts": [],
        "scammer_name": [],
        "scammer_address": [],
        "email_addresses": []
    }
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Get all messages that might have metadata
        c.execute("SELECT meta FROM chat_sessions WHERE session_id = ? AND meta IS NOT NULL", (session_id,))
        rows = c.fetchall()

    for row in rows:
        try:
            if not row['meta']: continue
            meta_data = json.loads(row['meta'])
            
            # The structure might be meta -> extracted_info
            extracted = meta_data.get("extracted_info", {})
            if not extracted: continue

            for key in aggregated.keys():
                new_items = extracted.get(key, [])
                if new_items and isinstance(new_items, list):
                    # Add unique items only
                    current_set = set(aggregated[key])
                    for item in new_items:
                        # Robustness: ensure item is string-like before adding
                        if isinstance(item, (str, int, float)):
                            item_str = str(item)
                            if item_str not in current_set:
                                aggregated[key].append(item_str)
                                current_set.add(item_str)
        except json.JSONDecodeError:
            print(f"Skipping corrupt JSON in history for session {session_id}")
            continue
        except Exception as e:
            print(f"Error processing row in history: {e}")
            continue
            
    return aggregated
