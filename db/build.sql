Create TABLE Guilds(
    Server_ID INT,
    Server_Name TEXT,
    PRIMARY KEY (Server_ID)
);

CREATE TABLE IF NOT EXISTS Users(
    User_ID INT PRIMARY KEY,
    Profile TEXT,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS RefSheets(
    Ref_ID INT UNIQUE,
    user_id FOREIGN KEY(),
    Name VARCHAR(20)
    Ref TEXT,
    PRIMARY KEY (Ref_ID),
    FOREIGN KEY (user_id) REFERENCES (Users)
);