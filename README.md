College Event Management System
A multi-role web application built with Streamlit and SQL Server to manage college event registrations, coordination, and analytics. The system provides tailored dashboards for Administrators, Students, and Faculty members.

🚀 Features
1. Admin Dashboard
Event Lifecycle Management: Create, update, and delete events.

Faculty Assignment: Assign specific faculty members as coordinators for events.

Registrations Overview: View and export student registration details.

Analytics: Branch-wise participation visualization using interactive bar charts.

2. Student Portal
Event Discovery: Browse available events with search functionality.

Flexible Registration: Support for Solo, Duo (with partner details), and Team (up to 4 members) registrations.

Personal Dashboard: View "My Registrations" and manage/cancel existing sign-ups.

3. Faculty Panel
Coordination Tools: Access a dedicated list of students registered for events they are coordinating.

Student Tracking: View student details including department and year of study.

🛠️ Tech Stack
Frontend: Streamlit (Python-based web framework)

Language: Python 3.x

Database: Microsoft SQL Server

Libraries: * pandas (Data manipulation and SQL querying)

pyodbc (Database connectivity)

📋 Prerequisites
Before running the application, ensure you have the following installed:

ODBC Driver 17 for SQL Server

Python 3.8+

A running SQL Server instance with a database named EventManagementSystem.

⚙️ Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/Charan-online/collegeeventmanagementsysytem.git
cd collegeeventmanagementsysytem
Install Dependencies:

Bash
pip install streamlit pyodbc pandas
Database Configuration:
Open app.py and update the connection string with your server details:

Python
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=YOUR_SERVER_NAME;"  # e.g., LAPTOP-J9K8KE6H
    "DATABASE=EventManagementSystem;"
    "Trusted_Connection=yes;"
)
Run the App:

Bash
streamlit run app.py
🗄️ Database Schema Requirement
The system expects the following tables to exist in your SQL Server:

Users & Roles (For authentication)

Events (Event details and participation types)

Registrations (Student-event mapping)

TeamMembers (Details for Duo/Team registrations)

FacultyCoordinators (Faculty-event mapping)

Note: This project uses st.session_state for session management and st.rerun() for seamless navigation between the login screen and user dashboards.
