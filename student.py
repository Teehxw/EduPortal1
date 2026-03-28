import sqlite3
from datetime import datetime, date
import calendar

#-----STUDENT FUNCTIONALITIES-----#
def student_functionalities(conn, uid, name):
   """Gives the options of choosing what the student wants to see and do   """
   while True:
       print(f"\n==== STUDENT MENU ====         {name} (uid: {uid})")
       print("1. Search for courses" )
       print("2. View enrolled courses")
       print("3. See Past Payments")
       print("4. Logout")
       print("5. Exit")
      
       choice = input("Select an option: ").strip()
      
       if choice == "1":
           search_courses(conn, uid)

       elif choice == "2":
           view_enrolled_courses(conn, uid)
          
       elif choice == "3":
           view_past_payments(conn, uid)
          
       elif choice == "4":
           print("\nLogging out...")
           break
      
       elif choice == "5":
           print("\nExiting program...\n \nSee you next time!")
           conn.close()
           exit(0)
          
       else:
           print("\nInvalid option. Please try again.")


def search_courses(conn, uid):
    cur = conn.cursor()
    key = input("\nEnter keyword: ").strip().lower()

    print("\n --- Filters ---")
    print("1. Category")
    print("2. Price Range")
    filter_choice = input("\nEnter filter (Press ENTER for none): ").strip()

    base_query = """
        SELECT c.cid, c.title, c.description, c.category, c.price, c.pass_grade, c.max_students, COUNT(e.uid) AS current_enrollment
        FROM courses c
        LEFT OUTER JOIN enrollments e ON c.cid = e.cid
        AND CURRENT_TIMESTAMP > e.start_ts
        AND CURRENT_TIMESTAMP < e.end_ts
        AND e.role = 'Student'
        WHERE (LOWER(c.title) LIKE ? OR LOWER(c.description) LIKE ?)
    """

    params = [f"%{key}%", f"%{key}%"]

    if filter_choice == "1":
        category = input("Enter category: ").strip().lower()
        base_query += " AND LOWER(c.category) = ?"
        params.append(category)
    elif filter_choice == "2":
        try:
            min_price = float(input("Enter min price: ").strip())
            max_price = float(input("Enter max price: ").strip())
        except ValueError:
            print("Invalid price entered. Searching without price filter.")
            min_price, max_price = None, None

        if min_price is not None and max_price is not None:
            base_query += " AND c.price >= ? AND c.price <= ?"
            params.extend([min_price, max_price])
    
    base_query += " GROUP BY c.cid, c.title, c.description, c.category, c.price, c.pass_grade, c.max_students;"

    cur.execute(base_query, params)
    search_result = cur.fetchall()

    if len(search_result) == 0:
        print("\nNo courses found")
        return
    
    course_cid = pagination(5, search_result, "SEARCH RESULTS", print_search, state=True)

    if course_cid is None:
        return

    cur.execute("""
        SELECT c.cid, c.title, c.description, c.category, c.price, c.pass_grade, c.max_students, COUNT(e.uid) AS current_enrollment
        FROM courses c
        LEFT OUTER JOIN enrollments e ON c.cid = e.cid
        AND CURRENT_TIMESTAMP > e.start_ts
        AND CURRENT_TIMESTAMP < e.end_ts
        WHERE c.cid = ?
        GROUP BY c.cid, c.title, c.description, c.category, c.price, c.pass_grade, c.max_students;""",
        (course_cid,)
    )

    result_course = cur.fetchone()

    if result_course is None:
        print("\nCourse Not Found")
        return
    else:
        print(f"\ncid: {result_course[0]}\nTitle: {result_course[1]}\nDescription: {result_course[2]}\nCategory: {result_course[3]}\nPrice: ${result_course[4]:.2f}\nPass Grade: {result_course[5]}\nMax Students: {result_course[6]}\nCurrent Enrollment: {result_course[7]}")
    
    cur.execute("""
        SELECT *
        FROM enrollments
        WHERE cid = ?
        AND uid = ?
        AND CURRENT_TIMESTAMP > start_ts
        AND CURRENT_TIMESTAMP < end_ts;""",
        (course_cid, uid)
    )

    user_enroll = cur.fetchone()

    if user_enroll is not None:
        print("Already enrolled in the course")
    else:
        enroll_input = input("\nNot enrolled in this course. Would you wish to enroll? (y/n): ").lower().strip()

        if enroll_input == 'y':
            print("\n--- PAYMENT ----")
            enroll(conn, result_course, uid)
        elif enroll_input == 'n':
            return
        else:
            print("Invalid input")

    cur.close()

