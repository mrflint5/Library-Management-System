import streamlit as st
import library_utils as lib

lib.connect_db()

st.set_page_config(page_title="Gurukul Library", page_icon="📚", layout="centered")
st.title("📚 Gurukul Library Management System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------- LOGIN PAGE --------------------
if not st.session_state.logged_in:
    st.subheader("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if lib.login_admin(username, password):
            st.session_state.logged_in = True
            st.success("✅ Logged in!")
        else:
            st.error("❌ Invalid credentials")

    st.info("Don't have an account?")
    with st.expander("Register New Admin"):
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if lib.register_admin(new_user, new_pass):
                st.success("✅ Registered! Now login.")
            else:
                st.error("❌ Username already exists.")

# ------------------- MAIN APP --------------------
else:
    menu = st.sidebar.selectbox("📖 Select Action", [
        "Add Book", "Add Student", "Issue Book", "Return Book", "View All", "Export to Excel", "Logout"
    ])

    if menu == "Add Book":
        st.subheader("➕ Add Book")
        title = st.text_input("Book Title")
        author = st.text_input("Author Name")
        if st.button("Add Book"):
            lib.add_book(title, author)
            st.success("✅ Book Added!")

    elif menu == "Add Student":
        st.subheader("🎓 Register Student")
        name = st.text_input("Student Name")
        if st.button("Add Student"):
            lib.add_student(name)
            st.success("✅ Student Registered!")

    elif menu == "Issue Book":
        st.subheader("📤 Issue Book")
        books = lib.get_books()
        students = lib.get_students()
        book = st.selectbox("Choose Book", [(b[0], b[1]) for b in books if b[3] == 1])
        student = st.selectbox("To Student", [(s[0], s[1]) for s in students])
        if st.button("Issue"):
            msg = lib.issue_book(book[0], student[0])
            st.info(msg)

    elif menu == "Return Book":
        st.subheader("📥 Return Book")
        students = lib.get_students()
        with_books = [(s[0], s[1]) for s in students if s[2]]
        student = st.selectbox("Select Student", with_books)
        if st.button("Return"):
            msg = lib.return_book(student[0])
            st.success(msg)

    elif menu == "View All":
        st.subheader("📚 All Books")
        st.dataframe(lib.get_books())
        st.subheader("🎓 All Students")
        st.dataframe(lib.get_students())

    elif menu == "Export to Excel":
        if st.button("Export Now"):
            msg = lib.export_data()
            st.success(msg)

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.experimental_rerun()
