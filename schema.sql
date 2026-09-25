CREATE TABLE IF NOT EXISTS students (
  student_id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, gender TEXT NOT NULL,
  date_of_birth TEXT, phone TEXT, email TEXT, address TEXT, class TEXT NOT NULL, section TEXT NOT NULL,
  roll_number TEXT NOT NULL, admission_date TEXT, academic_year TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Active',
  UNIQUE(class, section, roll_number, academic_year)
);
CREATE TABLE IF NOT EXISTS teachers (
  teacher_id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, gender TEXT NOT NULL,
  date_of_birth TEXT, phone TEXT, email TEXT, address TEXT, subject TEXT NOT NULL, qualification TEXT,
  joining_date TEXT, salary REAL, status TEXT NOT NULL DEFAULT 'Active'
);
CREATE TABLE IF NOT EXISTS staff (
  staff_id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, gender TEXT NOT NULL,
  phone TEXT, email TEXT, address TEXT, role TEXT NOT NULL, joining_date TEXT, salary REAL, status TEXT NOT NULL DEFAULT 'Active'
);
CREATE TABLE IF NOT EXISTS classes (
  class_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, section TEXT NOT NULL, academic_year TEXT NOT NULL, class_teacher TEXT,
  UNIQUE(name, section, academic_year)
);
CREATE TABLE IF NOT EXISTS subjects (
  subject_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, code TEXT NOT NULL UNIQUE, class_name TEXT, teacher TEXT
);
CREATE TABLE IF NOT EXISTS student_history (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, previous_class TEXT NOT NULL, previous_section TEXT NOT NULL,
  previous_academic_year TEXT NOT NULL, promoted_to_class TEXT NOT NULL, promoted_to_section TEXT NOT NULL,
  new_academic_year TEXT NOT NULL, promotion_date TEXT NOT NULL, FOREIGN KEY(student_id) REFERENCES students(student_id)
);
