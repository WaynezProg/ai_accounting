-- Migration: Add monthly_budget column to users table
-- Date: 2026-01-17
-- Description: 新增月預算欄位到用戶資料表

ALTER TABLE users ADD COLUMN monthly_budget INTEGER DEFAULT NULL;
