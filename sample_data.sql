-- =============================================================================
-- TEST DATA FOR COURSE PLATFORM
-- =============================================================================
-- LOGIN CREDENTIALS:
--   Students:    uid=1 pass1, uid=2 pass2, uid=3 pass3, uid=4 pass4, uid=5 pass5
--   Instructors: uid=6 teach1 (teaches cid 1,2,5), uid=7 teach2 (teaches cid 3,4,6)
--   Admin:       uid=8 admin1
-- =============================================================================

-- USERS
INSERT INTO users (uid, name, email, role, pwd) VALUES (1, 'Alice Smith',  'alice@example.com',  'Student',    'pass1');
INSERT INTO users (uid, name, email, role, pwd) VALUES (2, 'Bob Johnson',  'bob@example.com',    'Student',    'pass2');
INSERT INTO users (uid, name, email, role, pwd) VALUES (3, 'Carol White',  'carol@example.com',  'Student',    'pass3');
INSERT INTO users (uid, name, email, role, pwd) VALUES (4, 'David Lee',    'david@example.com',  'Student',    'pass4');
INSERT INTO users (uid, name, email, role, pwd) VALUES (5, 'Eva Green',    'eva@example.com',    'Student',    'pass5');
INSERT INTO users (uid, name, email, role, pwd) VALUES (6, 'Dr. Miller',   'miller@example.com', 'Instructor', 'teach1');
INSERT INTO users (uid, name, email, role, pwd) VALUES (7, 'Prof. Chen',   'chen@example.com',   'Instructor', 'teach2');
INSERT INTO users (uid, name, email, role, pwd) VALUES (8, 'Admin User',   'admin@example.com',  'Admin',      'admin1');

-- =============================================================================
-- COURSES
-- cid 1 (Intro to Python):    Alice enrolled, all lessons done, grades exist  -> TEST: certificate, grades, mark complete already done
-- cid 2 (Web Development):    Alice enrolled, no grades                       -> TEST: see grades shows N/A
-- cid 3 (Data Science 101):   Carol enrolled, partial completion              -> TEST: some Completed some Not Completed
-- cid 4 (Machine Learning):   max_students=2, David+Eva enrolled (FULL)      -> TEST: enroll blocked when full
-- cid 5 (Databases):          nobody enrolled as student                      -> TEST: search and fresh enroll
-- cid 6 (Digital Marketing):  no students enrolled                            -> TEST: admin top 5 and payment_count=0
-- =============================================================================
INSERT INTO courses (cid, title, description, category, price, pass_grade, max_students) VALUES (1, 'Intro to Python',   'Learn Python from scratch',                'Programming', 49.99,  60, 30);
INSERT INTO courses (cid, title, description, category, price, pass_grade, max_students) VALUES (2, 'Web Development',   'HTML, CSS, and JavaScript basics',         'Programming', 79.99,  65, 25);
INSERT INTO courses (cid, title, description, category, price, pass_grade, max_students) VALUES (3, 'Data Science 101',  'Intro to data analysis and visualization', 'Data',        99.99,  70, 20);
INSERT INTO courses (cid, title, description, category, price, pass_grade, max_students) VALUES (4, 'Machine Learning',  'Supervised and unsupervised learning',     'Data',        129.99, 75,  2);
INSERT INTO courses (cid, title, description, category, price, pass_grade, max_students) VALUES (5, 'Databases',         'SQL and relational database design',       'Programming', 59.99,  60, 30);
INSERT INTO courses (cid, title, description, category, price, pass_grade, max_students) VALUES (6, 'Digital Marketing', 'SEO, social media, and ads',               'Business',    39.99,  55, 50);