def enroll(conn, course, uid):
   """Enrolls the user into a course"""
   cur = conn.cursor()
   cid, title, description, category, price, pass_grade, max_students, current_enrollment = course

   cur.execute("""
       SELECT *
       FROM enrollments
       WHERE cid = ?
       AND uid = ?
       AND CURRENT_TIMESTAMP > start_ts
       AND CURRENT_TIMESTAMP < end_ts;""",
       (cid, uid)
   )

   if cur.fetchone() != None:
       print("Already enrolled in this course")
       return

   if current_enrollment >= max_students:
       print("The course is full. Cannot be enrolled")
       return

   card_num = input("\nEnter credit card number (16 digits):  ").replace(" ", "")
   cvv = input("Enter CVV (3 digits): ").strip()
   expiry_date = input("Enter expiry date (MM/YYYY): ").strip()

   if not (card_num.isdigit() and len(card_num) == 16):
       print("\nInvalid card number. Try again")
       return
   if not (cvv.isdigit() and len(cvv)==3):
       print("\nInvalid CVV. Try again")
       return

   check_expiry = datetime.strptime(expiry_date, "%m/%Y").date()
   check_expiry = date(check_expiry.year, check_expiry.month, calendar.monthrange(check_expiry.year, check_expiry.month)[1])
   current_day = date.today()
   if check_expiry < current_day:
       print("\nCard has expired")
       return

   cur.execute("""
       INSERT INTO enrollments
       VALUES (?, ?, CURRENT_TIMESTAMP, DATETIME(CURRENT_TIMESTAMP, '+1 year'), 'Student')""",
       (cid, uid)
   )

   ts = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

   mask = '*' * 12 
   masked_card = mask + card_num[-4:]

   cur.execute("""
        INSERT INTO payments
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)""",
        (uid, cid, masked_card, expiry_date)
   )
      
   conn.commit()
   cur.close()

   print(f"\nENROLLMENT SUCCESSFUL\n")
   print(f"cid: {cid}\n")
   print(f"title: {title}\n")
   print(f"price: ${price:.2f}\n")
   print(f"Timestamp: {ts}\n")
   print(f"Card Number: {masked_card}\n")


def view_enrolled_courses(conn, uid):
   cur = conn.cursor()

   cur.execute("""
       SELECT c.cid, c.title, c.category, e.start_ts, c.pass_grade
       FROM enrollments e
       LEFT OUTER JOIN courses c ON e.cid = c.cid
       WHERE e.uid = ?
       AND e.role = 'Student'
       AND CURRENT_TIMESTAMP > e.start_ts 
       AND CURRENT_TIMESTAMP < e.end_ts
       ORDER BY e.start_ts DESC
   """, (uid,))

   enrollments = cur.fetchall()

   if len(enrollments) == 0:
       print("\nCurrently not enrolled in any courses.")
       return

   # use the pagination function to get the selected cid
   course_select = pagination(5, enrollments, "ACTIVE ENROLLMENTS", print_enrollment, state=True)
   
   # check if the user even entered a cid
   if course_select is None:
      return

   # Direct it to the course menu
   course_menu(conn, uid, course_select)


def course_menu(conn, uid, cid):
    while True:
       print("\n---- COURSE MENU ----")
       print("1. See all modules" )
       print("2. See grades")
       print("3. See Certificates")
       print("4. Go back")
      
       choice = input("Select an option: ").strip()
      
       if choice == "1":
           see_all_modules(conn, uid, cid)

       elif choice == "2":
           see_grades(conn, uid, cid)
          
       elif choice == "3":
           see_certificates(conn, uid, cid)
          
       elif choice == "4":
           break

       else:
           print("\nInvalid option. Please try again.")

