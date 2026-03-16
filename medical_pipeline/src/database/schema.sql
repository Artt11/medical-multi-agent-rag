IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'patients')
BEGIN
    CREATE TABLE patients (
        id INT IDENTITY(1,1) PRIMARY KEY, 
        name NVARCHAR(MAX) NOT NULL,     
        dob DATE,
        gender NVARCHAR(50),
        email NVARCHAR(255),
        phone NVARCHAR(50),
        social_card NVARCHAR(100) UNIQUE,
        patient_id NVARCHAR(100) UNIQUE,
       
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'medical_exams')
BEGIN
    CREATE TABLE medical_exams (
        exam_id INT IDENTITY(1,1) PRIMARY KEY,
        patient_id INT FOREIGN KEY REFERENCES patients(id) ON DELETE CASCADE,
        source_file NVARCHAR(MAX),
        exam_date DATE,
        examination_type NVARCHAR(255),
        
        diagnosis NVARCHAR(MAX),
        conclusion NVARCHAR(MAX),
        recommendations NVARCHAR(MAX),
        full_json NVARCHAR(MAX),
        
        document_hash VARCHAR(64) UNIQUE 
    );
END

-- IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'chat_history')
-- BEGIN
--     CREATE TABLE chat_history (
--         id INT IDENTITY(1,1) PRIMARY KEY,
--         session_id NVARCHAR(100) NOT NULL, 
--         role NVARCHAR(20) NOT NULL, 
--         content NVARCHAR(MAX) NOT NULL,
--         created_at DATETIME DEFAULT GETDATE()
--     );
--     CREATE INDEX IX_ChatHistory_SessionID ON chat_history (session_id);
-- END