-- =============================================================================
-- ENROLLMENTS
-- =============================================================================
-- Alice (uid=1): cid1 and cid2
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (1, 1, '2024-01-01 10:00:00', '2027-01-01 10:00:00', 'Student');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (2, 1, '2024-03-01 10:00:00', '2027-03-01 10:00:00', 'Student');
-- Bob (uid=2): cid1 only
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (1, 2, '2024-02-01 10:00:00', '2027-02-01 10:00:00', 'Student');
-- Carol (uid=3): cid3 only
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (3, 3, '2024-01-15 10:00:00', '2027-01-15 10:00:00', 'Student');
-- David (uid=4): cid4 (fills spot 1 of 2)
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (4, 4, '2024-04-01 10:00:00', '2027-04-01 10:00:00', 'Student');
-- Eva (uid=5): cid4 (fills spot 2 of 2 - now FULL)
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (4, 5, '2024-05-01 10:00:00', '2027-05-01 10:00:00', 'Student');
-- Extra enrollments in cid1 so admin top 5 shows cid1=5, cid2=1, cid3=1, cid4=2
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (1, 3, '2024-03-01 10:00:00', '2027-03-01 10:00:00', 'Student');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (1, 4, '2024-04-01 10:00:00', '2027-04-01 10:00:00', 'Student');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (1, 5, '2024-05-01 10:00:00', '2027-05-01 10:00:00', 'Student');
-- Instructor enrollments
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (1, 6, '2023-01-01 10:00:00', '2027-12-31 10:00:00', 'Instructor');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (2, 6, '2023-01-01 10:00:00', '2027-12-31 10:00:00', 'Instructor');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (5, 6, '2023-01-01 10:00:00', '2027-12-31 10:00:00', 'Instructor');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (3, 7, '2023-01-01 10:00:00', '2027-12-31 10:00:00', 'Instructor');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (4, 7, '2023-01-01 10:00:00', '2027-12-31 10:00:00', 'Instructor');
INSERT INTO enrollments (cid, uid, start_ts, end_ts, role) VALUES (6, 7, '2023-01-01 10:00:00', '2027-12-31 10:00:00', 'Instructor');