def see_all_modules(conn, uid, cid):
    cur = conn.cursor()

    cur.execute("""
        SELECT mid, name, weight, summary
        FROM modules
        WHERE cid = ?;""",
        (cid, )
        )

    modules = cur.fetchall()

    if len(modules) == 0:
        print("\nNo modules found")
        return

    # Use the pagination function to get the selected mid
    mid_select = pagination(5, modules, "MODULES", print_modules, state=True)

    # check if the user even selected an mid
    if mid_select is None:
       return
    
    see_lessons(conn, uid, cid, mid_select)

def see_grades(conn, uid, cid):
    cur = conn.cursor()

    cur.execute("""
        SELECT m.mid, m.name, m.weight, g.grade, g.received_ts
        FROM modules m
        LEFT JOIN grades g ON g.mid = m.mid AND g.cid = m.cid AND g.uid = ?
        WHERE m.cid = ?
        ORDER BY m.mid
    """, (uid, cid))

    rows = cur.fetchall()

    if not rows:
        print("\nNo modules found for this course.")
        print("Final Grade: N/A")
        cur.close()
        return
    
    print(f"\n{'MID':<5} | {'Module Name':<25} | {'Weight':<8} | {'Grade':<8} | {'Date Received'}")
    border = "-" * 77
    print(border)

    total_weighted_grade = 0
    total_weight = 0

    for row in rows:
        mid, name, weight, grade, received_ts = row
        grade_str = f"{grade:<6}" if grade is not None else "N/A"
        date_str = received_ts if received_ts is not None else "N/A"
        print(f"{mid:<5} | {name:<25} | {weight:<8} | {grade_str:<8} | {date_str}")

        if grade is not None:
            total_weighted_grade += (grade * weight)
            total_weight += weight
    
    print(border)

    if total_weight > 0:
        final_grade = total_weighted_grade / total_weight
        print(f"FINAL GRADE: {final_grade:.2f}")
    else:
        print("FINAL GRADE: N/A")

    cur.close()

def see_certificates(conn, uid, cid):
    cur = conn.cursor()

    cur.execute("""
        SELECT c.cid, co.title, c.received_ts, c.final_grade
        FROM certificates c
        JOIN courses co ON c.cid = co.cid
        WHERE c.uid = ? AND c.cid = ?
    """, (uid, cid))

    row = cur.fetchone()

    if row:
        print("\n---- CERTIFICATE ----")
        print(f"\nCID:          {row[0]}")
        print(f"Course Title: {row[1]}")
        print(f"Received:     {row[2]}")
        print(f"Final Grade:  {row[3]}")
    else:
        print("\nNo certificate found for this course.")
    
    cur.close()


def view_past_payments(conn, uid):
    cur = conn.cursor()

    cur.execute("""
        SELECT p.ts, p.cid, c.title, p.credit_card_no, p.expiry_date
        FROM payments p
        LEFT OUTER JOIN courses c on c.cid = p.cid
        WHERE p.uid = ?
        ORDER BY p.ts DESC;""",
        (uid, )
    )

    payment_hist = cur.fetchall()

    if len(payment_hist) == 0:
        print("\nNo payments found ")
        return
    
    pagination(5, payment_hist, "PAST PAYMENTS", print_payment, state=False)

    cur.close()

