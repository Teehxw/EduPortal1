import sys

#-----INSTRUCTOR FUNCTIONALITIES----#

def instructor_functionalities(conn, uid, name):
    """Gives the options of choosing what the instructor wants to see and do   """
    while True:
        print(f"\n==== INSTRUCTOR MENU ====         {name} (uid: {uid})\n")
        print("1. Update Course" )
        print("2. Override Enrollment")
        print("3. Course Stats")
        print("4. Logout")
        print("5. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == "1":
            update_course(conn, uid)
        
        elif choice == "2":
            override_enroll(conn, uid)

        elif choice == "3":
            course_stats(conn, uid)
            
        elif choice == "4":
            print("\nLogging out...")
            break  # Goes back to login screen
        
        elif choice == "5":
            print("\nExiting program...\n \nSee you next time!")
            conn.close()
            exit(0)
            
        else:
            print("\nInvalid option. Please try again.")

def update_course(conn, uid):
            
            cur = conn.cursor()

            cur.execute("""
                       SELECT c.cid, c.title, c.category,c.price,c.pass_grade,c.max_students,COUNT(e.uid) AS current_enrollment
                        FROM courses c
                        LEFT JOIN enrollments e ON c.cid = e.cid
                        WHERE e.uid = ?
                        GROUP BY c.cid, c.title, c.category,c.price, c.pass_grade, c.max_students;""", (uid,))
            
            instructor_courses = cur.fetchall()
            print("\n---- YOUR COURSES ----")
            
            #Print the courses 
            for course in instructor_courses:
                print(f"\ncid: {course[0]} ")
                print(f"Course Title: {course[1]} ")
                print(f"Category: {course[2]} ")
                print(f"Price: ${course[3]:.2f} ")
                print(f"Pass grade: {course[4]} ")
                print(f"Max students: {course[5]} ")
                print(f"Current Enrollment: {course[6]} ")

            # valid course ids
            valid_cid = []
            for course in instructor_courses:
                valid_cid.append(course[0])

            #Ask for which course to update:
            course_update = int(input("\nEnter the Course ID (cid) to update: "))

            while course_update not in valid_cid:
                print("Course not found\n")
                course_update = int(input("Try again. Enter cid: "))


            print( "\n--- UPDATE MENU ---\n")
            print("1. Price")
            print("2. Pass Grade ") 
            print("3. Max Students ")
            print("4. Return to main menu ")
            
            update_item = input( "\nWhich would you like to update (1-4):").strip()

            if update_item == "1":
                new_price = float(input("What is your new price: "))
                cur.execute("""
                            UPDATE Courses
                            SET price = ? 
                            WHERE cid = ? 
                            """, (new_price, course_update) )

                conn.commit()

                cur.execute("""
                            SELECT cid, price, pass_grade, max_students
                            FROM courses
                            WHERE cid = ?;""", (course_update,))
                            
                updated_course = cur.fetchone()
                
                print("\nCOURSE UPDATED!")
                print(f"\ncid: {updated_course[0]}")
                print(f"Price: ${updated_course[1]:.2f}")
                print(f"Pass grade: {updated_course[2]}")
                print(f"Max students: {updated_course[3]}")


            #certificates issue
            elif update_item == "2":
                new_pass_grade = float(input( "New pass grade: "))
                cur.execute("""
                            UPDATE Courses
                            SET pass_grade = ? 
                            WHERE cid = ? 
                            ;""", (new_pass_grade, course_update) )

                conn.commit()
                

                cur.execute(""" 
                            SELECT e.uid
                            FROM enrollments e
                            INNER JOIN users u ON e.uid = u.uid
                            WHERE e.cid = ?
                            AND u.role = 'Student'
                            AND CURRENT_TIMESTAMP BETWEEN e.start_ts 
                            AND e.end_ts;""",(course_update,))
                
                active_enrollment = cur.fetchall()
                
                cur.execute(""" 
                            SELECT COUNT(*) 
                            FROM lessons
                            WHERE cid = ?;""",(course_update,))

                lessons = cur.fetchone()[0]     # gets the cid

                certificates_added = 0
                certificates_removed = 0

                for student in active_enrollment:
                    student_uid = student[0]


                # lessons completed by student
                    cur.execute("""
                                SELECT COUNT(*)
                                FROM completion
                                WHERE cid = ? AND uid = ?
                                """, (course_update, student_uid))
                    
                    lessons_completed = cur.fetchone()[0]

                # compute final grade
                    cur.execute("""
                                SELECT COALESCE(SUM(g.grade * m.weight),0)
                                FROM grades g
                                LEFT JOIN modules m
                                ON g.cid = m.cid AND g.mid = m.mid
                                WHERE g.cid = ? AND g.uid = ?
                                """, (course_update, student_uid))
                    final_grade = cur.fetchone()[0]


                # check if certificate exists
                    cur.execute("""
                                SELECT COUNT(*)
                                FROM certificates
                                WHERE cid = ? AND uid = ?
                                """, (course_update, student_uid))
                    
                    cert_exists = cur.fetchone()[0] > 0

                # determine qualification
                    
                    student_qualified = (lessons > 0) and (lessons_completed == lessons) and (final_grade >= new_pass_grade)

                # insert certificate
                    if student_qualified and not cert_exists:
                         cur.execute("""
                                     INSERT INTO certificates (cid, uid, received_ts, final_grade)
                                     VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                                     """, (course_update, student_uid, final_grade))
                         
                         certificates_added += 1

    # remove certificate
                    elif not student_qualified and cert_exists:
                        cur.execute("""
                                    DELETE FROM certificates
                                    WHERE cid = ? AND uid = ?
                                    """, (course_update, student_uid))
                        
                        certificates_removed += 1

                conn.commit()

                cur.execute("""
                            SELECT cid, price, pass_grade, max_students
                            FROM courses
                            WHERE cid = ?
                            """, (course_update,))

                course_info = cur.fetchone()
                cid, price, pass_grade, max_students = course_info
                
                # unwrap the tuple
                print("\nPASS GRADE UPDATED!")
                print(f"\ncid: {cid}")
                print(f"Price: ${price:.2f}")
                print(f"Pass grade: {pass_grade}")
                print(f"Max students: {max_students}")
                print(f"Certificates added: {certificates_added}")
                print(f"Certificates removed: {certificates_removed}")

            elif update_item == "3":
                new_max_students = int(input( "\nNew maximum of students: "))
                cur.execute("""
                            UPDATE Courses
                            SET max_students = ? 
                            WHERE cid = ?;"""
                            , (new_max_students, course_update) )

                conn.commit()

                cur.execute("""
                            SELECT cid, price, pass_grade, max_students
                            FROM courses
                            WHERE cid = ?;""", (course_update,))
                            
                updated_course = cur.fetchone()
                
             
                print("\nCOURSE UPDATED!")
                print(f"\ncid: {updated_course[0]}")
                print(f"Price: ${updated_course[1]:.2f}")
                print(f"Pass grade: {updated_course[2]}")
                print(f"Max students: {updated_course[3]}")
                
            elif update_item == "4":
                return



def override_enroll(conn,uid):
    
    cur = conn.cursor()

    std_uid = int(input("Enter student(uid): "))
    cid = int(input("Enter the ID of the course: "))

    cur.execute("""
        SELECT c.title
        FROM courses c
        JOIN enrollments e ON c.cid = e.cid
        WHERE e.cid = ? AND e.uid = ? AND e.role = 'Instructor' """, (cid, uid))
    
    instructor_course = cur.fetchone()

    
    
    if instructor_course is None:
        print("\nYou are not authorized to enroll students in this course.")
        print("You can only enroll students in courses you teach.")
        return

    course_title = instructor_course[0]

    cur.execute("""
        SELECT name
        FROM users
        WHERE uid = ? AND role = 'Student' """, (std_uid,))
    
    user = cur.fetchone()
    
    if user is None:
        print("Id does not exist or the user is not a student.")
        return
    
    student_name = user[0]

    cur.execute("""
        SELECT *
        FROM enrollments
        WHERE cid = ? AND uid = ?; """, (cid, std_uid))
    
    if cur.fetchone():
        print("\nStudent is enrolled in this course already.")
        return
    
    cur.execute("""
        INSERT INTO enrollments (cid, uid, role, start_ts, end_ts)
        VALUES (?, ?, 'Student', CURRENT_TIMESTAMP, DATETIME(CURRENT_TIMESTAMP, '+1 year')) """, (cid, std_uid))
    
    cur.execute("""
        INSERT INTO payments (uid, cid, credit_card_no, expiry_date, ts)
        VALUES (?, ?, '0000000000000000', '12/2026', CURRENT_TIMESTAMP) """, (std_uid, cid))

    conn.commit()
    
    cur.execute("""
        SELECT c.title, e.start_ts
        FROM courses c
        JOIN enrollments e ON c.cid = e.cid
        WHERE c.cid = ? AND e.uid = ?
        ORDER BY e.start_ts DESC
        LIMIT 1 """, (cid, std_uid))

    result = cur.fetchone()
    course_title, start_ts = result

    # Print enrollment confirmation

    print("\nSTUDENT IS ENROLLED ---")
    print(f"\ncid: {cid}")
    print(f"Course Title: {course_title}")
    print(f"Student uid: {std_uid}")
    print(f"Student Name: {student_name}")
    print(f"Start timestamp: {start_ts}")

def course_stats(conn,uid):


    cur = conn.cursor()


    cur.execute("""
                SELECT c.cid, c.title,
                COUNT (DISTINCT e.uid)  AS active_enrollment,
                CASE
                WHEN COUNT(DISTINCT e.uid) = 0 THEN 0
                ELSE 100.0 * COUNT(DISTINCT cert.uid) / COUNT(DISTINCT e.uid)
                END AS completion_rate,
                    AVG(cert.final_grade) AS average_final_grade
                FROM courses c

                LEFT OUTER JOIN enrollments e
                ON c.cid = e.cid
                AND e.role = 'Student'

                LEFT OUTER JOIN certificates cert
                ON cert.cid = c.cid
                AND cert.uid = e.uid

                WHERE c.cid IN (
                    SELECT cid
                    FROM enrollments
                    WHERE uid = ?
                    AND role = 'Instructor'
                )

                GROUP BY c.cid, c.title;
""", (uid,))

    stats = cur.fetchall()

    # Print the stats2
    for course in stats:
       cid, title, active_enrollment, completion_rate, avg_final_grade = course
       print(f"\ncid: {cid}")
       print(f"Course Title: {title}")
       print(f"Active enrollment: {active_enrollment}")
       print(f"Completion rate: {completion_rate}")
       print(f"Average final grade: {avg_final_grade}")
