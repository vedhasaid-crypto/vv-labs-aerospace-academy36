
import os
import sqlite3
import secrets
from functools import wraps
from hashlib import sha256
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, request, redirect, url_for, session,
    flash, render_template_string, abort
)

# ============================================================
# VV LAB'S | AEROSPACE ACADEMY
# Completely free aerospace learning platform
# Made by VV Lab's
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "aerospace_academy.db")

app = Flask(__name__)
app.secret_key = os.environ.get(
    "AEROSPACE_SECRET_KEY", secrets.token_hex(32)
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ------------------------- LESSON DATA -------------------------

LESSONS = [
    {
        "id": 1,
        "title": "The World of Aviation",
        "category": "AVIATION",
        "icon": "✈",
        "level": "Beginner",
        "duration": "8 min",
        "intro": "Discover how aircraft fly and how pilots navigate the skies.",
        "sections": [
            ("How does an airplane fly?",
             "An airplane flies through the interaction of four main forces: lift, weight, thrust, and drag. "
             "Wings are designed to produce lift as air flows around them. Engines provide thrust, while "
             "gravity pulls the aircraft downward and drag resists its movement."),
            ("The four forces",
             "Lift acts upward, weight acts downward, thrust pushes an aircraft forward, and drag acts "
             "against its motion. During steady, level flight, lift approximately balances weight and thrust "
             "balances drag."),
            ("Aircraft navigation",
             "Pilots use instruments, radio communication, navigation systems, weather reports, and "
             "air traffic control to plan and conduct flights safely.")
        ],
        "questions": [
            {
                "q": "Which force primarily opposes an aircraft's forward motion?",
                "options": ["Lift", "Drag", "Weight", "Gravity"],
                "answer": 1,
                "explanation": "Drag resists movement through the air."
            },
            {
                "q": "Which part of an airplane is mainly designed to generate lift?",
                "options": ["Wings", "Landing lights", "Tail number", "Cabin seats"],
                "answer": 0,
                "explanation": "The wings generate most of an airplane's lift."
            },
            {
                "q": "What helps pilots navigate and monitor a flight?",
                "options": ["Only the windows", "Navigation systems and instruments",
                            "Passenger seats", "Paint colour"],
                "answer": 1,
                "explanation": "Pilots combine instruments, navigation systems, communication, and other information."
            }
        ]
    },
    {
        "id": 2,
        "title": "Rocket Science",
        "category": "ROCKETRY",
        "icon": "🚀",
        "level": "Beginner",
        "duration": "10 min",
        "intro": "Explore rocket engines, thrust, stages, and orbital launches.",
        "sections": [
            ("How rockets move",
             "Rockets produce thrust by expelling exhaust at high speed. Newton's third law describes "
             "the equal and opposite reaction: the exhaust moves one way while the rocket is pushed the other way."),
            ("Rocket stages",
             "Many launch vehicles use multiple stages. Once a stage has used its propellant, it can be "
             "separated so the remaining vehicle does not have to accelerate that empty structure."),
            ("Reaching orbit",
             "Getting into orbit requires enormous horizontal speed as well as altitude. An orbiting "
             "spacecraft is continuously falling toward Earth while moving sideways fast enough to keep missing it.")
        ],
        "questions": [
            {
                "q": "What produces the thrust of a rocket?",
                "options": ["Wings", "Expelled exhaust", "Solar panels alone", "Airplane propellers"],
                "answer": 1,
                "explanation": "A rocket gains thrust by expelling mass in the opposite direction."
            },
            {
                "q": "Why do many rockets use multiple stages?",
                "options": ["To carry empty tanks forever", "To reduce unnecessary mass",
                            "To eliminate gravity", "To stop producing thrust"],
                "answer": 1,
                "explanation": "Dropping spent stages reduces the mass the remaining rocket must accelerate."
            },
            {
                "q": "What is important for reaching orbit?",
                "options": ["Altitude alone", "Horizontal orbital speed as well as altitude",
                            "Colour of the rocket", "A runway"],
                "answer": 1,
                "explanation": "Orbit requires sufficient sideways velocity, not just height."
            }
        ]
    },
    {
        "id": 3,
        "title": "Exploring the Planets",
        "category": "PLANETARY SCIENCE",
        "icon": "🪐",
        "level": "Beginner",
        "duration": "9 min",
        "intro": "Tour the planets and compare rocky worlds with giant planets.",
        "sections": [
            ("Our solar system",
             "The solar system has eight recognised planets. Mercury, Venus, Earth, and Mars are rocky "
             "planets. Jupiter and Saturn are gas giants, while Uranus and Neptune are ice giants."),
            ("Worlds of extremes",
             "Venus has an extremely hot surface because of its dense atmosphere and strong greenhouse effect. "
             "Jupiter is the largest planet, while Saturn is famous for its extensive ring system."),
            ("Searching for life",
             "Scientists study planetary atmospheres, surface chemistry, water, and geological history to "
             "understand whether a world could support life. Evidence of habitability is not the same as proof of life.")
        ],
        "questions": [
            {
                "q": "How many planets are recognised in our solar system?",
                "options": ["Seven", "Eight", "Nine", "Twelve"],
                "answer": 1,
                "explanation": "The solar system has eight recognised planets."
            },
            {
                "q": "Which is the largest planet?",
                "options": ["Earth", "Mars", "Jupiter", "Venus"],
                "answer": 2,
                "explanation": "Jupiter is the largest planet in our solar system."
            },
            {
                "q": "Which planet is famous for its prominent rings?",
                "options": ["Saturn", "Mercury", "Mars", "Earth"],
                "answer": 0,
                "explanation": "Saturn has a particularly extensive and visible ring system."
            }
        ]
    },
    {
        "id": 4,
        "title": "Astronaut Training",
        "category": "HUMAN SPACEFLIGHT",
        "icon": "👨‍🚀",
        "level": "Beginner",
        "duration": "8 min",
        "intro": "Learn how astronauts prepare for life and work in space.",
        "sections": [
            ("Preparing for space",
             "Astronaut training may include scientific study, engineering, robotics, survival training, "
             "medical preparation, and practice with spacecraft systems."),
            ("Living in microgravity",
             "In orbit, astronauts and objects experience apparent weightlessness because they are in "
             "continuous free fall together. Crews use restraints and specialised equipment to work safely."),
            ("Spacewalks",
             "An extravehicular activity, or spacewalk, allows astronauts to work outside a spacecraft while "
             "wearing a pressurised spacesuit with life-support systems.")
        ],
        "questions": [
            {
                "q": "Why do astronauts appear weightless in orbit?",
                "options": ["There is no gravity anywhere in space",
                            "They and their spacecraft are in continuous free fall",
                            "Their bodies stop having mass", "They are above the atmosphere only"],
                "answer": 1,
                "explanation": "Orbiting astronauts experience apparent weightlessness while falling around Earth."
            },
            {
                "q": "What provides life support during a spacewalk?",
                "options": ["An ordinary jacket", "A pressurised spacesuit system",
                            "A parachute alone", "A paper mask"],
                "answer": 1,
                "explanation": "A spacesuit helps provide pressure, oxygen, temperature control, and other protections."
            },
            {
                "q": "Which skill can be part of astronaut training?",
                "options": ["Robotics", "Ignoring checklists", "Avoiding teamwork",
                            "Working without communication"],
                "answer": 0,
                "explanation": "Robotics and teamwork are important in many space missions."
            }
        ]
    },
    {
        "id": 5,
        "title": "Satellites and Their Secrets",
        "category": "SATELLITE TECHNOLOGY",
        "icon": "🛰",
        "level": "Beginner",
        "duration": "9 min",
        "intro": "Discover how satellites support communication, weather forecasting, and navigation.",
        "sections": [
            ("What is a satellite?",
             "A satellite is an object that orbits another object. Artificial satellites can observe Earth, "
             "relay communications, measure weather, support navigation, and conduct scientific research."),
            ("Different orbits",
             "Low Earth orbit is relatively close to Earth and is used by many imaging satellites and crewed "
             "spacecraft. Geostationary satellites orbit above the equator at a distance that lets them remain "
             "over approximately the same longitude."),
            ("Solar power and communication",
             "Many satellites use solar panels to generate electricity and radio links to communicate with "
             "ground stations. Their designs must account for radiation, temperature changes, and limited maintenance.")
        ],
        "questions": [
            {
                "q": "Which technology can satellites support?",
                "options": ["Weather forecasting", "Only cooking", "Road construction directly",
                            "Underground mining by themselves"],
                "answer": 0,
                "explanation": "Weather satellites observe clouds, storms, and other atmospheric conditions."
            },
            {
                "q": "What do many satellites use to generate electricity?",
                "options": ["Solar panels", "Campfires", "Petrol engines only", "Wind turbines"],
                "answer": 0,
                "explanation": "Solar panels are widely used to power satellite electronics."
            },
            {
                "q": "What is a geostationary satellite designed to do?",
                "options": ["Stay over approximately the same longitude",
                            "Land on the Moon every day", "Stop orbiting", "Fly like an ordinary aircraft"],
                "answer": 0,
                "explanation": "Its orbital period matches Earth's rotation, keeping it over approximately the same longitude."
            }
        ]
    },
    {
        "id": 6,
        "title": "Black Holes and Deep Space",
        "category": "ASTROPHYSICS",
        "icon": "🌌",
        "level": "Intermediate",
        "duration": "10 min",
        "intro": "Investigate event horizons, gravity, and the mysteries of black holes.",
        "sections": [
            ("What is a black hole?",
             "A black hole is a region of spacetime where gravity is so strong that nothing, including light, "
             "can escape from inside its event horizon."),
            ("The event horizon",
             "The event horizon marks the boundary beyond which escape to the outside is impossible. It is "
             "not a solid surface. Material falling toward a black hole can become extremely hot before crossing it."),
            ("How scientists study them",
             "Scientists investigate black holes using the behaviour of nearby stars and gas, gravitational "
             "waves from certain mergers, and images of emission around some black holes.")
        ],
        "questions": [
            {
                "q": "What is the event horizon?",
                "options": ["A planet's atmosphere", "The boundary beyond which escape is impossible",
                            "A star's surface", "The edge of the solar system"],
                "answer": 1,
                "explanation": "Inside the event horizon, escape to the outside is impossible."
            },
            {
                "q": "Can light escape from inside a black hole's event horizon?",
                "options": ["Yes, always", "No", "Only during daytime", "Only with a telescope"],
                "answer": 1,
                "explanation": "By definition, light cannot escape from inside the event horizon."
            },
            {
                "q": "Which can help scientists detect black hole mergers?",
                "options": ["Gravitational waves", "Ocean tides alone", "Plant growth",
                            "Aircraft radar alone"],
                "answer": 0,
                "explanation": "Black hole mergers can produce detectable ripples in spacetime called gravitational waves."
            }
        ]
    },
    {
        "id": 7,
        "title": "Planet Earth from Space",
        "category": "EARTH SCIENCE",
        "icon": "🌍",
        "level": "Beginner",
        "duration": "8 min",
        "intro": "Understand Earth's atmosphere, climate, oceans, and observation from orbit.",
        "sections": [
            ("Our living planet",
             "Earth has liquid water at its surface, a protective atmosphere, and a range of conditions that "
             "support life. Its atmosphere helps regulate temperature and protects the surface from many hazards."),
            ("Earth observation",
             "Satellites monitor vegetation, ocean temperatures, ice cover, wildfires, storms, and changes "
             "in land use. These observations help scientists study our changing planet."),
            ("Protecting Earth",
             "Earth science helps communities understand natural hazards and long-term environmental change. "
             "Careful measurements over time are important for identifying trends.")
        ],
        "questions": [
            {
                "q": "What can Earth-observation satellites monitor?",
                "options": ["Vegetation and storms", "Only classroom attendance",
                            "Every underground object", "The future with certainty"],
                "answer": 0,
                "explanation": "Earth-observation instruments can monitor vegetation, storms, oceans, and much more."
            },
            {
                "q": "Why is Earth's atmosphere important?",
                "options": ["It helps regulate temperature and protects life",
                            "It removes all natural hazards", "It stops Earth from rotating",
                            "It makes gravity disappear"],
                "answer": 0,
                "explanation": "The atmosphere plays important roles in climate, weather, and protection from some hazards."
            },
            {
                "q": "What helps scientists identify environmental trends?",
                "options": ["Long-term measurements", "One random guess",
                            "Ignoring observations", "Changing units without recording them"],
                "answer": 0,
                "explanation": "Repeated, reliable measurements help reveal patterns and changes over time."
            }
        ]
    },
    {
        "id": 8,
        "title": "The Future of Space Missions",
        "category": "FUTURE EXPLORATION",
        "icon": "🛸",
        "level": "Intermediate",
        "duration": "11 min",
        "intro": "Explore robotic missions, lunar exploration, Mars research, and future technologies.",
        "sections": [
            ("Returning to the Moon",
             "Lunar exploration can help scientists study the Moon's history and test technologies for longer "
             "missions. The Moon may also provide useful opportunities to study how humans operate away from Earth."),
            ("Robotic exploration of Mars",
             "Rovers and orbiters examine Martian rocks, soil, atmosphere, and geology. Robotic missions can "
             "explore difficult environments before humans attempt more demanding journeys."),
            ("What comes next?",
             "Future missions may include improved reusable launch systems, advanced space telescopes, "
             "robotic exploration of icy moons, and research into living and working safely beyond Earth. "
             "Many possibilities remain research goals rather than guaranteed achievements.")
        ],
        "questions": [
            {
                "q": "Why send robotic missions before people explore some locations?",
                "options": ["To gather information and test technologies",
                            "To prove every mission is risk-free", "To eliminate scientific research",
                            "To make spacecraft unnecessary"],
                "answer": 0,
                "explanation": "Robots can gather data and test systems before more complex crewed missions."
            },
            {
                "q": "What do Mars rovers investigate?",
                "options": ["Martian rocks, soil, and geology", "Earth's oceans directly",
                            "The inside of every star", "Only Earth's weather"],
                "answer": 0,
                "explanation": "Rovers investigate the surface and geological history of Mars."
            },
            {
                "q": "Which is a possible area of future space research?",
                "options": ["Advanced space telescopes", "Stopping all scientific observation",
                            "Removing gravity from the universe", "Guaranteed travel to every galaxy"],
                "answer": 0,
                "explanation": "Advanced telescopes are a real and continuing area of space research."
            }
        ]
    }
]

# ------------------------- DATABASE -------------------------

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS progress (
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, lesson_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    with get_db() as db:
        return db.execute(
            "SELECT id, username FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Sign in to access your mission dashboard.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def get_progress(user_id):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM progress WHERE user_id = ?", (user_id,)
        ).fetchall()
    return {row["lesson_id"]: dict(row) for row in rows}


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


@app.before_request
def protect_post_requests():
    if request.method == "POST":
        supplied = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not supplied or not expected or not secrets.compare_digest(supplied, expected):
            abort(400, description="Security token missing or expired. Reload and try again.")


# ------------------------- DESIGN / HTML -------------------------

BASE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#050b19">
<title>{{ title }} | AeroSpace Academy</title>
<style>
:root {
 --bg:#050b19; --panel:#0b162a; --panel2:#101f38;
 --cyan:#48e6ff; --blue:#448cff; --text:#edf7ff;
 --muted:#93a9c5; --line:rgba(111,183,255,.18);
 --green:#55f2bb; --amber:#ffc66d; --red:#ff718c;
}
* {box-sizing:border-box}
body {
 margin:0; min-height:100vh; color:var(--text);
 background:radial-gradient(ellipse at 80% 0%,#122b51 0,transparent 38%),
 radial-gradient(ellipse at 5% 45%,#102443 0,transparent 32%),var(--bg);
 font-family:Inter,"Segoe UI",Arial,sans-serif; line-height:1.65;
}
a {color:var(--cyan);text-decoration:none}
a:hover {color:white}
button,input {font:inherit}
button,.btn {
 display:inline-flex;align-items:center;justify-content:center;gap:8px;
 border:1px solid rgba(72,230,255,.38);border-radius:10px;
 padding:11px 17px;color:#03101d;font-weight:800;cursor:pointer;
 background:linear-gradient(110deg,var(--cyan),#83baff);
 transition:transform .18s,filter .18s;
}
button:hover,.btn:hover {transform:translateY(-2px);filter:brightness(1.1);color:#03101d}
.btn.secondary,button.secondary {
 background:#101e35;color:var(--text);border-color:var(--line)
}
.btn.small {padding:7px 11px;font-size:.9rem}
header {
 position:sticky;top:0;z-index:10;background:rgba(5,11,25,.88);
 backdrop-filter:blur(18px);border-bottom:1px solid var(--line)
}
.nav {
 max-width:1200px;margin:auto;padding:13px 22px;
 display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap
}
.brand {display:flex;gap:11px;align-items:center;font-weight:900;letter-spacing:.5px}
.brand-icon {
 display:grid;place-items:center;width:42px;height:42px;border-radius:13px;
 background:linear-gradient(135deg,#153b62,#087d9d);
 border:1px solid #3adfff;box-shadow:0 0 22px #1ba9da40;font-size:22px
}
.brand small {display:block;color:var(--cyan);font-size:10px;letter-spacing:2px}
.nav-links {display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.nav-links a {color:#b6c9e0;font-size:.92rem}
.nav-links a:hover {color:var(--cyan)}
main {max-width:1200px;margin:auto;padding:30px 22px 70px}
.hero {
 position:relative;overflow:hidden;display:grid;grid-template-columns:1.2fr .8fr;
 gap:25px;align-items:center;padding:clamp(26px,5vw,64px);
 border:1px solid var(--line);border-radius:26px;
 background:linear-gradient(135deg,#102745e8,#091426f5);
 box-shadow:0 25px 90px #0003
}
.hero:after {
 content:"";position:absolute;width:290px;height:290px;border:1px solid #48e6ff28;
 border-radius:50%;right:4%;top:12%;box-shadow:0 0 0 25px #48e6ff08,0 0 0 55px #48e6ff05;
 pointer-events:none
}
.eyebrow {color:var(--cyan);letter-spacing:2.5px;font-size:.76rem;font-weight:900}
h1 {font-size:clamp(2.4rem,6vw,4.8rem);line-height:1.04;margin:16px 0}
h1 span {color:var(--cyan);text-shadow:0 0 28px #48e6ff30}
h2 {line-height:1.2}
p {color:#afc1d7}
.hero-graphic {position:relative;z-index:1;display:grid;place-items:center;min-height:260px}
.orbit {
 width:240px;height:240px;border:1px solid #48e6ff68;border-radius:50%;
 display:grid;place-items:center;position:relative;
 box-shadow:0 0 55px #208fff16,inset 0 0 50px #208fff10;
 animation:float 6s ease-in-out infinite
}
.orbit:before,.orbit:after {content:"";position:absolute;border:1px dashed #448cff66;border-radius:50%}
.orbit:before {width:185px;height:185px;transform:rotateX(60deg)}
.orbit:after {width:285px;height:105px;transform:rotate(-28deg)}
.planet {font-size:94px;filter:drop-shadow(0 0 25px #398eff75)}
@keyframes float {50%{transform:translateY(-8px) rotate(3deg)}}
.stats {display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0}
.stat,.card,.lesson,.panel {
 border:1px solid var(--line);background:linear-gradient(145deg,#0d1a30ed,#091323ed);
 border-radius:17px;padding:19px
}
.stat strong {display:block;font-size:1.6rem;color:var(--cyan)}
.stat span {color:var(--muted);font-size:.85rem}
.section-head {display:flex;justify-content:space-between;align-items:end;gap:14px;flex-wrap:wrap;margin:36px 0 16px}
.section-head h2 {margin:0}
.grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.lesson {transition:transform .2s,border-color .2s}
.lesson:hover {transform:translateY(-4px);border-color:#48e6ff66}
.lesson-icon {font-size:30px;margin-bottom:8px}
.tag {display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 9px;
 font-size:.72rem;letter-spacing:.8px;color:var(--cyan)}
.muted {color:var(--muted);font-size:.9rem}
.progress-track {height:7px;background:#1b2a40;border-radius:20px;overflow:hidden;margin:12px 0}
.progress-fill {height:100%;background:linear-gradient(90deg,var(--blue),var(--cyan));border-radius:20px}
.form-wrap {max-width:480px;margin:35px auto}
.form-wrap h1 {font-size:2.5rem}
label {display:block;margin:13px 0 6px;color:#c7d9ec;font-size:.9rem}
input {
 width:100%;background:#071120;color:white;border:1px solid #28425e;
 border-radius:10px;padding:12px 13px;outline:none
}
input:focus {border-color:var(--cyan);box-shadow:0 0 0 3px #48e6ff14}
.flash {padding:12px 15px;margin-bottom:12px;border:1px solid var(--line);
 border-radius:10px;background:#10203a;color:#d9f4ff}
.flash.error {border-color:#ff718c66;color:#ffb7c5}
.flash.success {border-color:#55f2bb66;color:#a9ffdf}
.flash.info {border-color:#48e6ff55}
.lesson-body {max-width:850px;margin:auto}
.lesson-body h1 {font-size:clamp(2rem,5vw,3.4rem)}
.lesson-section {padding:15px 0;border-bottom:1px solid var(--line)}
.quiz-option {
 display:flex;gap:10px;align-items:flex-start;padding:12px;margin:9px 0;
 border:1px solid var(--line);border-radius:10px;background:#0a1729
}
.quiz-option input {width:auto;margin-top:7px;accent-color:#48e6ff}
.quiz-option label {margin:0;cursor:pointer;flex:1}
.badges {display:flex;flex-wrap:wrap;gap:12px}
.badge {
 padding:14px;border:1px solid #48e6ff42;border-radius:14px;
 background:linear-gradient(135deg,#12304b,#0a1729);min-width:150px
}
.badge strong {display:block;color:var(--cyan)}
.empty {padding:30px;text-align:center;border:1px dashed var(--line);border-radius:15px}
footer {border-top:1px solid var(--line);padding:26px 20px;text-align:center;color:var(--muted);font-size:.88rem}
footer strong {color:var(--cyan)}
@media(max-width:850px) {
 .hero {grid-template-columns:1fr}.hero-graphic {min-height:220px}
 .grid {grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:560px) {
 .nav {padding:12px 15px}.nav-links {gap:10px}
 main {padding:20px 14px 50px}
 .grid {grid-template-columns:1fr}
 .stats {grid-template-columns:1fr}
 .hero {padding:25px 20px}.orbit {transform:scale(.82)}
}
</style>
</head>
<body>
<header>
 <div class="nav">
  <a class="brand" href="{{ url_for('home') }}">
   <span class="brand-icon">🚀</span>
   <span>VV LAB'S<small>AEROSPACE ACADEMY</small></span>
  </a>
  <nav class="nav-links">
   <a href="{{ url_for('home') }}">Home</a>
   <a href="{{ url_for('lessons') }}">Lessons</a>
   {% if user %}
    <a href="{{ url_for('dashboard') }}">Dashboard</a>
    <a href="{{ url_for('logout') }}">Log out</a>
   {% else %}
    <a href="{{ url_for('login') }}">Log in</a>
    <a class="btn small" href="{{ url_for('register') }}">Join free</a>
   {% endif %}
  </nav>
 </div>
</header>
<main>
 {% for category, message in get_flashed_messages(with_categories=true) %}
  <div class="flash {{ category }}">{{ message }}</div>
 {% endfor %}
 {{ content|safe }}
</main>
<footer>
 <strong>VV Lab's</strong> · AeroSpace Academy · Explore. Learn. Discover.<br>
 A free educational project. No payments, subscriptions, or paid lessons.
</footer>
</body>
</html>
"""


def render_page(title, content, **context):
    user = current_user()
    page = render_template_string(
        BASE_HTML,
        title=title,
        content=content,
        user=user,
        get_flashed_messages=__import__("flask").get_flashed_messages,
        **context
    )
    return page


def lesson_card(lesson, progress):
    record = progress.get(lesson["id"], {})
    completed = bool(record.get("completed", 0))
    score = record.get("best_score", 0)
    return f"""
    <article class="lesson">
      <div class="lesson-icon">{lesson['icon']}</div>
      <span class="tag">{lesson['category']}</span>
      <h3>{lesson['title']}</h3>
      <p>{lesson['intro']}</p>
      <div class="muted">{lesson['level']} · {lesson['duration']}</div>
      <div class="progress-track"><div class="progress-fill" style="width:{100 if completed else 0}%"></div></div>
      <div class="muted">{'✓ Completed' if completed else 'Not completed'} · Best quiz: {score}%</div>
      <p><a class="btn small" href="/lesson/{lesson['id']}">Open mission →</a></p>
    </article>
    """


# ------------------------- HOME -------------------------

@app.route("/")
def home():
    user = current_user()
    progress = get_progress(user["id"]) if user else {}
    completed = sum(bool(progress.get(i, {}).get("completed", 0)) for i in range(1, 9))
    lessons_html = "".join(lesson_card(lesson, progress) for lesson in LESSONS[:3])

    content = f"""
    <section class="hero">
      <div>
        <div class="eyebrow">MISSION CONTROL // LEARNING SYSTEM ONLINE</div>
        <h1>Your universe.<br>Your <span>next mission.</span></h1>
        <p>Explore aerospace, master the science of flight, discover distant worlds, and prepare for tomorrow's missions.</p>
        <p>
          <a class="btn" href="{url_for('lessons')}">🚀 Explore lessons</a>
          <a class="btn secondary" href="{url_for('dashboard') if user else url_for('register')}">
            { 'Open dashboard' if user else 'Start learning free' }
          </a>
        </p>
        <div class="muted">✦ Created with curiosity by VV Lab's</div>
      </div>
      <div class="hero-graphic"><div class="orbit"><div class="planet">🪐</div></div></div>
    </section>
    <div class="stats">
      <div class="stat"><strong>08</strong><span>Learning missions</span></div>
      <div class="stat"><strong>24</strong><span>Interactive quiz questions</span></div>
      <div class="stat"><strong>₹0</strong><span>Always free to learn</span></div>
    </div>
    <div class="section-head"><div><div class="eyebrow">FLIGHT PATH</div><h2>Featured missions</h2></div>
      <a href="{url_for('lessons')}">View all missions →</a>
    </div>
    <div class="grid">{lessons_html}</div>
    <section class="panel" style="margin-top:24px">
      <div class="eyebrow">YOUR JOURNEY STARTS HERE</div>
      <h2>Think beyond the horizon.</h2>
      <p>Study the science, test your knowledge, and track your progress one mission at a time.</p>
      <a class="btn" href="{url_for('dashboard') if user else url_for('register')}">
        { 'Continue your journey' if user else 'Create a free student account' }
      </a>
    </section>
    """
    return render_page("Mission Control", content)


# ------------------------- REGISTRATION / LOGIN -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not 3 <= len(username) <= 24:
            flash("Username must contain 3–24 characters.", "error")
        elif not username.replace("_", "").replace("-", "").isalnum():
            flash("Use only letters, numbers, underscores, or hyphens in your username.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                with get_db() as db:
                    cursor = db.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, generate_password_hash(password))
                    )
                    user_id = cursor.lastrowid
                session.clear()
                session["user_id"] = user_id
                session["csrf_token"] = secrets.token_urlsafe(32)
                flash("Welcome aboard! Your free account is ready.", "success")
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("That username is already in use. Please choose another.", "error")

    content = """
    <section class="form-wrap panel">
      <div class="eyebrow">NEW CREW MEMBER</div>
      <h1>Join the <span style="color:var(--cyan)">mission.</span></h1>
      <p>Create your free account to save lessons, quiz scores, and achievements.</p>
      <form method="post">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <label for="username">Username</label>
        <input id="username" name="username" minlength="3" maxlength="24" required autocomplete="username" placeholder="Choose a username">
        <label for="password">Password (at least 8 characters)</label>
        <input id="password" name="password" type="password" minlength="8" required autocomplete="new-password" placeholder="Create a password">
        <label for="confirm">Confirm password</label>
        <input id="confirm" name="confirm" type="password" minlength="8" required autocomplete="new-password" placeholder="Repeat your password">
        <p><button type="submit">Create free account →</button></p>
      </form>
      <p class="muted">Already a member? <a href="{{ url_for('login') }}">Log in</a></p>
    </section>
    """
    return render_page("Join the Crew", render_template_string(content, csrf_token=csrf_token))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            account = db.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
                (username,)
            ).fetchone()

        if account and check_password_hash(account["password_hash"], password):
            session.clear()
            session["user_id"] = account["id"]
            session["csrf_token"] = secrets.token_urlsafe(32)
            flash("Welcome back, astronaut.", "success")
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")

    content = """
    <section class="form-wrap panel">
      <div class="eyebrow">SECURE CREW ACCESS</div>
      <h1>Welcome <span style="color:var(--cyan)">back.</span></h1>
      <p>Sign in to continue your aerospace learning journey.</p>
      <form method="post">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <label for="username">Username</label>
        <input id="username" name="username" required autocomplete="username" placeholder="Your username">
        <label for="password">Password</label>
        <input id="password" name="password" type="password" required autocomplete="current-password" placeholder="Your password">
        <p><button type="submit">Log in →</button></p>
      </form>
      <p class="muted">New astronaut? <a href="{{ url_for('register') }}">Create a free account</a></p>
    </section>
    """
    return render_page("Crew Login", render_template_string(content, csrf_token=csrf_token))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully.", "info")
    return redirect(url_for("home"))


# ------------------------- LESSON LIBRARY / SEARCH -------------------------

@app.route("/lessons")
def lessons():
    query = request.args.get("q", "").strip().lower()
    progress = get_progress(current_user()["id"]) if current_user() else {}
    filtered = [
        lesson for lesson in LESSONS
        if query in lesson["title"].lower()
        or query in lesson["category"].lower()
        or query in lesson["intro"].lower()
    ] if query else LESSONS

    cards = "".join(lesson_card(lesson, progress) for lesson in filtered)
    if not cards:
        cards = '<div class="empty"><h3>No missions found</h3><p>Try another search term.</p></div>'

    content = f"""
    <div class="eyebrow">MISSION DATABASE // 08 MODULES</div>
    <h1 style="font-size:clamp(2.2rem,5vw,3.5rem)">Explore the <span style="color:var(--cyan)">universe.</span></h1>
    <p>Choose a mission, study the lesson, and complete its knowledge check.</p>
    <form method="get" action="{url_for('lessons')}" style="display:flex;gap:10px;max-width:600px;margin:20px 0">
      <input name="q" value="{query.replace('&','&amp;').replace('"','&quot;').replace('<','&lt;').replace('>','&gt;')}"
       placeholder="Search aviation, planets, rockets..." aria-label="Search lessons">
      <button type="submit">Search</button>
    </form>
    <div class="grid">{cards}</div>
    """
    return render_page("Lesson Library", content)


# ------------------------- INDIVIDUAL LESSON -------------------------

@app.route("/lesson/<int:lesson_id>")
def lesson_detail(lesson_id):
    lesson = next((x for x in LESSONS if x["id"] == lesson_id), None)
    if lesson is None:
        abort(404)

    sections = "".join(
        f'<section class="lesson-section"><h2>{heading}</h2><p>{body}</p></section>'
        for heading, body in lesson["sections"]
    )
    user = current_user()
    record = get_progress(user["id"]).get(lesson_id, {}) if user else {}
    score = record.get("best_score", 0)
    status = "Mission completed ✓" if record.get("completed") else "Mission in progress"

    content = f"""
    <article class="lesson-body">
      <a href="{url_for('lessons')}">← All missions</a>
      <div style="margin-top:28px" class="eyebrow">{lesson['category']} // MISSION {lesson_id:02d}</div>
      <div style="font-size:50px;margin-top:12px">{lesson['icon']}</div>
      <h1>{lesson['title']}</h1>
      <p>{lesson['intro']}</p>
      <div class="muted">{lesson['level']} · {lesson['duration']} · {status}</div>
      {sections}
      <section class="panel" style="margin-top:25px">
        <div class="eyebrow">KNOWLEDGE CHECK</div>
        <h2>Ready for your quiz?</h2>
        <p>Answer three questions and receive a score with explanations.</p>
        <p class="muted">Your best score: {score}%</p>
        <a class="btn" href="{url_for('quiz', lesson_id=lesson_id)}">Start quiz →</a>
      </section>
    </article>
    """
    return render_page(lesson["title"], content)


# ------------------------- QUIZZES -------------------------

@app.route("/quiz/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def quiz(lesson_id):
    lesson = next((x for x in LESSONS if x["id"] == lesson_id), None)
    if lesson is None:
        abort(404)

    if request.method == "POST":
        answers = []
        correct = 0

        for index, question in enumerate(lesson["questions"]):
            raw = request.form.get(f"q{index}", "")
            try:
                answer = int(raw)
            except (ValueError, TypeError):
                answer = -1

            valid = 0 <= answer < len(question["options"])
            is_correct = valid and answer == question["answer"]
            correct += int(is_correct)
            answers.append({
                "question": question["q"],
                "selected": question["options"][answer] if valid else "Not answered",
                "correct_answer": question["options"][question["answer"]],
                "is_correct": is_correct,
                "explanation": question["explanation"]
            })

        score = round(correct / len(lesson["questions"]) * 100)
        user = current_user()

        with get_db() as db:
            previous = db.execute(
                "SELECT * FROM progress WHERE user_id = ? AND lesson_id = ?",
                (user["id"], lesson_id)
            ).fetchone()

            best = max(score, previous["best_score"] if previous else 0)
            completed = int(score >= 60 or bool(previous and previous["completed"]))
            attempts = (previous["attempts"] if previous else 0) + 1

            db.execute("""
                INSERT INTO progress
                (user_id, lesson_id, completed, best_score, attempts, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, lesson_id) DO UPDATE SET
                    completed = excluded.completed,
                    best_score = excluded.best_score,
                    attempts = excluded.attempts,
                    updated_at = CURRENT_TIMESTAMP
            """, (user["id"], lesson_id, completed, best, attempts))

        result_html = "".join(
            f"""
            <div class="lesson-section">
              <strong style="color:{'var(--green)' if item['is_correct'] else 'var(--red)'}">
                {'✓ Correct' if item['is_correct'] else '✗ Review this answer'}
              </strong>
              <p><strong>{item['question']}</strong></p>
              <p>Your answer: {item['selected']}</p>
              <p>Correct answer: {item['correct_answer']}</p>
              <p class="muted">{item['explanation']}</p>
            </div>
            """
            for item in answers
        )

        content = f"""
        <section class="lesson-body panel">
          <div class="eyebrow">QUIZ REPORT // MISSION {lesson_id:02d}</div>
          <h1>{'Excellent work!' if score >= 80 else 'Mission report ready.'}</h1>
          <p>{lesson['title']}</p>
          <div class="stats">
            <div class="stat"><strong>{score}%</strong><span>Your score</span></div>
            <div class="stat"><strong>{correct}/{len(answers)}</strong><span>Correct answers</span></div>
            <div class="stat"><strong>{'✓' if score >= 60 else '↻'}</strong><span>{'Mission completed' if score >= 60 else 'Try again to complete'}</span></div>
          </div>
          <div class="progress-track"><div class="progress-fill" style="width:{score}%"></div></div>
          <h2>Answer explanations</h2>
          {result_html}
          <p style="margin-top:25px">
            <a class="btn" href="{url_for('quiz', lesson_id=lesson_id)}">Try quiz again</a>
            <a class="btn secondary" href="{url_for('dashboard')}">Dashboard</a>
          </p>
        </section>
        """
        return render_page("Quiz Results", content)

    questions_html = ""
    for index, question in enumerate(lesson["questions"]):
        options_html = "".join(
            f"""
            <div class="quiz-option">
              <input type="radio" id="q{index}_o{option_index}"
                name="q{index}" value="{option_index}" required>
              <label for="q{index}_o{option_index}">{option}</label>
            </div>
            """
            for option_index, option in enumerate(question["options"])
        )
        questions_html += f"""
        <section class="lesson-section">
          <h3>{index + 1}. {question['q']}</h3>
          {options_html}
        </section>
        """

    content = f"""
    <section class="lesson-body panel">
      <div class="eyebrow">KNOWLEDGE CHECK // MISSION {lesson_id:02d}</div>
      <h1>{lesson['title']}</h1>
      <p>Choose one answer for each question. A score of 60% completes the mission.</p>
      <form method="post">
        <input type="hidden" name="csrf_token" value="{csrf_token()}">
        {questions_html}
        <p><button type="submit">Submit answers →</button>
          <a class="btn secondary" href="{url_for('lesson_detail', lesson_id=lesson_id)}">Back to lesson</a>
        </p>
      </form>
    </section>
    """
    return render_page("Mission Quiz", content)


# ------------------------- STUDENT DASHBOARD -------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    progress = get_progress(user["id"])
    completed = sum(bool(progress.get(i, {}).get("completed", 0)) for i in range(1, 9))
    scores = [progress[i]["best_score"] for i in progress]
    average = round(sum(scores) / len(scores)) if scores else 0
    attempts = sum(row.get("attempts", 0) for row in progress.values())

    badges = [
        ("🚀", "First Launch", "Complete your first mission", completed >= 1),
        ("🛰", "Orbit Achieved", "Complete three missions", completed >= 3),
        ("🌌", "Deep Space Explorer", "Complete six missions", completed >= 6),
        ("🏆", "Mission Commander", "Complete all eight missions", completed == 8),
        ("🧠", "Perfect Score", "Earn 100% on any quiz", any(s == 100 for s in scores))
    ]
    badge_html = "".join(
        f"""
        <div class="badge" style="opacity:{1 if earned else .4}">
          <div style="font-size:25px">{icon}</div>
          <strong>{name} {'✓' if earned else '🔒'}</strong>
          <div class="muted">{description}</div>
        </div>
        """
        for icon, name, description, earned in badges
    )

    cards = "".join(lesson_card(lesson, progress) for lesson in LESSONS)

    content = f"""
    <section class="hero">
      <div>
        <div class="eyebrow">STUDENT CONTROL CENTER // ACCESS GRANTED</div>
        <h1>Welcome aboard,<br><span>{user['username']}</span>.</h1>
        <p>Your learning log is online. Continue a mission, improve your quiz scores, and unlock achievements.</p>
        <a class="btn" href="{url_for('lessons')}">Choose next mission →</a>
      </div>
      <div class="hero-graphic"><div class="orbit"><div class="planet">👨‍🚀</div></div></div>
    </section>
    <div class="stats">
      <div class="stat"><strong>{completed}/8</strong><span>Missions completed</span></div>
      <div class="stat"><strong>{average}%</strong><span>Average best quiz score</span></div>
      <div class="stat"><strong>{attempts}</strong><span>Total quiz attempts</span></div>
    </div>
    <div class="section-head"><div><div class="eyebrow">CREW RECOGNITION</div><h2>Your achievements</h2></div></div>
    <div class="badges">{badge_html}</div>
    <div class="section-head"><div><div class="eyebrow">PERSONAL FLIGHT LOG</div><h2>Your missions</h2></div></div>
    <div class="grid">{cards}</div>
    """
    return render_page("Student Dashboard", content)


# ------------------------- ERROR PAGES -------------------------

@app.errorhandler(400)
def bad_request(error):
    return render_page(
        "Request Error",
        f'<div class="panel"><h1>Request could not be verified.</h1>'
        f'<p>{error.description}</p><a class="btn" href="{url_for("home")}">Return home</a></div>'
    ), 400


@app.errorhandler(404)
def not_found(error):
    return render_page(
        "Mission Not Found",
        f'<div class="panel"><h1>Mission not found.</h1>'
        f'<p>The requested page is not in our flight plan.</p>'
        f'<a class="btn" href="{url_for("lessons")}">Return to missions</a></div>'
    ), 404


# ------------------------- START APPLICATION -------------------------

init_db()

if __name__ == "__main__":
    print("=" * 58)
    print(" VV LAB'S | AEROSPACE ACADEMY")
    print(" Mission Control is starting...")
    print(" Website: http://127.0.0.1:5000")
    print(" Database: aerospace_academy.db")
    print(" Payments: DISABLED — ALL LEARNING IS FREE")
    print(" Press CTRL+C to stop the server.")
    print("=" * 58)

    app.run(host="127.0.0.1", port=5000, debug=False)