def see_lessons(conn, uid, cid, mid_select):
    cur = conn.cursor()

    cur.execute("""
        SELECT l.lid, l.title, l.duration,
               c.ts IS NOT NULL as status,
               l.content, l.cid, l.mid
        FROM lessons l
        LEFT OUTER JOIN completion c
            ON l.cid = c.cid
            AND l.mid = c.mid
            AND l.lid = c.lid
            AND c.uid = ?
        WHERE l.cid = ? AND l.mid = ?;
    """, (uid, cid, mid_select))

    lessons = cur.fetchall()

    if len(lessons) == 0:
        print("\nNo lessons found in this module.")
        cur.close()
        return

    lid_select = pagination(5, lessons, "LESSONS", print_lessons, state=True)

    if lid_select is None:
        cur.close()
        return

    selected_lesson = None
    for lesson in lessons:
        if lesson[0] == lid_select:
            selected_lesson = lesson
            break
    
    if selected_lesson:
        lid, title, duration, status, content, cid, mid = selected_lesson

        print(f"\n--- LESSON DETAILS ---")
        print(f"\nCourse ID: {cid}")
        print(f"Module ID: {mid}")
        print(f"Lesson ID: {lid}")
        print(f"Title: {title}")
        print(f"Duration: {duration} mins")
        print(f"Status: {'Completed' if status else 'Not Completed'}")
        print(f"\nContent: \n{content}\n")

        if not status:
            choice = input("Would you like to mark this lesson as complete? (y/n): ").lower().strip()
            if choice == 'y':
                cur.execute("""
                    INSERT INTO completion (uid, cid, mid, lid, ts)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (uid, cid, mid, lid))
                conn.commit()
                print("\nLesson marked as completed.")
        else:
            print("This lesson is already completed.")
    else:
        print("Invalid lid. Returning to module menu.")
    
    cur.close()

# mask card number
def mask_card(card_num):
    if not card_num:
        return card_num
    if len(card_num) == 16 and card_num.isdigit():  # check if the card number is 16 digits and is digits only
        return '*' * 12 + card_num[-4:]
    return card_num


# ------- PAGINATION AND HELPER PRINT FUNCTIONS -----------
def pagination(page_size, result_rows, title, print_function, state):       # added a state to indicate which functions need to have a select id

    page = 0
    total_pages = (len(result_rows) + page_size - 1) // page_size    # number of pages (wrapped)

    while True:
       start = page * page_size
       end = start + page_size
       page_rows = result_rows[start:end]
       
       # get the valid ids on the current page
       valid_cid = []
       for course in page_rows:
           valid_cid.append(course[0])

       # Print the page
       print(f"\n{title}  ---- (Page {page + 1}/{total_pages})\n")

       for row in page_rows:
           print_function(row)

       # NAVIGATION

       nav_option = []      # a list where the options are going to be appended to based on the page on
    
       # pages before the last page
       if page < total_pages - 1:   
          nav_option.append("[N]ext page")
       # last page
       if page > 0:
          nav_option.append("[P]revious page")

       # append this regardless
       nav_option.append("[B]ack")
    
       # If the state is true have the option to select id if false then no
       if state:
          navigation = input(f"\n{','.join(nav_option)}, or enter id to select: ").lower().strip()      #string join
       else:
          navigation = input(f"\n{','.join(nav_option)}: ").lower().strip()

       # page navigation
       if navigation == 'n' and page < total_pages - 1:
            page += 1
       elif navigation == 'p' and page > 0:
            page -= 1
       elif navigation == 'b':
            break
       elif navigation.isdigit():       # check if the user inputted a digit to represent id
            selected_cid = int(navigation)      # turn it into int so it can be used to compared to the valid cids
            if selected_cid in valid_cid:
                return selected_cid

    if len(payment_hist) == 0:
        print("\nNo payments found ")
        return
    
    pagination(5, payment_hist, "PAST PAYMENTS", print_payment, state=False)

    cur.close()

def see_lessons(conn, uid, cid, mid_select):
    cur = conn.cursor()

    cur.execute("""
        SELECT l.lid, l.title, l.duration,
               c.ts IS NOT NULL as status,
               l.content, l.cid, l.mid
        FROM lessons l
        LEFT OUTER JOIN completion c
            ON l.cid = c.cid
            AND l.mid = c.mid
            AND l.lid = c.lid
            AND c.uid = ?
        WHERE l.cid = ? AND l.mid = ?;
    """, (uid, cid, mid_select))

    lessons = cur.fetchall()

    if len(lessons) == 0:
        print("\nNo lessons found in this module.")
        cur.close()
        return

    lid_select = pagination(5, lessons, "LESSONS", print_lessons, state=True)

    if lid_select is None:
        cur.close()
        return

    selected_lesson = None
    for lesson in lessons:
        if lesson[0] == lid_select:
            selected_lesson = lesson
            break
    
    if selected_lesson:
        lid, title, duration, status, content, cid, mid = selected_lesson

        print(f"\n--- LESSON DETAILS ---")
        print(f"\nCourse ID: {cid}")
        print(f"Module ID: {mid}")
        print(f"Lesson ID: {lid}")
        print(f"Title: {title}")
        print(f"Duration: {duration} mins")
        print(f"Status: {'Completed' if status else 'Not Completed'}")
        print(f"\nContent: \n{content}\n")

        if not status:
            choice = input("Would you like to mark this lesson as complete? (y/n): ").lower().strip()
            if choice == 'y':
                cur.execute("""
                    INSERT INTO completion (uid, cid, mid, lid, ts)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (uid, cid, mid, lid))
                conn.commit()
                print("\nLesson marked as completed.")
        else:
            print("This lesson is already completed.")
    else:
        print("Invalid lid. Returning to module menu.")
    
    cur.close()

