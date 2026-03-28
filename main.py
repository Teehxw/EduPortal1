import sqlite3
import login
import student
import admin 
import instructor
import sys

# ------- CONNECT TO THE DATABASE ------- #

def setup_db():
    """
    Creating all the tables
    """
    global conn, cur

    #Connect to the database 
    conn = sqlite3.connect("portal_db")
    cur = conn.cursor()

    #Drop tables if they exist
    cur.execute("DROP TABLE IF EXISTS payments;")
    cur.execute("DROP TABLE IF EXISTS certificates;")
    cur.execute("DROP TABLE IF EXISTS grades;")
    cur.execute("DROP TABLE IF EXISTS completion;")
    cur.execute("DROP TABLE IF EXISTS lessons;")
    cur.execute("DROP TABLE IF EXISTS modules;")
    cur.execute("DROP TABLE IF EXISTS enrollments;")
    cur.execute("DROP TABLE IF EXISTS courses;")
    cur.execute("DROP TABLE IF EXISTS users;")
    
    #Create the 'Users' Table
    cur.execute("""
        CREATE TABLE users (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL CHECK(role IN ('Student', 'Instructor', 'Admin')),
        pwd TEXT NOT NULL
);
    """)
    #Create the 'Courses' Table
    cur.execute("""
        CREATE TABLE courses (
        cid INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL NOT NULL CHECK(price >= 0),
        pass_grade REAL NOT NULL CHECK(pass_grade >= 0 AND pass_grade <= 100),
        max_students INTEGER NOT NULL CHECK(max_students > 0)
);
    """)
    #Create the 'Enrollments' Table
    cur.execute("""
        CREATE TABLE enrollments (
        cid INTEGER NOT NULL,
        uid INTEGER NOT NULL,
        start_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        end_ts TIMESTAMP NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Student', 'Instructor')),
        PRIMARY KEY (cid, uid, start_ts),
        FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE,
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);
    """)

    #Create the 'Modules' Table
    cur.execute("""
        CREATE TABLE modules (
        cid INTEGER NOT NULL,
        mid INTEGER NOT NULL,
        name TEXT NOT NULL,
        summary TEXT,
        weight REAL NOT NULL CHECK(weight >= 0),
        PRIMARY KEY (cid, mid),
        FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE
    );
    """)

    #Create the 'Lessons' Table
    cur.execute("""
        CREATE TABLE lessons (
        cid INTEGER NOT NULL,
        mid INTEGER NOT NULL,
        lid INTEGER NOT NULL,
        title TEXT NOT NULL,
        duration INTEGER NOT NULL CHECK(duration >= 0),
        content TEXT,
        PRIMARY KEY (cid, mid, lid),
        FOREIGN KEY (cid, mid) REFERENCES modules(cid, mid) ON DELETE CASCADE
);
    """)

    #Create the 'Completion' Table
    cur.execute("""
        CREATE TABLE completion (
        uid INTEGER NOT NULL,
        cid INTEGER NOT NULL,
        mid INTEGER NOT NULL,
        lid INTEGER NOT NULL,
        ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (uid, cid, mid, lid, ts),
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
        FOREIGN KEY (cid, mid, lid) REFERENCES lessons(cid, mid, lid) ON DELETE CASCADE
    );
    """)

    #Create the 'Grades' Table
    cur.execute("""
        CREATE TABLE grades (
        uid INTEGER NOT NULL,
        cid INTEGER NOT NULL,
        mid INTEGER NOT NULL,
        received_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        grade REAL NOT NULL CHECK(grade >= 0 AND grade <= 100),
        PRIMARY KEY (uid, cid, mid, received_ts),
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
        FOREIGN KEY (cid, mid) REFERENCES modules(cid, mid) ON DELETE CASCADE
    );
    """)

    #Create the 'Certificates' Table
    cur.execute("""
        CREATE TABLE certificates (
        cid INTEGER NOT NULL,
        uid INTEGER NOT NULL,
        received_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        final_grade REAL NOT NULL CHECK(final_grade >= 0 AND final_grade <= 100),
        PRIMARY KEY (cid, uid, received_ts),
        FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE,
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
    );
    
    """)

    #Create the 'Payments' Table
    cur.execute("""
        CREATE TABLE payments (
        uid INTEGER NOT NULL,
        cid INTEGER NOT NULL,
        ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        credit_card_no TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        PRIMARY KEY (uid, cid, ts),
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
        FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE
    );
    """)

    conn.commit()
    print("Tables created successfully!")


#----MAIN LOGIN LOOP -----#
def login_menu(conn):
    # while loop for menu
    while True:
        print("\n**** WELCOME ****\n")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        user_choice = input("\nSelect Option 1-3: ")

        # Choice 1
        if user_choice == "1":
            user = login.login(conn)
            if user != None:
                uid, role, name = user

                #--- Role functionalities ---
                if role == "Student":
                    student.student_functionalities(conn, uid, name)
                if role == "Instructor":
                    instructor.instructor_functionalities(conn, uid, name)
                if role == "Admin":
                    admin.admin_functionalities(conn, uid, name)

        elif user_choice == "2":
            login.register(conn)
        
        elif user_choice == "3":
            print("\nSee you next time!")
            conn.close()
            break
        
        else:
            print("\nInvalid option. Please use valid option")


# SET UP MAIN FOR TESTING THE PROGRAM
def main():
    if len(sys.argv) < 2:  
        print("Usage: python main.py <sql_file>")
        exit(1)    

    sql_file = sys.argv[1]

    # Connect to the database
    conn = sqlite3.connect("portal_db")

    setup_db()

    # Load and execute the SQL file
    with open(sql_file, 'r') as file:
        sql = file.read()
    
    conn.executescript(sql)
    conn.commit()
    print("Data loaded successfully!")
    
    # Start login loop
    login_menu(conn)

    # Close connection when program exits
    conn.close()

if __name__ == "__main__":
    main()
