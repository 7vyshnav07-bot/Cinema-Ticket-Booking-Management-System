# 🎬 CineBook – Cinema Ticket Booking Management System

CineBook is a web-based Cinema Ticket Booking Management System developed using Python, Flask, MySQL, HTML, CSS, and JavaScript. It provides a platform for customers to browse movies, view available showtimes, select seats, and book cinema tickets online.

The system also provides an administrative interface to manage movies, theatres, screens, seats, shows, and booking records. It uses a centralised MySQL database to maintain and organise cinema-related information.

## 🚀 Features

### 👤 Customer Features
- **User Registration and Login** – Create an account and securely access the application.
- **Movie Browsing** – Explore available movies and their details.
- **Showtime Selection** – View available movie screenings and select a suitable show.
- **Seat Selection** – Choose seats for a particular movie show.
- **Ticket Booking** – Reserve selected seats and generate booking records.
- **Booking History** – View previous and current reservations.
- **Profile Management** – Access personal account information.

### 🛠️ Admin Features
- **Admin Dashboard** – Centralised interface for managing cinema operations.
- **Movie Management** – Add, view, and update movie information.
- **Theatre Management** – Manage theatre details.
- **Screen Management** – Manage screens within theatres.
- **Seat Management** – Maintain seat information.
- **Show Management** – Manage movie schedules and ticket prices.
- **Booking Management** – View and manage customer booking records.
- **Payment Records** – Access payment-related information.

### 🗄️ Database Features
- Relational database design using MySQL.
- Primary key and foreign key relationships.
- Normalisation of database tables.
- SQL joins, subqueries, and aggregate functions.
- Views, stored functions, and stored procedures.
- Transaction handling and data integrity validation.

## 💻 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| MySQL | Database management |
| HTML5 | Frontend structure |
| CSS3 | Styling and layout |
| JavaScript | Frontend interactivity |
| Jinja | Dynamic HTML templating |
| Git & GitHub | Version control |

## 🗂️ Database Structure

CineBook uses a relational MySQL database consisting of the following main tables:

| Table | Description |
|---|---|
| `users` | Customer and administrator information |
| `movies` | Movie details |
| `theatres` | Theatre information |
| `screens` | Screen details |
| `seats` | Seat information |
| `shows` | Movie show schedules |
| `bookings` | Customer booking records |
| `booking_details` | Individual seats associated with bookings |
| `payments` | Payment-related records |

## 📁 Project Structure

The project is organised into backend components, frontend templates, static resources, and database-related files.

```text
Cinema-Ticket-Booking-Management-System/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── database/
│   └── cinebook.sql
│
└── ...
```

*Note: This is a representative structure. Refer to the actual project folders and filenames when organising the repository.*

## ⚙️ Installation and Setup

Follow these steps to run CineBook locally.

### 1. Clone the Repository

```bash
git clone https://github.com/7vyshnav07-bot/Cinema-Ticket-Booking-Management-System.git
```

### 2. Navigate to the Project Directory

```bash
cd Cinema-Ticket-Booking-Management-System
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure MySQL Database

- Install and start MySQL Server.
- Create the CineBook database.
- Import the provided SQL database script, if included.
- Configure the database connection settings in the application.
- Update the database credentials using your local configuration.

Do not upload database passwords or secret credentials to GitHub.

### 6. Run the Application

If the main Flask application file is `app.py`, execute:

```bash
python app.py
```

If your project uses a different entry-point file, run that file instead.

### 7. Open in Browser

Access the application using the local address displayed by Flask, commonly:

```text
http://127.0.0.1:5000/
```

## 🔐 Security Considerations

- Authentication is used to manage customer access.
- Sessions help maintain logged-in user information.
- Role-based access separates customer and administrator functionality.
- Database operations should use parameterised queries.
- Sensitive configuration values should be stored outside the public source code.

## 🔮 Future Enhancements

- Online payment gateway integration.
- QR-code-based digital ticket generation.
- Email and SMS booking notifications.
- Online booking cancellation and refunds.
- Real-time seat availability updates.
- Movie ratings and reviews.
- Discount coupons and loyalty programs.
- Mobile application development.
- Advanced booking analytics and reports.
- Cloud deployment and support for multiple cinema locations.

## 🎯 Project Objective

The main objective of CineBook is to simplify cinema ticket booking and management through a centralised web application. It aims to reduce manual booking activities, improve accessibility, organise cinema information, and provide a convenient reservation experience for customers.

## 👨‍💻 Developer

**Vyshnav Manoharan**

- GitHub: [@7vyshnav07-bot](https://github.com/7vyshnav07-bot)
- Project: [Cinema Ticket Booking Management System](https://github.com/7vyshnav07-bot/Cinema-Ticket-Booking-Management-System)

## 📄 License

This project was developed for academic purposes. You may add an appropriate open-source license if you intend to distribute or reuse the source code.

---

⭐ If you find this project interesting, consider giving the repository a star!
