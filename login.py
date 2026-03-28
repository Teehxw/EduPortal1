import getpass
import sqlite3

def login(conn):
    cur = conn.cursor()

    #Print the login screen
    print("\n---- LOGIN ----\n")

    #Get the user and password input
    # Use try-except to handle the case where the user enters a non-integer 
    while True:
        try:
            uid = int(input("Enter User Id: "))
            break
        except ValueError:
            print("\nInvalid user ID. Please enter a number.\n")
            

    password = getpass.getpass(prompt = "Enter Password: ")     #Masks the password

    cur.execute("""
        SELECT uid, role, name
        FROM users
        WHERE uid = ? AND pwd = ?;""",
        (uid, password)
        )

    result = cur.fetchone()     # returns (uid, role, name)

    if result != None:
        print("\nLOGIN SUCCESSFUL!")
        return result
    else:
        print("\nInvalid username or password. Try again")
        return None     

#---- REGISTER ----
def register(conn):
    cur = conn.cursor()

    #Print the Register Screen
    print("\n---- REGISTER ----\n")

    #Get the user input for name, email address, password
    reg_name = input("Enter first and last name:  ")
    reg_email = input("Enter email address: ")
    reg_pass = input("Create a password: ")

    # Now we have to check if the email is in use or not
    cur.execute("""
        SELECT *
        FROM users
        WHERE email = ?;""",
        (reg_email, )
        )

    if cur.fetchone() != None:
        print("\nEmail already in use. Please Try a different email")
        return None
    
    # Now we have to insert these values into the table. The role is automatically set to 'Student' and a unqiue id is generated
    role = 'Student'
    cur.execute("""
        INSERT INTO users (name, email, role, pwd)
        VALUES (?,?,?,?);""",
        (reg_name, reg_email, role, reg_pass)
    )

    conn.commit()

    # Now generate the unqiue id for the new user
    new_userid = cur.lastrowid   #this gets the ID of the most recent inserted row 

    #Let the user know that the registration was successful
    print(f"\nYour registration was successful! Your unique id is: {new_userid}")
    return new_userid   #return the new user id 
