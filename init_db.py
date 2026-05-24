import sqlite3

def init_db():
    # Connect to SQLite database (this creates the file if it doesn't exist)
    conn = sqlite3.connect('iot_platform.db')
    cursor = conn.cursor()

    # Create the Devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Devices (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Protocol TEXT NOT NULL,
            ThingsBoardToken TEXT NOT NULL
        )
    ''')

    # Create the Telemetry table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Telemetry (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DeviceID INTEGER,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            Value REAL,
            FOREIGN KEY(DeviceID) REFERENCES Devices(ID)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and tables initialized successfully.")

if __name__ == '__main__':
    init_db()
