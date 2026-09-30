from database import get_connection

events = [
    (
        "Chennai Tech Summit 2026",
        "Technology",
        "A technology summit covering artificial intelligence, cloud computing, cybersecurity and emerging digital technologies.",
        "2026-10-24",
        "10:00 AM",
        "Chennai Trade Centre",
        300,
        247
    ),

    (
        "CodeCraft Hackathon 2026",
        "Hackathon",
        "A 24-hour student hackathon where participants develop innovative solutions using modern technologies.",
        "2026-11-12",
        "9:00 AM",
        "Anna University Innovation Centre",
        120,
        76
    ),

    (
        "Python for Beginners Workshop",
        "Workshop",
        "A hands-on Python workshop covering programming fundamentals, functions, data structures and mini projects.",
        "2026-11-18",
        "10:00 AM",
        "Tidel Park Training Hall",
        60,
        18
    ),

    (
        "Future of AI Conference",
        "Conference",
        "Industry professionals and technology enthusiasts discuss artificial intelligence, automation and the future of work.",
        "2026-11-25",
        "9:30 AM",
        "Chennai Convention Centre",
        200,
        91
    ),

    (
        "Chennai Cultural Fest 2026",
        "Cultural",
        "A celebration of music, dance, theatre and traditional arts featuring performances by students and local artists.",
        "2026-12-05",
        "5:00 PM",
        "City Arts Auditorium",
        500,
        326
    ),

    (
        "Startup Connect Chennai",
        "Business",
        "An evening networking event connecting aspiring entrepreneurs, startup founders, mentors and technology professionals.",
        "2026-12-12",
        "2:00 PM",
        "Chennai Innovation Hub",
        100,
        42
    ),

    (
        "Future Developers Meetup",
        "Technology",
        "Connect with developers and technology enthusiasts to discuss software development, APIs, open-source projects and career opportunities.",
        "2026-12-19",
        "11:00 AM",
        "Tech Community Hall",
        150,
        83
    ),

    (
        "Design Thinking Workshop",
        "Workshop",
        "Learn practical design thinking techniques for understanding users, generating ideas and building better solutions.",
        "2027-01-09",
        "10:30 AM",
        "Innovation Studio Chennai",
        80,
        29
    )
]

connection = get_connection()

for event in events:
    connection.execute("""
        INSERT INTO events
        (name, category, description, date, time, venue, capacity, available_seats)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, event)

connection.commit()
connection.close()

print("Realistic sample events added successfully!")