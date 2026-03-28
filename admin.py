def admin_functionalities(conn, uid, name):
    while True:
        print(f"\n===== Admin Menu =====         {name} (uid: {uid})")
        print("1. Platform statistics")
        print("2. Logout")
        print("3. Exit")
        
        choice = input("\nSelect Option (1-3): ").strip()
        
        if choice == "1":
            platform_statistics(conn)
        elif choice == "2":
            print("\nLogging out...")
            break
        elif choice == "3":
            print("\nExiting program...\n \nSee you next time!")
            exit(0)
        else:
            print("\nInvalid choice. Please try again.") 

def platform_statistics(conn):
    #display the platform stats reports for admin
    while True:
        print("\n==== Platform Statistics ====")
        print("1. Top 5 Courses by active enrollment")
        print("2. Payment counts per course")
        print("3. Go back")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            top_courses(conn)
        elif choice == "2":
            payment_counts(conn)
        elif choice == "3":
            return
        else:
            print("\nInvalid Option. Please try again.")

def top_courses(conn):
    cur = conn.cursor()

    # Query to get the top courses
    cur.execute("""
        SELECT c.cid, c.title, COUNT(e.uid) AS active_enrollment
        FROM courses c
        LEFT OUTER JOIN enrollments e ON c.cid = e.cid
            AND CURRENT_TIMESTAMP > e.start_ts
            AND CURRENT_TIMESTAMP < e.end_ts
            AND e.role = 'Student'
        GROUP BY c.cid, c.title
        HAVING active_enrollment >= (
            SELECT MIN(ranked.active_enrollment)
            FROM (
                SELECT COUNT(e2.uid) AS active_enrollment
                FROM courses c2
                LEFT OUTER JOIN enrollments e2 ON c2.cid = e2.cid
                    AND CURRENT_TIMESTAMP > e2.start_ts
                    AND CURRENT_TIMESTAMP < e2.end_ts
                    AND e2.role = 'Student'
                GROUP BY c2.cid
                ORDER BY active_enrollment DESC
                LIMIT 5
            ) AS ranked
        )
        ORDER BY active_enrollment DESC;
    """)

    # fetch the top courses
    top_course = cur.fetchall()

    # check if there is any enrollment data
    if len(top_course) == 0:
        print("\nNo enrollment data found.")
        return
    
    # print the top courses
    print("\n--- Top 5 Courses by Active Enrollment ---")
    for course in top_course:
        print(f"\ncid: {course[0]} | Title: {course[1]} | Active Enrollment: {course[2]}")

def payment_counts(conn):
    cur = conn.cursor()

    # Query to get the payment counts
    cur.execute("""
        SELECT c.cid, c.title, COUNT(p.uid) AS payment_count
        FROM courses c
        LEFT OUTER JOIN payments p ON c.cid = p.cid
        GROUP BY c.cid, c.title
        ORDER BY payment_count DESC;
    """)

    # fetch the payment counts
    pay_count = cur.fetchall()

    # check if there is any payment data
    if len(pay_count) == 0:
        print("\nNo payment data found")
        return
    
    # print the payment counts
    print("\n--- Payment Counts Per Course ---")
    for payment in pay_count:
        print(f"\ncid: {payment[0]} | Title: {payment[1]} | Payment Count: {payment[2]}")
