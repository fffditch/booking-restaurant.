from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime
import json
import os
from urllib.parse import quote, unquote


# ============================================================
# Flask App
# ============================================================

app = Flask(__name__)
application = app

BOOKING_FILE = "/tmp/bookings.json"


# ============================================================
# สีของเว็บไซต์
# ============================================================

BG_COLOR = "#F5F6FA"
PRIMARY = "#E74C3C"
DARK = "#2C3E50"
GREEN = "#2ECC71"
RED = "#E74C3C"
WHITE = "#FFFFFF"
GRAY = "#7F8C8D"
LIGHT_GRAY = "#ECF0F1"
ORANGE = "#F39C12"


# ============================================================
# ข้อมูลร้านอาหาร
# ============================================================

restaurants = [

    {
        "id": 1,
        "name": "ร้านบักแอว แจ่วฮ้อน",
        "category": ["อาหารอีสาน", "นั่งชิล"],
        "description": "อาหารอีสานเปิดใหม่ บรรยากาศดี",
        "popular": True,
        "icon": "🌶️",
        "tables": 30
    },

    {
        "id": 2,
        "name": "บ้านล้านข้าว คลอง3",
        "category": ["อาหารไทย", "นั่งชิล"],
        "description": "ฟิลร้านอบอุ่น บรรยากาศร่มรื่น",
        "popular": False,
        "icon": "🏡",
        "tables": 10
    },

    {
        "id": 3,
        "name": "ร้านอาหารบายพาส",
        "category": ["อาหารป่า", "แนวลึกลับ"],
        "description": "รสชาติจัดจ้าน เน้นวัตถุดิบ",
        "popular": False,
        "icon": "🌲",
        "tables": 5
    },

    {
        "id": 4,
        "name": "ร้านคิดไม่ออกบอกกะเพรา",
        "category": ["อาหารไทย", "กะเพรา"],
        "description": "ร้านกะเพราจานเด็ด รสชาติเข้มข้น",
        "popular": False,
        "icon": "🌶️",
        "tables": 7
    },

    {
        "id": 5,
        "name": "เพิ่มพูน บุฟเฟ่ต์",
        "category": ["บุฟเฟ่ต์"],
        "description": "บุฟเฟ่ต์ กินได้ไม่อั้น ไม่จำกัด",
        "popular": False,
        "icon": "🍢",
        "tables": 12
    },

    {
        "id": 6,
        "name": "ธิดา คาเฟ่",
        "category": ["คาเฟ่", "นั่งชิล"],
        "description": "คาเฟ่สไตล์มินิมอล รวมอาหารคาวและหวาน",
        "popular": False,
        "icon": "☕",
        "tables": 10
    },

    {
        "id": 7,
        "name": "Ebisu Ramen",
        "category": ["อาหารญี่ปุ่น", "ราเมง"],
        "description": "ราเมงเส้นสด บรรยากาศนั่งชิล",
        "popular": False,
        "icon": "🍜",
        "tables": 8
    },

    {
        "id": 8,
        "name": "มาตาเนะชาบู&ซูซิ พรีเมี่ยม",
        "category": ["บุฟเฟ่ต์", "อาหารญี่ปุ่น"],
        "description": "อาหารระดับพรีเมี่ยม และอาหารญี่ปุ่นไม่อั้น",
        "popular": True,
        "icon": "🍣",
        "tables": 30
    },

    {
        "id": 9,
        "name": "ก๋วยเตี๋ยวข้ามคลอง",
        "category": ["อาหารไทย", "ก๋วยเตี๋ยว"],
        "description": "ก๋วยเตี๋ยวรสชาติน้ำซุปเข้มข้น ราคาถูก",
        "popular": True,
        "icon": "🍜",
        "tables": 40
    },

    {
        "id": 10,
        "name": "สเต๊กโชกุน",
        "category": ["สเต๊ก", "นั่งชิล"],
        "description": "อาหารจานใหญ่ บรรยากาศสบายๆ",
        "popular": False,
        "icon": "🥩",
        "tables": 15
    }

]


# ============================================================
# โหลดข้อมูลการจอง
# ============================================================

