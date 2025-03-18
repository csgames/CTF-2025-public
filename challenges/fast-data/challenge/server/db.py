import sqlite3

con = sqlite3.connect("data.db")

cursor = con.cursor()

cursor.execute("CREATE TABLE data(color varchar(255), numberInStock int)")

cursor.execute("INSERT INTO data VALUES ('red', 19860)")
cursor.execute("INSERT INTO data VALUES ('blue', 2893)")
cursor.execute("INSERT INTO data VALUES ('yellow', 9521)")
cursor.execute("INSERT INTO data VALUES ('black', 1986)")
cursor.execute("INSERT INTO data VALUES ('white', 6734)")
cursor.execute("INSERT INTO data VALUES ('purple', 7569)")
cursor.execute("INSERT INTO data VALUES ('cyan', 4563)")
cursor.execute("INSERT INTO data VALUES ('orange', 4532)")
cursor.execute("INSERT INTO data VALUES ('green', 7746)")
cursor.execute("INSERT INTO data VALUES ('gray', 2315)")
cursor.execute("INSERT INTO data VALUES ('pink', 6872)")
cursor.execute("INSERT INTO data VALUES ('navy', 7651)")
cursor.execute("INSERT INTO data VALUES ('brown', 1576)")
cursor.execute("INSERT INTO data VALUES ('gold', 14)")
cursor.execute("INSERT INTO data VALUES ('coffee', 852)")
cursor.execute("INSERT INTO data VALUES ('indigo', 999)")
cursor.execute("INSERT INTO data VALUES ('magenta', 244)")
cursor.execute("INSERT INTO data VALUES ('pear', 753)")
cursor.execute("INSERT INTO data VALUES ('#CC7722', 634)")
cursor.execute("INSERT INTO data VALUES ('#BFFF00', 134)")
cursor.execute("INSERT INTO data VALUES ('Secret color', 0)")

con.commit()
