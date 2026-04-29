-- Migration: Add authentication fields to usuarios table
-- This migration updates the usuarios table to support email/password authentication

-- Check if columns already exist and add them if needed
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='email') THEN
        ALTER TABLE usuarios ADD COLUMN email VARCHAR(255) UNIQUE NOT NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='password') THEN
        ALTER TABLE usuarios ADD COLUMN password VARCHAR(255) NOT NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='nombre') THEN
        ALTER TABLE usuarios ADD COLUMN nombre VARCHAR(255) NOT NULL DEFAULT 'Usuario';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='baby_birthdate') THEN
        ALTER TABLE usuarios ADD COLUMN baby_birthdate DATE;
    END IF;
END $$;