def load_bookings():

    if not os.path.exists(BOOKING_FILE):
        return []

    try:

        with open(
            BOOKING_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


bookings = load_bookings()


# ============================================================
# บันทึกข้อมูลการจอง
# ============================================================

def save_bookings():

    with open(
        BOOKING_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            bookings,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# ลบการจองที่หมดเวลา
# ============================================================

def remove_expired_bookings():

    global bookings

    current_time = datetime.now()

    new_bookings = []

    for booking in bookings:

        try:

            end_datetime = datetime.strptime(
                booking["date"] + " " + booking["end_time"],
                "%Y-%m-%d %H:%M"
            )

            if current_time < end_datetime:

                new_bookings.append(booking)

        except Exception:

            new_bookings.append(booking)

    if len(new_bookings) != len(bookings):

        bookings = new_bookings
        save_bookings()


# ============================================================
# ตรวจสอบเวลาถูกต้อง
# ============================================================

def parse_datetime(date, time):

    return datetime.strptime(
        date + " " + time,
        "%Y-%m-%d %H:%M"
    )


# ============================================================
# ตรวจสอบโต๊ะถูกจองหรือไม่
# ============================================================

def is_table_reserved(
    restaurant_id,
    table_number,
    date,
    start_time,
    end_time
):

    try:

        new_start = parse_datetime(
            date,
            start_time
        )

        new_end = parse_datetime(
            date,
            end_time
        )

    except Exception:

        return False


    for booking in bookings:

        if booking["restaurant_id"] != restaurant_id:
            continue

        if booking["table_number"] != table_number:
            continue

        if booking["date"] != date:
            continue


        try:

            old_start = parse_datetime(
                booking["date"],
                booking["start_time"]
            )

            old_end = parse_datetime(
                booking["date"],
                booking["end_time"]
            )

        except Exception:

            continue


        # ตรวจสอบเวลาทับกัน
        if new_start < old_end and new_end > old_start:

            return True


    return False


# ============================================================
# HTML หลัก
# ============================================================

BASE_HTML = """

<!DOCTYPE html>

<html lang="th">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>ระบบจองโต๊ะร้านอาหาร</title>


<style>

* {
    box-sizing: border-box;
}


body {

    margin: 0;

    font-family:
        Arial,
        "Tahoma",
        sans-serif;

    background: #F5F6FA;

    color: #2C3E50;

}


.header {

    background: #E74C3C;

    color: white;

    padding: 25px;

    text-align: center;

}


.header h1 {

    margin: 0;

    font-size: 32px;

}


.container {

    width: 95%;

    max-width: 1200px;

    margin: auto;

}


.search-box {

    background: white;

    margin-top: 25px;

    padding: 25px;

    border-radius: 15px;

    box-shadow:
        0 4px 15px rgba(0,0,0,0.08);

}


.search-box form {

    display: flex;

    gap: 10px;

}


.search-box input {

    flex: 1;

    padding: 14px;

    border: 1px solid #ddd;

    border-radius: 8px;

    font-size: 16px;

}


button,
.btn {

    border: none;

    border-radius: 8px;

    padding: 12px 20px;

    font-size: 15px;

    font-weight: bold;

    cursor: pointer;

    text-decoration: none;

    display: inline-block;

}


.btn-primary {

    background: #E74C3C;

    color: white;

}


.btn-green {

    background: #2ECC71;

    color: white;

}


.btn-gray {

    background: #7F8C8D;

    color: white;

}


.categories {

    margin-top: 25px;

    display: flex;

    gap: 10px;

    flex-wrap: wrap;

}


.category {

    background: white;

    color: #2C3E50;

    border: 1px solid #ddd;

    border-radius: 20px;

    padding: 10px 18px;

    text-decoration: none;

}


.category:hover {

    background: #E74C3C;

    color: white;

}


.section-title {

    margin-top: 35px;

    margin-bottom: 20px;

}


.restaurant-grid {

    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(250px, 1fr));

    gap: 20px;

}


.card {

    background: white;

    border-radius: 15px;

    padding: 22px;

    box-shadow:
        0 4px 15px rgba(0,0,0,0.08);

    transition: 0.2s;

}


.card:hover {

    transform: translateY(-3px);

}


.icon {

    font-size: 55px;

    text-align: center;

}


.card h3 {

    text-align: center;

    margin: 10px 0;

}


.description {

    color: #7F8C8D;

    text-align: center;

    min-height: 45px;

}


.tags {

    text-align: center;

    margin: 12px 0;

}


.tag {

    color: #F39C12;

    font-size: 13px;

    margin: 3px;

}


.card .btn {

    width: 100%;

    text-align: center;

}


.restaurant-header {

    background: white;

    margin-top: 25px;

    padding: 25px;

    border-radius: 15px;

    text-align: center;

}


.restaurant-header .big-icon {

    font-size: 70px;

}


.legend {

    background: white;

    margin-top: 20px;

    padding: 15px;

    border-radius: 12px;

    display: flex;

    justify-content: center;

    gap: 30px;

    flex-wrap: wrap;

}


.green-text {

    color: #2ECC71;

    font-weight: bold;

}


.red-text {

    color: #E74C3C;

    font-weight: bold;

}


.date-form {

    background: white;

    margin-top: 20px;

    padding: 20px;

    border-radius: 12px;

}


.date-form form {

    display: flex;

    gap: 10px;

    flex-wrap: wrap;

    align-items: center;

}


.date-form input {

    padding: 12px;

    border: 1px solid #ddd;

    border-radius: 8px;

    font-size: 15px;

}


.floor {

    background: white;

    margin-top: 20px;

    padding: 30px;

    border-radius: 15px;

}


.entrance {

    text-align: center;

    background: #ECF0F1;

    padding: 12px;

    border-radius: 10px;

    margin-bottom: 25px;

    font-weight: bold;

}


.table-grid {

    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(110px, 1fr));

    gap: 15px;

}


.table {

    min-height: 100px;

    border-radius: 15px;

    display: flex;

    flex-direction: column;

    justify-content: center;

    align-items: center;

    text-align: center;

    font-weight: bold;

}


.table-free {

    background: #2ECC71;

    color: white;

}


.table-booked {

    background: #E74C3C;

    color: white;

    opacity: 0.75;

}


.table a {

    color: white;

    text-decoration: none;

}


.booking-box {

    max-width: 600px;

    margin: 30px auto;

    background: white;

    padding: 30px;

    border-radius: 15px;

    box-shadow:
        0 4px 20px rgba(0,0,0,0.1);

}


.form-group {

    margin-bottom: 18px;

}


.form-group label {

    display: block;

    font-weight: bold;

    margin-bottom: 7px;

}


.form-group input {

    width: 100%;

    padding: 13px;

    border: 1px solid #ddd;

    border-radius: 8px;

    font-size: 16px;

}


.alert {

    padding: 15px;

    border-radius: 10px;

    margin-top: 20px;

}


.alert-error {

    background: #FDEDEC;

    color: #C0392B;

}


.alert-success {

    background: #EAFAF1;

    color: #1E8449;

}


.empty {

    text-align: center;

    padding: 50px;

    color: #7F8C8D;

}


.back {

    margin-top: 20px;

}


@media(max-width: 600px) {

    .header h1 {
        font-size: 24px;
    }

    .search-box form {
        flex-direction: column;
    }

    .table-grid {
        grid-template-columns:
            repeat(2, 1fr);
    }

}

</style>

</head>


<body>

<div class="header">

    <h1>🍽️ ระบบจองโต๊ะร้านอาหาร</h1>

    <p>ค้นหาร้านอาหารและจองโต๊ะได้ง่าย ๆ</p>

</div>


<div class="container">

{{ content | safe }}

</div>


</body>

</html>

"""


# ============================================================
# สร้างการ์ดร้าน
# ============================================================

def restaurant_cards(restaurant_list):

    if not restaurant_list:

        return """
        <div class="empty">
            <h2>ไม่พบร้านอาหาร</h2>
            <p>ลองค้นหาด้วยคำอื่น</p>
        </div>
        """


    html = '<div class="restaurant-grid">'


    for restaurant in restaurant_list:

        categories = ""

        for category in restaurant["category"]:

            categories += (
                f'<span class="tag">#{category}</span>'
            )


        popular = ""

        if restaurant["popular"]:

            popular = "<div>⭐ ร้านยอดนิยม</div>"


        html += f"""

        <div class="card">

            <div class="icon">
                {restaurant["icon"]}
            </div>

            <h3>
                {restaurant["name"]}
            </h3>

            <div class="description">
                {restaurant["description"]}
            </div>

            <div class="tags">
                {categories}
            </div>

            {popular}

            <p style="text-align:center;">
                🪑 {restaurant["tables"]} โต๊ะ
            </p>

            <a
                class="btn btn-primary"
                href="/restaurant/{restaurant["id"]}"
            >
                เข้าสู่ร้าน →
            </a>

        </div>

        """


    html += "</div>"

    return html


# ============================================================
# หน้าแรก
# ============================================================

@app.route("/")
def home():

    remove_expired_bookings()


    popular_restaurants = [

        restaurant

        for restaurant in restaurants

        if restaurant["popular"]

    ]


    categories = [
        "ทั้งหมด",
        "อาหารไทย",
        "คาเฟ่",
        "นั่งชิล",
        "บุฟเฟ่ต์",
        "อาหารป่า",
        "อาหารญี่ปุ่น",
        
    ]



    category_html = ""

    for category in categories:

        if category == "ทั้งหมด":

            category_url = url_for("home")

        else:

            category_url = url_for(
                "category",
                category=category
            )

        category_html += f"""
        <a
            class="category"
            href="{category_url}"
        >
            {category}
        </a>
        """


    content = f"""

    <div class="search-box">

        <h2>🔎 ค้นหาร้านอาหาร</h2>

        <form action="/search" method="get">

            <input
                type="text"
                name="q"
                placeholder="พิมพ์ชื่อร้านอาหาร..."
            >

            <button
                class="btn-primary"
                type="submit"
            >
                ค้นหา
            </button>

        </form>

    </div>


    <div class="categories">

        {category_html}

    </div>


    <h2 class="section-title">
        ⭐ ร้านอาหารยอดนิยม
    </h2>


    {restaurant_cards(popular_restaurants)}


    <h2 class="section-title">
        🍽️ ร้านอาหารทั้งหมด
    </h2>


    {restaurant_cards(restaurants)}

    """


    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# ค้นหาร้าน
# ============================================================

@app.route("/search")
def search():

    remove_expired_bookings()


    keyword = request.args.get(
        "q",
        ""
    ).strip().lower()


    result = []


    for restaurant in restaurants:

        if (

            keyword in restaurant["name"].lower()

            or

            keyword in restaurant["description"].lower()

            or

            any(
                keyword in category.lower()
                for category in restaurant["category"]
            )

        ):

            result.append(restaurant)


    content = f"""

    <div class="back">

        <a
            class="btn btn-gray"
            href="/"
        >
            ← กลับหน้าหลัก
        </a>

    </div>


    <h2 class="section-title">
        🔎 ผลการค้นหา: {keyword}
    </h2>


    {restaurant_cards(result)}

    """


    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# กรองหมวดหมู่
# ============================================================

@app.route("/category/<path:category>")
def category(category):

    remove_expired_bookings()

    result = [
        restaurant
        for restaurant in restaurants
        if category in restaurant["category"]
    ]

    content = f"""

    <div class="back">

        <a
            class="btn btn-gray"
            href="/"
        >
            ← กลับหน้าหลัก
        </a>

    </div>

    <h2 class="section-title">
        🍽️ หมวดหมู่: {category}
    </h2>

    {restaurant_cards(result)}

    """

    return render_template_string(
        BASE_HTML,
        content=content
    )

# ============================================================
# หน้าร้านอาหาร
# ============================================================

@app.route("/restaurant/<int:restaurant_id>")
def restaurant_page(restaurant_id):

    remove_expired_bookings()


    restaurant = next(
        (
            r for r in restaurants
            if r["id"] == restaurant_id
        ),
        None
    )


    if restaurant is None:

        return "ไม่พบร้านอาหาร", 404


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    selected_date = request.args.get(
        "date",
        today
    )


    start_time = request.args.get(
        "start",
        "18:00"
    )


    end_time = request.args.get(
        "end",
        "20:00"
    )


    # ตรวจสอบวันที่
    try:

        datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        )

    except Exception:

        selected_date = today


    # ตรวจสอบเวลา
    try:

        start_dt = datetime.strptime(
            start_time,
            "%H:%M"
        )

        end_dt = datetime.strptime(
            end_time,
            "%H:%M"
        )

        if start_dt >= end_dt:

            start_time = "18:00"
            end_time = "20:00"

    except Exception:

        start_time = "18:00"
        end_time = "20:00"


    tables_html = '<div class="table-grid">'


    for table_number in range(
        1,
        restaurant["tables"] + 1
    ):

        reserved = is_table_reserved(

            restaurant["id"],

            table_number,

            selected_date,

            start_time,

            end_time

        )


        if reserved:

            tables_html += f"""

            <div class="table table-booked">

                <div>
                    🔴
                </div>

                <div>
                    โต๊ะ {table_number}
                </div>

                <small>
                    ไม่ว่าง
                </small>

            </div>

            """

        else:

            booking_url = (
                f"/booking/"
                f"{restaurant['id']}/"
                f"{table_number}"
                f"?date={selected_date}"
                f"&start={start_time}"
                f"&end={end_time}"
            )


            tables_html += f"""

            <div class="table table-free">

                <a href="{booking_url}">

                    <div>
                        🟢
                    </div>

                    <div>
                        โต๊ะ {table_number}
                    </div>

                    <small>
                        ว่าง
                    </small>

                </a>

            </div>

            """


    tables_html += "</div>"


    content = f"""

    <div class="back">

        <a
            class="btn btn-gray"
            href="/"
        >
            ← กลับหน้าหลัก
        </a>

    </div>


    <div class="restaurant-header">

        <div class="big-icon">
            {restaurant["icon"]}
        </div>

        <h1>
            {restaurant["name"]}
        </h1>

        <p>
            {restaurant["description"]}
        </p>

        <p>
            🪑 มีทั้งหมด {restaurant["tables"]} โต๊ะ
        </p>

    </div>


    <div class="legend">

        <span class="green-text">
            🟢 โต๊ะว่าง = สามารถจองได้
        </span>

        <span class="red-text">
            🔴 โต๊ะไม่ว่าง = ไม่สามารถจองได้
        </span>

    </div>


    <div class="date-form">

        <form
            action="/restaurant/{restaurant["id"]}"
            method="get"
        >

            <label>
                📅 วันที่
            </label>

            <input
                type="date"
                name="date"
                value="{selected_date}"
                required
            >


            <label>
                🕐 เริ่ม
            </label>

            <input
                type="time"
                name="start"
                value="{start_time}"
                required
            >


            <label>
                🕐 สิ้นสุด
            </label>

            <input
                type="time"
                name="end"
                value="{end_time}"
                required
            >


            <button
                class="btn-primary"
                type="submit"
            >
                แสดงผังโต๊ะ
            </button>

        </form>

    </div>


    <div class="floor">

        <div class="entrance">
            🚪 ทางเข้า / ทางออก
        </div>

        {tables_html}

    </div>

    """


    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# หน้าแบบฟอร์มจอง
# ============================================================

@app.route("/booking/<int:restaurant_id>/<int:table_number>")
def booking_page(
    restaurant_id,
    table_number
):

    remove_expired_bookings()


    restaurant = next(
        (
            r for r in restaurants
            if r["id"] == restaurant_id
        ),
        None
    )


    if restaurant is None:

        return "ไม่พบร้านอาหาร", 404


    if table_number < 1 or table_number > restaurant["tables"]:

        return "ไม่พบโต๊ะ", 404


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    date = request.args.get(
        "date",
        today
    )


    start = request.args.get(
        "start",
        "18:00"
    )


    end = request.args.get(
        "end",
        "20:00"
    )


    content = f"""

    <div class="back">

        <a
            class="btn btn-gray"
            href="/restaurant/{restaurant_id}?date={date}&start={start}&end={end}"
        >
            ← กลับไปผังโต๊ะ
        </a>

    </div>


    <div class="booking-box">

        <h1 style="text-align:center;">
            📋 จองโต๊ะ
        </h1>


        <h2 style="text-align:center; color:#E74C3C;">
            {restaurant["name"]}
        </h2>


        <h2 style="text-align:center;">
            🪑 โต๊ะ {table_number}
        </h2>


        <form
            action="/book"
            method="post"
        >

            <input
                type="hidden"
                name="restaurant_id"
                value="{restaurant_id}"
            >

            <input
                type="hidden"
                name="table_number"
                value="{table_number}"
            >


            <div class="form-group">

                <label>
                    📅 วันที่จอง
                </label>

                <input
                    type="date"
                    name="date"
                    value="{date}"
                    required
                >

            </div>


            <div class="form-group">

                <label>
                    🕐 เวลาเริ่ม
                </label>

                <input
                    type="time"
                    name="start_time"
                    value="{start}"
                    required
                >

            </div>


            <div class="form-group">

                <label>
                    🕐 เวลาสิ้นสุด
                </label>

                <input
                    type="time"
                    name="end_time"
                    value="{end}"
                    required
                >

            </div>


            <div class="form-group">

                <label>
                    👤 ชื่อผู้จอง
                </label>

                <input
                    type="text"
                    name="customer_name"
                    placeholder="กรอกชื่อผู้จอง"
                    required
                >

            </div>


            <button
                class="btn-green"
                type="submit"
                style="width:100%;"
            >
                ✓ ยืนยันการจอง
            </button>

        </form>

    </div>

    """


    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# บันทึกการจอง
# ============================================================

@app.route(
    "/book",
    methods=["POST"]
)
def book():

    remove_expired_bookings()


    try:

        restaurant_id = int(
            request.form["restaurant_id"]
        )

        table_number = int(
            request.form["table_number"]
        )

    except Exception:

        return "ข้อมูลร้านหรือโต๊ะไม่ถูกต้อง", 400


    date = request.form.get(
        "date",
        ""
    ).strip()


    start_time = request.form.get(
        "start_time",
        ""
    ).strip()


    end_time = request.form.get(
        "end_time",
        ""
    ).strip()


    customer_name = request.form.get(
        "customer_name",
        ""
    ).strip()


    # --------------------------------------------------------
    # ตรวจสอบร้าน
    # --------------------------------------------------------

    restaurant = next(
        (
            r for r in restaurants
            if r["id"] == restaurant_id
        ),
        None
    )


    if restaurant is None:

        return "ไม่พบร้านอาหาร", 404


    # --------------------------------------------------------
    # ตรวจสอบข้อมูลว่าง
    # --------------------------------------------------------

    if not date or not start_time or not end_time:

        return error_page(
            "กรุณากรอกข้อมูลวันที่และเวลาให้ครบ"
        )


    if not customer_name:

        return error_page(
            "กรุณากรอกชื่อผู้จอง"
        )


    # --------------------------------------------------------
    # ตรวจสอบวันที่และเวลา
    # --------------------------------------------------------

    try:

        start_dt = parse_datetime(
            date,
            start_time
        )

        end_dt = parse_datetime(
            date,
            end_time
        )

    except Exception:

        return error_page(
            "รูปแบบวันที่หรือเวลาไม่ถูกต้อง"
        )


    if start_dt >= end_dt:

        return error_page(
            "เวลาสิ้นสุดต้องมากกว่าเวลาเริ่ม"
        )


    # --------------------------------------------------------
    # ตรวจสอบการจองซ้ำ
    # --------------------------------------------------------

    if is_table_reserved(

        restaurant_id,

        table_number,

        date,

        start_time,

        end_time

    ):

        return error_page(
            "โต๊ะนี้ถูกจองในช่วงเวลาดังกล่าวแล้ว"
        )


    # --------------------------------------------------------
    # บันทึก
    # --------------------------------------------------------

    new_booking = {

        "restaurant_id":
            restaurant_id,

        "restaurant_name":
            restaurant["name"],

        "table_number":
            table_number,

        "date":
            date,

        "start_time":
            start_time,

        "end_time":
            end_time,

        "customer_name":
            customer_name

    }


    bookings.append(
        new_booking
    )


    save_bookings()


    # --------------------------------------------------------
    # หน้าจองสำเร็จ
    # --------------------------------------------------------

    content = f"""

    <div class="booking-box">

        <div class="alert alert-success">

            <h2>
                ✅ จองโต๊ะสำเร็จ!
            </h2>

            <p>
                ร้าน: <b>{restaurant["name"]}</b>
            </p>

            <p>
                โต๊ะ: <b>{table_number}</b>
            </p>

            <p>
                วันที่: <b>{date}</b>
            </p>

            <p>
                เวลา:
                <b>{start_time} - {end_time}</b>
            </p>

            <p>
                ผู้จอง:
                <b>{customer_name}</b>
            </p>

        </div>


        <br>


        <a
            class="btn btn-primary"
            href="/restaurant/{restaurant_id}?date={date}&start={start_time}&end={end_time}"
        >
            กลับไปดูผังโต๊ะ
        </a>


        <a
            class="btn btn-gray"
            href="/"
        >
            กลับหน้าหลัก
        </a>

    </div>

    """


    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# หน้าแจ้งข้อผิดพลาด
# ============================================================

def error_page(message):

    content = f"""

    <div class="booking-box">

        <div class="alert alert-error">

            <h2>
                ❌ ไม่สามารถจองได้
            </h2>

            <p>
                {message}
            </p>

        </div>


        <br>


        <button
            class="btn btn-gray"
            onclick="history.back()"
        >
            ← กลับ
        </button>

    </div>

    """


    return render_template_string(
        BASE_HTML,
        content=content
    )


# ============================================================
# เริ่ม Flask
# ============================================================

if __name__ == "__main__":

    print("")
    print("==========================================")
    print("🍽️ ระบบจองโต๊ะร้านอาหาร")
    print("==========================================")
    print("เปิดเว็บไซต์ที่:")
    print("http://127.0.0.1:5000")
    print("==========================================")
    print("")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