# mask card number
def mask_card(card_num):
    if not card_num:
        return card_num
    if len(card_num) == 16 and card_num.isdigit():
        return '*' * 12 + card_num[-4:]
    return card_num


# ------- PAGINATION AND HELPER PRINT FUNCTIONS -----------
def pagination(page_size, result_rows, title, print_function, state):       # added a state to indicate which functions need to have a select id

    page = 0
    total_pages = (len(result_rows) + page_size - 1) // page_size    # number of pages (wrapped)

    while True:
       start = page * page_size
       end = start + page_size
       page_rows = result_rows[start:end]
       
       # get the valid ids on the current page
       valid_cid = []
       for course in page_rows:
           valid_cid.append(course[0])

       # Print the page
       print(f"\n{title}  ---- (Page {page + 1}/{total_pages})\n")

       for row in page_rows:
           print_function(row)

       # NAVIGATION

       nav_option = []      # a list where the options are going to be appended to based on the page on
    
       # pages before the last page
       if page < total_pages - 1:   
          nav_option.append("[N]ext page")
       # last page
       if page > 0:
          nav_option.append("[P]revious page")

       # append this regardless
       nav_option.append("[B]ack")
    
       # If the state is true have the option to select id if false then no
       if state:
          navigation = input(f"\n{','.join(nav_option)}, or enter id to select: ").lower().strip()      #string join
       else:
          navigation = input(f"\n{','.join(nav_option)}: ").lower().strip()

       # page navigation
       if navigation == 'n' and page < total_pages - 1:
            page += 1
       elif navigation == 'p' and page > 0:
            page -= 1
       elif navigation == 'b':
            break
       elif navigation.isdigit():       # check if the user inputted a digit to represent id
            selected_cid = int(navigation)      # turn it into int so it can be used to compared to the valid cids
            if selected_cid in valid_cid:
                return selected_cid
            else:
                print("Not on this page")
       else:
            print("\nInvalid option.")

#Print functions for pagination to use
def print_payment(row):
    ts, cid, title, card, expire = row
    print(f"Timestamp: {ts}")
    print(f"cid: {cid}")
    print(f"Course title: {title}")
    print(f"Card Number: {mask_card(card)}")
    print(f"Expiry date: {expire}\n")

def print_enrollment(row):
    cid, title, category, start_ts, pass_grade = row
    print(f"\ncid: {cid}")
    print(f"Course: {title}")
    print(f"Category: {category}")
    print(f"Start Timestamp: {start_ts}")
    print(f"Pass Grade: {pass_grade}")

def print_search(row):
    cid, title, description, category, price, pass_grade, max_students, current_enroll = row
    print(f"\ncid: {cid}")
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Category: {category}")
    print(f"Price: ${price:.2f}")
    print(f"Pass Grade: {pass_grade}")
    print(f"Max Students: {max_students}")
    print(f"Current Enrollment: {current_enroll}")

def print_modules(row):
    mid, name, weight, summary = row
    print(f"mid: {mid}")
    print(f"Name: {name}")
    print(f"Weight: {weight}")
    print(f"Summary: {summary}\n")    

def print_lessons(row):
    lid, title, duration, status, content, cid, mid = row
    print(f"lid: {lid}")
    print(f"Title: {title}")
    print(f"Duration: {duration}")
    print(f"Status: {'Completed' if status else 'Not Completed'}\n")