-- =============================================================================
-- MODULES
-- =============================================================================
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (1, 1, 'Python Basics',          'Variables, types, and control flow',        30);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (1, 2, 'Functions & Modules',    'Defining and importing functions',          40);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (1, 3, 'OOP in Python',          'Classes, objects, inheritance',             30);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (2, 1, 'HTML Fundamentals',      'Tags, structure, and semantics',            25);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (2, 2, 'CSS Styling',            'Selectors, layout, and responsive',         25);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (2, 3, 'JavaScript Basics',      'DOM, events, and functions',                50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (3, 1, 'Pandas & NumPy',         'Data manipulation with Python',             50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (3, 2, 'Data Visualization',     'Matplotlib and Seaborn',                    50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (4, 1, 'Supervised Learning',    'Regression and classification',             50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (4, 2, 'Unsupervised Learning',  'Clustering and dimensionality reduction',   50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (5, 1, 'SQL Basics',             'SELECT, WHERE, and JOINs',                  50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (5, 2, 'Database Design',        'Normalization and ER diagrams',             50);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (6, 1, 'SEO Fundamentals',       'Keywords, meta tags, and indexing',         40);
INSERT INTO modules (cid, mid, name, summary, weight) VALUES (6, 2, 'Social Media Marketing', 'Content strategy and engagement',           60);

-- =============================================================================
-- LESSONS
-- cid1 has 5 lessons total (Alice completed ALL 5)
-- cid3 has 2 lessons (Carol completed only 1)
-- =============================================================================
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (1, 1, 1, 'Hello World',        30, 'Your first Python program');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (1, 1, 2, 'Variables & Types',  45, 'int, float, str, bool explained');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (1, 2, 1, 'Writing Functions',  60, 'def, return, parameters');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (1, 2, 2, 'Importing Modules',  45, 'import, from, as keywords');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (1, 3, 1, 'Classes & Objects',  60, 'class syntax and instantiation');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (2, 1, 1, 'HTML Structure',     30, 'html, head, body tags');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (2, 1, 2, 'Forms & Inputs',     45, 'form elements and attributes');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (2, 2, 1, 'CSS Selectors',      30, 'class, id, element selectors');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (2, 3, 1, 'Intro to JS',        60, 'variables, functions, events');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (3, 1, 1, 'Intro to Pandas',    60, 'DataFrames and Series');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (3, 2, 1, 'Plotting with MPL',  45, 'line, bar, scatter plots');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (4, 1, 1, 'Linear Regression',  60, 'Fitting and interpreting models');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (4, 2, 1, 'K-Means Clustering', 45, 'Unsupervised grouping');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (5, 1, 1, 'SELECT Statements',  45, 'Basic queries and filtering');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (5, 1, 2, 'JOINs',              60, 'INNER, LEFT, RIGHT JOIN');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (5, 2, 1, 'Normal Forms',       60, '1NF, 2NF, 3NF explained');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (6, 1, 1, 'Keyword Research',   45, 'Finding and targeting keywords');
INSERT INTO lessons (cid, mid, lid, title, duration, content) VALUES (6, 2, 1, 'Content Calendar',   45, 'Planning and scheduling posts');

-- =============================================================================
-- COMPLETION
-- Alice (uid=1): ALL 5 lessons in cid1 done  -> "already completed" message + certificate eligible
-- Bob (uid=2):   2 of 5 lessons in cid1 done -> partial
-- Carol (uid=3): 1 of 2 lessons in cid3 done -> lid1 Completed, lid2(plotting) Not Completed
-- =============================================================================
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (1, 1, 1, 1, '2024-01-05 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (1, 1, 1, 2, '2024-01-06 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (1, 1, 2, 1, '2024-01-10 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (1, 1, 2, 2, '2024-01-11 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (1, 1, 3, 1, '2024-01-15 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (2, 1, 1, 1, '2024-02-05 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (2, 1, 1, 2, '2024-02-06 10:00:00');
INSERT INTO completion (uid, cid, mid, lid, ts) VALUES (3, 3, 1, 1, '2024-01-20 10:00:00');

-- =============================================================================
-- GRADES
-- Alice (uid=1) cid1: (85*30 + 90*40 + 78*30) / 100 = 84.9
-- Bob (uid=2) cid1:   only module 1 graded     -> partial grades shown
-- Carol (uid=3) cid3: (88*50 + 91*50) / 100 = 89.5
-- David (uid=4) cid4: NO grades                -> final_grade = N/A
-- =============================================================================
INSERT INTO grades (uid, cid, mid, received_ts, grade) VALUES (1, 1, 1, '2024-01-20 10:00:00', 85);
INSERT INTO grades (uid, cid, mid, received_ts, grade) VALUES (1, 1, 2, '2024-02-01 10:00:00', 90);
INSERT INTO grades (uid, cid, mid, received_ts, grade) VALUES (1, 1, 3, '2024-02-15 10:00:00', 78);
INSERT INTO grades (uid, cid, mid, received_ts, grade) VALUES (2, 1, 1, '2024-03-01 10:00:00', 72);
INSERT INTO grades (uid, cid, mid, received_ts, grade) VALUES (3, 3, 1, '2024-02-01 10:00:00', 88);
INSERT INTO grades (uid, cid, mid, received_ts, grade) VALUES (3, 3, 2, '2024-02-20 10:00:00', 91);

-- =============================================================================
-- CERTIFICATES
-- Alice has cert for cid1 (all lessons done + 84.9 >= 60)             -> TEST: see certificate shows it
-- Carol has cert for cid3 (89.5 >= 70 BUT only 1/2 lessons done)      -> TEST: instructor lowers pass_grade,
--   cert stays; instructor RAISES pass_grade above 89.5, cert removed
-- =============================================================================
INSERT INTO certificates (cid, uid, received_ts, final_grade) VALUES (1, 1, '2024-03-01 10:00:00', 84.9);
INSERT INTO certificates (cid, uid, received_ts, final_grade) VALUES (3, 3, '2024-03-01 10:00:00', 89.5);

-- =============================================================================
-- PAYMENTS (masked card numbers, MM/YYYY expiry)
-- Alice has 2 payments (cid1 and cid2) -> TEST: past payments shows 2 rows most recent first
-- =============================================================================
INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date) VALUES (1, 1, '2024-01-01 09:00:00', '************5678', '12/2027');
INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date) VALUES (1, 2, '2024-03-01 09:00:00', '1234567890123456', '12/2027');
INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date) VALUES (2, 1, '2024-02-01 09:00:00', '************6789', '06/2028');
INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date) VALUES (3, 3, '2024-01-15 09:00:00', '************7890', '09/2028');
INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date) VALUES (4, 4, '2024-04-01 09:00:00', '1234567890234567', '03/2029');
INSERT INTO payments (uid, cid, ts, credit_card_no, expiry_date) VALUES (5, 4, '2024-05-01 09:00:00', '************9012', '11/2027');
