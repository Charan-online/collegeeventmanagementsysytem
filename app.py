import streamlit as st
import pyodbc
import pandas as pd

# ---------------- DATABASE CONNECTION ----------------
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-J9K8KE6H;"
    "DATABASE=EventManagementSystem;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# ---------------- PAGE TITLE ----------------
st.title("College Event Management System")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.name = ""
    st.session_state.role = ""

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        query = """
        SELECT Users.UserID, Users.Name, Roles.RoleName
        FROM Users
        JOIN Roles ON Users.RoleID = Roles.RoleID
        WHERE Username=? AND Password=?
        """
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.name = user[1]
            st.session_state.role = user[2]
            st.rerun()
        else:
            st.error("Invalid username or password")

# ---------------- AFTER LOGIN ----------------
else:
    st.sidebar.success(f"Logged in as {st.session_state.name}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ====================== ADMIN PANEL ======================
    if st.session_state.role == "Admin":
        st.sidebar.title("Admin Dashboard")
        menu = st.sidebar.selectbox(
            "Menu",
            ["Dashboard","Create Event","View Events","Modify Event","Delete Event",
             "Assign Faculty Coordinator","View Faculty Coordinators","View Registrations",
             "Participation Analytics"]
        )

        if menu=="Dashboard":
            st.header("Dashboard")
            total_events = pd.read_sql("SELECT COUNT(*) AS Total FROM Events", conn).iloc[0]["Total"]
            total_users = pd.read_sql("SELECT COUNT(*) AS Total FROM Users", conn).iloc[0]["Total"]
            total_regs = pd.read_sql("SELECT COUNT(*) AS Total FROM Registrations", conn).iloc[0]["Total"]
            st.write("Total Events:", total_events)
            st.write("Total Users:", total_users)
            st.write("Total Registrations:", total_regs)

        elif menu=="Create Event":
            st.header("Create Event")
            name = st.text_input("Event Name")
            date = st.date_input("Event Date")
            location = st.text_input("Location")
            desc = st.text_area("Description")
            participation = st.selectbox("Participation Type", ["Solo","Duo","Team","None"])
            if st.button("Create Event"):
                cursor.execute(
                    "INSERT INTO Events (EventName, EventDate, Location, Description, ParticipationType) VALUES (?,?,?,?,?)",
                    (name, date, location, desc, participation)
                )
                conn.commit()
                st.success("Event Created Successfully")

        elif menu=="View Events":
            st.header("All Events")
            df = pd.read_sql("SELECT EventName, EventDate, Location, ParticipationType FROM Events", conn)
            search = st.text_input("Search Event")
            if search: df = df[df["EventName"].str.contains(search, case=False)]
            st.dataframe(df, use_container_width=True)

        elif menu=="Modify Event":
            st.header("Modify Event")
            events = pd.read_sql("SELECT EventID, EventName FROM Events", conn)
            event_name = st.selectbox("Select Event", events["EventName"])
            selected = events[events["EventName"]==event_name]
            event_id = int(selected.iloc[0]["EventID"])
            event_data = pd.read_sql("SELECT EventName, EventDate, Location, Description, ParticipationType FROM Events WHERE EventID=?",
                                     conn, params=[event_id]).iloc[0]
            new_name = st.text_input("Event Name", event_data["EventName"])
            new_date = st.date_input("Event Date", event_data["EventDate"])
            new_location = st.text_input("Location", event_data["Location"])
            new_desc = st.text_area("Description", event_data["Description"])
            new_participation = st.selectbox("Participation Type", ["Solo","Duo","Team","None"],
                                             index=["Solo","Duo","Team","None"].index(event_data["ParticipationType"]))
            if st.button("Update Event"):
                cursor.execute(
                    "UPDATE Events SET EventName=?, EventDate=?, Location=?, Description=?, ParticipationType=? WHERE EventID=?",
                    (new_name,new_date,new_location,new_desc,new_participation,event_id)
                )
                conn.commit()
                st.success("Event Updated Successfully")

        elif menu=="Delete Event":
            st.header("Delete Event")
            events = pd.read_sql("SELECT EventID, EventName FROM Events", conn)
            event_name = st.selectbox("Select Event to Delete", events["EventName"])
            event_id = int(events[events["EventName"]==event_name]["EventID"].values[0])
            if st.button("Delete"):
                cursor.execute("DELETE FROM Events WHERE EventID=?", (event_id,))
                conn.commit()
                st.success("Event Deleted Successfully")

        elif menu=="Assign Faculty Coordinator":
            st.header("Assign Faculty Coordinator")
            events = pd.read_sql("SELECT EventID, EventName FROM Events", conn)
            faculty = pd.read_sql("SELECT Users.UserID, Users.Name FROM Users JOIN Roles ON Users.RoleID=Roles.RoleID WHERE Roles.RoleName='Faculty'", conn)
            event_name = st.selectbox("Select Event", events["EventName"])
            event_id = int(events[events["EventName"]==event_name]["EventID"].values[0])
            faculty_name = st.selectbox("Select Faculty", faculty["Name"])
            faculty_id = int(faculty[faculty["Name"]==faculty_name]["UserID"].values[0])
            if st.button("Assign"):
                cursor.execute("INSERT INTO FacultyCoordinators (EventID, FacultyID, AssignedDate) VALUES (?,?,GETDATE())",
                               (event_id, faculty_id))
                conn.commit()
                st.success("Faculty Assigned Successfully")

        elif menu=="View Faculty Coordinators":
            st.header("Faculty Coordinators")
            query = """
            SELECT Events.EventName, Users.Name AS Faculty, FacultyCoordinators.AssignedDate
            FROM FacultyCoordinators
            JOIN Events ON FacultyCoordinators.EventID=Events.EventID
            JOIN Users ON FacultyCoordinators.FacultyID=Users.UserID
            """
            df = pd.read_sql(query, conn)
            st.dataframe(df, use_container_width=True)

        elif menu=="View Registrations":
            st.header("Event Registrations")
            query = """
            SELECT Users.Name, Users.Department, Users.Year, Events.EventName, Registrations.ParticipationType, Registrations.RegistrationDate
            FROM Registrations
            JOIN Users ON Registrations.StudentID = Users.UserID
            JOIN Events ON Registrations.EventID = Events.EventID
            ORDER BY Users.Department, Users.Year
            """
            df = pd.read_sql(query, conn)
            st.dataframe(df, use_container_width=True)

        elif menu=="Participation Analytics":
            st.header("Branch Wise Participation")
            query = "SELECT Users.Department, COUNT(*) AS Total FROM Registrations JOIN Users ON Registrations.StudentID=Users.UserID GROUP BY Users.Department"
            df = pd.read_sql(query, conn)
            st.bar_chart(df.set_index("Department"))

# ====================== STUDENT PANEL ======================
    elif st.session_state.role=="Student":
        st.sidebar.title("Student Dashboard")
        menu = st.sidebar.selectbox("Menu", ["View Events","Register Event","My Registrations","Cancel Registration"])

        if menu=="View Events":
            st.header("Available Events")
            df = pd.read_sql("SELECT EventName, EventDate, Location, ParticipationType FROM Events", conn)
            search = st.text_input("Search Event")
            if search: df = df[df["EventName"].str.contains(search, case=False)]
            st.dataframe(df, use_container_width=True)

        elif menu=="Register Event":
            st.header("Register Event")
            events = pd.read_sql("SELECT EventID, EventName, ParticipationType FROM Events", conn)
            event_name = st.selectbox("Select Event", events["EventName"])
            selected = events[events["EventName"]==event_name]
            event_id = int(selected.iloc[0]["EventID"])
            ptype = selected.iloc[0]["ParticipationType"]

            # Determine participation type
            if ptype=="None":
                participation = st.selectbox("Choose Participation", ["Solo","Duo","Team"])
            else:
                participation = ptype
                st.write("Participation Type:", participation)

            teammate_names = []
            teammate_emails = []

            # Duo registration
            if participation=="Duo":
                st.subheader("Add Your Partner")
                partner_name = st.text_input("Partner Name")
                partner_email = st.text_input("Partner Email")
                if partner_name and partner_email:
                    teammate_names.append(partner_name)
                    teammate_emails.append(partner_email)

            # Team registration (max 4 members including student)
            elif participation=="Team":
                st.subheader("Add Teammates (max 3 teammates)")
                num_teammates = st.number_input("Number of Teammates (excluding you)", min_value=1, max_value=3, step=1)
                for i in range(num_teammates):
                    name = st.text_input(f"Teammate {i+1} Name")
                    email = st.text_input(f"Teammate {i+1} Email")
                    teammate_names.append(name)
                    teammate_emails.append(email)

            if st.button("Register"):
                cursor.execute(
                    "INSERT INTO Registrations (StudentID, EventID, ParticipationType, RegistrationDate) VALUES (?,?,?,GETDATE())",
                    (st.session_state.user_id, event_id, participation)
                )
                conn.commit()

                reg_id = cursor.execute("SELECT MAX(RegistrationID) FROM Registrations").fetchval()

                for i in range(len(teammate_names)):
                    if teammate_names[i] and teammate_emails[i]:
                        cursor.execute(
                            "INSERT INTO TeamMembers (RegistrationID, StudentName, StudentEmail) VALUES (?,?,?)",
                            (reg_id, teammate_names[i], teammate_emails[i])
                        )
                conn.commit()
                st.success("Registered Successfully")

        elif menu=="My Registrations":
            st.header("My Registrations")
            df = pd.read_sql("""
                SELECT R.RegistrationID, E.EventName, R.ParticipationType, R.RegistrationDate
                FROM Registrations R
                JOIN Events E ON R.EventID = E.EventID
                WHERE R.StudentID=?
            """, conn, params=[st.session_state.user_id])
            st.dataframe(df, use_container_width=True)

            # Show teammates
            for idx, row in df.iterrows():
                if row["ParticipationType"] in ["Duo","Team"]:
                    tm_df = pd.read_sql("SELECT StudentName, StudentEmail FROM TeamMembers WHERE RegistrationID=?",
                                        conn, params=[row["RegistrationID"]])
                    if not tm_df.empty:
                        st.write(f"Teammates for {row['EventName']}:")
                        st.dataframe(tm_df)

        elif menu=="Cancel Registration":
            st.header("Cancel Registration")
            df = pd.read_sql("SELECT Registrations.RegistrationID, Events.EventName FROM Registrations JOIN Events ON Registrations.EventID=Events.EventID WHERE Registrations.StudentID=?",
                             conn, params=[st.session_state.user_id])
            st.dataframe(df)
            reg_id = st.number_input("Enter Registration ID", step=1)
            if st.button("Cancel"):
                cursor.execute("DELETE FROM Registrations WHERE RegistrationID=?", (reg_id,))
                cursor.execute("DELETE FROM TeamMembers WHERE RegistrationID=?", (reg_id,))
                conn.commit()
                st.success("Registration Cancelled")

# ====================== FACULTY PANEL ======================
    elif st.session_state.role=="Faculty":
        st.sidebar.title("Faculty Dashboard")
        menu = st.sidebar.selectbox("Menu", ["View Events","View Student Registrations","My Coordinated Events"])

        if menu=="View Events":
            st.header("All Events")
            df = pd.read_sql("SELECT EventName, EventDate, Location, ParticipationType FROM Events", conn)
            search = st.text_input("Search Event")
            if search: df = df[df["EventName"].str.contains(search, case=False)]
            st.dataframe(df, use_container_width=True)

        elif menu=="View Student Registrations":
            st.header("Student Registrations")
            df = pd.read_sql("""
                SELECT Users.Name, Users.Department, Users.Year, Events.EventName, Registrations.ParticipationType
                FROM Registrations
                JOIN Users ON Registrations.StudentID = Users.UserID
                JOIN Events ON Registrations.EventID = Events.EventID
                ORDER BY Users.Department, Users.Year
            """, conn)
            st.dataframe(df, use_container_width=True)

        elif menu=="My Coordinated Events":
            st.header("Events I Coordinate")
            events = pd.read_sql("SELECT Events.EventID, Events.EventName FROM FacultyCoordinators JOIN Events ON FacultyCoordinators.EventID=Events.EventID WHERE FacultyCoordinators.FacultyID=?", conn, params=[st.session_state.user_id])
            if events.empty: st.warning("You are not assigned to any event.")
            else:
                event_name = st.selectbox("Select Event", events["EventName"])
                selected = events[events["EventName"]==event_name]
                event_id = int(selected.iloc[0]["EventID"])
                df = pd.read_sql("SELECT Users.Name, Users.Department, Users.Year, Registrations.ParticipationType FROM Registrations JOIN Users ON Registrations.StudentID=Users.UserID WHERE Registrations.EventID=?",
                                 conn, params=[event_id])
                st.subheader("Participating Students")
                st.dataframe(df, use_container_width=True)