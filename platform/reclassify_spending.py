#!/usr/bin/env python3
"""reclassify_spending.py — cycle476 clean re-classification.

Loads finance_spending.jsonl.bak_reclass (the earliest pre-reclass backup),
re-guesses every row's category using the new 9-category ruleset,
writes the result back to finance_spending.jsonl, and saves a fresh
backup as finance_spending.jsonl.bak_reclass_final.

Target categories (9):
  餐飲 / 娛樂 / 醫療 / 日用 / 交通 / 旅遊 / 寵物 / 其他 / Poker

Trip date override: 2025-12-24 ~ 2026-01-02 → 旅遊 (Poker exempt).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path("C:/Users/admin/workspace/digital-immortality")
SRC = REPO / "results" / "finance_spending.jsonl.bak_reclass"
DST = REPO / "results" / "finance_spending.jsonl"
FINAL_BACKUP = REPO / "results" / "finance_spending.jsonl.bak_reclass_final"

# ---------------------------------------------------------------------------
# Trip date windows (Poker exempt).
# ---------------------------------------------------------------------------
TRIP_DATE_OVERRIDES: tuple[tuple[str, str, str], ...] = (
    ("2025-12-24", "2026-01-02", "旅遊"),
)

# ---------------------------------------------------------------------------
# Ruleset — ORDER MATTERS. First match wins.
#
# Priority design:
#   1. Poker      (privacy, absolute top)
#   2. 寵物        (pet-specific: supplies + pet medical)
#   3. 旅遊        (FX fees, airlines, booking platforms, resorts)
#   4. 醫療        (clinics, pharmacies, drugstores, therapy)
#   5. 交通        (transit, taxi, gas, parking, scooter sharing)
#   6. 餐飲        (restaurants, cafes, convenience, supermarkets, delivery)
#   7. 娛樂        (movies/games/books/sports/classes/gifts/toys)
#   8. 日用        (household goods + personal care + department stores + online shopping)
#   9. 其他        (subscriptions, utilities, bills, taxes, unknowns)
# ---------------------------------------------------------------------------

RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    # ------------------------------------------------------------------
    # 1. Poker — privacy code, never re-categorise
    # ------------------------------------------------------------------
    ("Poker", ("poker",)),

    # ------------------------------------------------------------------
    # 2. 寵物 — pet supplies + pet medical (珍珠 = cat; excludes 貓/貓貓 which = partner nickname)
    # ------------------------------------------------------------------
    ("寵物", (
        # Pet supplies
        "貓砂", "貓糧", "貓抓板", "貓窩", "貓碗", "貓鏟", "貓砂盆",
        "逗貓棒", "磨牙棒", "外出籠", "雞里肌", "貓零食",
        # Pet cat 珍珠 medical & grooming
        "珍珠看", "珍珠結紮", "珍珠剪線", "珍珠回娘家", "珍珠眼",
        "珍珠耳", "珍珠皮膚",
        # Pet medical signals
        "獸醫", "貓台大獸醫", "貓康藥局", "貓康", "寵物醫院", "寵物診所",
        "貓看病", "貓牙周", "貓齒科", "貓貓看皮膚", "貓做臉", "貓剪毛",
        # Pet store/brand
        "寵物", "貓貓頻道",
    )),

    # ------------------------------------------------------------------
    # 3. 旅遊 — booking platforms, airlines, FX fees, resorts, attractions
    # ------------------------------------------------------------------
    ("旅遊", (
        # Bank FX fee — strong travel signal
        "國外交易手續費", "外幣手續費", "foreign transaction fee",
        # Booking platforms
        "booking.com", "agoda", "airbnb", "trip.com", "hotels.com",
        "expedia", "kkday", "klook", "客路",
        # Airlines (major TW/asia)
        "航空", "airlines", "airways", "長榮", "華航", "星宇", "國泰航",
        "日航", "全日空", "樂桃", "酷航", "虎航", "ana ", "jal ",
        "機票", "eva air", "china airlines",
        # Car rental
        "租車", "rental car", "hertz", "avis", "budget rent",
        # Lodging
        "度假村", "resort ", "resort-", "hotel ", "hotel-", "hotels",
        "旅館", "民宿", "hostel", " inn ", "ryokan", "villa ",
        "住宿",
        # Attractions / tickets
        "景點", "樂園", "主題公園", "博物館", "門票", "溫泉", "spa",
        "展望台", "朱印", "御朱印", "首里城", "沖宮", "紅磚倉庫",
        "teamlab", "ghibli", "cupnoodles", "kkday",
        # Specific trip mentions seen in data
        "泡麵博物館", "六本木", "金魚展", "沖繩", "日本 10 天",
        "蒲田住宿", "the artist spa", "狐獴", "機場",
        "dfs", "免稅", "duty free",
        "單軌電車", "一日票", "周遊券", "pass券", "jr pass",
        "okashigoten", "首里", "那霸", "shinjuku", "shibuya",
        "asakusa", "kyoto", "osaka", "tokyo", "hokkaido",
        # 101 观光
        "台北101", "福隆", "墾丁", "三天旅行", "兩天一夜",
        "三天兩夜", "四天三夜",
        # Overseas 7-11 (trip only — caught by date window, but also here for safety)
        "nimmanhemin",
    )),

    # ------------------------------------------------------------------
    # 4. 醫療 — clinics, pharmacies, drugstores, therapy
    # ------------------------------------------------------------------
    ("醫療", (
        # Drugstores
        "康是美", "屈臣氏", "cosmed", "watsons", "watson's", "藥妝",
        "寶雅", "poya", "tomod", "大樹連鎖",
        # Counselling / mental health
        "諮商",
        # Medical misc
        "活髓治療", "除疤藥", "ok繃", "ok 蹦", "藥膏", "止滑液",
        "止滑噴霧", "團診",
        # Pharmacies / clinics / hospitals
        "藥局", "診所", "醫院", "clinic", "pharmacy", "hospital",
        "牙醫", "牙科", "皮膚科", "眼科", "腸胃", "耳鼻喉",
        "復健", "物理治療", "徒手治療", "prp", "按摩",
        "台大醫", "馬偕醫", "榮總", "長庚",
        # Health merchandise often bought at drugstore
        "止汗", "b群", "c群", "鎂鈣", "維他命", "保健品",
        "白木耳", "牙齒矯正", "牙齒損壞", "看病", "看醫生",
    )),

    # ------------------------------------------------------------------
    # 5. 交通 — transit, rideshare (non-eats), gas, parking, scooter
    # ------------------------------------------------------------------
    ("交通", (
        # Rail
        "高鐵", "台鐵", "捷運", "mrt",
        # Transit cards
        "悠遊卡", "一卡通", "suica", "icoca", "pasmo",
        # Taxi / rideshare
        "計程車", "taxi", "uber ", "uber-", "uber*",
        "優步", "優步福爾摩沙",
        # Scooter / bike sharing
        "gogoro", "goshare", "wemo", "威摩", "irent", "youbike", "chargespot",
        "充電", "博歐特", "耐斯車隊",
        # Gas / parking / ETC
        "加油", "加油站", "停車", "etc ", "etag", "昇泰昌", "昇?昌", "台灣中油",
        "中油", "台亞石油", "台塑石油",
        "騎車車", "機車",
        # Airport / shuttle (not airline itself)
        "國道客運", "客運", "公車",
    )),

    # ------------------------------------------------------------------
    # 6. 餐飲 — restaurants, cafes, convenience, supermarkets, delivery
    # ------------------------------------------------------------------
    ("餐飲", (
        # Convenience stores (all chains + variants)
        "7-11", "7 11", "7-eleven", "seven-eleven", "seven eleven",
        "711", "統一超商", "統一超", "超商",
        "全家", "familymart", "family mart", "family-mart",
        "萊爾富", "hi-life", "hilife",
        "ok超商", "ok 超商", "ok mart", "ok-mart", "ok mini",
        # Supermarkets / groceries
        "全聯", "家樂福", "carrefour", "costco", "好市多", "大潤發", "愛買",
        "楓康", "美廉社", "city super", "jasons",
        "超市", "supermarket", "雜貨", "蔬果", "肉品", "海鮮", "食材",
        # Delivery platforms
        "ubereats", "uber eats", "foodpanda", "food panda", "熊貓",
        "優食", "deliveroo",
        # Coffee / tea / beverage chains
        "星巴克", "starbucks", "cama", "louisa", "路易莎", "伯朗",
        "85度c", "mister donut", "dunkin",
        "迷客夏", "milksha", "五十嵐", "kebuke", "可不可",
        "coco", "清心", "珍煮丹", "鶴茶樓", "龍角",
        "麻古", "大苑子", "comebuy",
        # Food / meal signals
        "餐", "食", "飯", "麵", "壽司", "拉麵", "便當", "咖啡",
        "sukiya", "すき家", "yoshinoya", "吉野家", "くら寿司",
        "subway", "麥當勞", "mcdonald", "肯德基", "kfc",
        "摩斯", "mos ", "丹丹", "三商巧福",
        "cafe", "café", "restaurant", "bistro", "izakaya",
        "早餐", "午餐", "晚餐", "消夜", "下午茶", "宵夜",
        "茶", "飲料", "果汁", "豆花", "刨冰", "冰品", "雪花冰",
        "烘焙", "麵包", "蛋糕", "甜點", "dessert", "bakery",
        # Specific restaurants seen in data
        "給力", "馬可先生", "品川蘭", "百八魚場", "雞湯桑", "炭丼",
        "仁王家", "梁社漢", "米室", "一流二事", "旨丼", "民生雙連",
        "而立", "牛有廖", "哈囉你好", "hello!你好", "hello 你好",
        "金沐子", "麥味登", "貓貓午餐", "貓午餐", "貓晚餐",
        "狒狒早餐", "狒狒午餐", "狒狒晚餐", "狒狒伙食", "貓伙食",
        "狒狒鹽水雞", "京饌", "烹星", "京站", "安心食品",
        "優格", "希臘式優格", "地瓜", "水果", "梅子", "關東煮",
        "桂花凍", "焙茶", "凍焙茶", "抹茶", "matcha", "milk tea",
        "青山", "共樂", "享之饌", "旭集", "餐酒", "酒館", "燒烤",
        "火鍋", "鍋物", "丼飯", "定食", "串燒", "居酒屋",
        "鳳餐酒", "安東尼", "小林製冰",
        # More restaurants/food signals seen in data
        "口香糖", "糖", "餅乾", "蘿蔔", "鹽水雞", "粥", "炸雞",
        "蘋果", "木瓜", "滷蛋", "雞蛋", "蛋白", "氣泡水",
        "雞腿", "雞排", "牛排", "豬排", "肉排", "里肌",
        "三明治", "吐司", "刈包", "burger", "漢堡", "poke", "poké",
        "鮮奶酪", "薏仁", "綠豆", "蛋塔", "杏仁奶", "植物奶",
        "拿鐵", "latte", "義美", "湯", "小吃店", "水 ",
        "餃", "饅頭", "包子", "蔥油餅", "燒餅", "花捲",
        "牛奶", "豆腐", "豆漿", "豆花", "牛奶冰", "奶茶",
        "cuppa", "so good", "8more", "銀耳", "鮮奶",
        "hoho drinks", "drinks", "beverage", "juice",
        "ugtea", "tea ", " tea", "珈琲", "coffee", "卡布",
        "義大利麵", "pasta", "pizza", "必勝客", "pizza hut",
        "達美樂", "domino",
        "haloa poke", "curry", "curry for peace", "咖哩",
        "tamed fox", "cozy quail", "tann", "cinder and smoke",
        "lost taiwan", "libreadry", "巢屋", "東京油組",
        "白巷子", "福餃", "fukgyo", "季緣", "綠逗",
        "yoogup", "an burger", "藍新", "人間煙火", "深活",
        "樂法", "hama sus", "億萬里", "mu hills",
        "朝美料", "百八", "湯湯水水", "ok蹦",
        "c hock", "hood", "kure8", "dream plaza",
        "hello drinks", "精萃",
        "河粉", "pho ", "港都", "熱炒", "經貿",
        "coppii", "lumii", "點心", "dim sum",
        "肯塔哈", "貓cc", "cc ", "cc-",
        "紅豆餅", "鹹水雞", "沙拉", "salad", "香蕉", "banana",
        "堅果", "nut ", "nuts", "越春", "迪化街", "茄",
        "貪吃", "greed", "brekkie", "kaju", "啾",
        "什麼雞", "檔案室", "410號",
        "鐵板燒", "teppanyaki", "吉豚屋", "katsu", "就饗",
        "克菲爾", "kefir", "funpaste",
        "柿子", "西瓜", "香蕉片", "火龍果", "葡萄", "橘子",
        "柳橙", "芒果", "鳳梨", "草莓", "藍莓", "櫻桃",
        "哈密瓜", "奇異果",
        "暖暖包",  # trip context but harmless in 餐飲
        "關東本家", "丼魂", "烏弄", "得正", "一沐日", "五桐號",
        "鑫口味", "粥大福", "beard papa", "大戶屋", "拼拼拌",
        "黑松", "販賣機", "鍋燒", "baristro", "青草", "姚德和",
        "gonna eat", "春燒桂花", "德克士", "炸雞", "牧方", "moocub",
        "炭井", "寧夏夜市", "夜市",
        "貓貝果", "貝果", "bagel", "palmier", "可頌",
        "友善時光", "雲眾股份", "hellos 你好", "rimping", "mjt-central",
        "andoumomofuku", "azabudai",
        "丼", "沃貓奧", "嵐天", "龜記", "貓龜記", "學斯",
        "global m", "伊府", "global-m",
        # Delivery convenience
        "街口電支", "街口twqr", "街口funpass", "line pay", "綁卡交易",
    )),

    # ------------------------------------------------------------------
    # 7. 娛樂 — movies, games, books, sports, classes, gifts, toys, music
    # ------------------------------------------------------------------
    ("娛樂", (
        # Movies / theatres
        "影城", "電影", "秀泰", "威秀", "vieshow", "in89",
        "國賓影", "華納威秀",
        # Concerts / KTV / shows
        "演唱會", "concert", "ktv", "錢櫃", "好樂迪",
        # Games
        "steam", "nintendo", "playstation", "xbox", "遊戲",
        "boardgame", "桌遊", "玩具", "toy ", " toys",
        "阿瓦隆", "avalon",
        # Sports — activities
        "羽球", "健身", "gym", "fitness", "yoga", "瑜珈",
        "球拍", "運動", "自在生活", "球場", "練球",
        # Sports equipment brands
        "球鞋", "運動服", "nike", "adidas", "asics", "yonex", "victor",
        "迪卡儂", "decathlon", "lululemon", "under armour", "ua ",
        "凱勝體育",
        # Books / education
        "書店", "博客來", "誠品書", "金石堂", "讀冊",
        " 書", "course", "課程", "補習", "學費", "tutor",
        "teachable", "udemy", "coursera", "hahow",
        "空環課", "手作課", "rehersoul", "課卡",
        # Cat café / pet play (撸貓 = hang out with cats)
        "撸貓", "擼貓", "貓咖", "cat cafe", "cat café",
        # Escape rooms / LARP / immersive entertainment
        "密室", "解謎", "larp", "狙擊", "松菸解謎", "瘋密",
        "不貓能的任務", "catch 22", "展票", "動畫展",
        "迪士尼", "disney",
        # Movie titles seen (玩命關頭)
        "玩命關頭",
        # Workshops
        "工作坊", "澄言彤語",
        "幻隱光靈", "光靈",
        "同事生日", "生日禮", "生日蛋糕", "賀禮",
        "複習考", "模擬考", "考試", "題庫",
        # Pole dancing / aerial / dance classes
        "舞綢", "懸浮", "自主練習", "空中", "舞蹈課",
        "pole dance", "aerial",
        # English / language lessons
        "stand up eibun", "英文課", "english class", "日文課",
        # Rental of hobby/practice spaces (prefix 貓租 = partner renting space)
        "貓租", "租教室", "租場地", "瑜伽教室", "瑜珈教室",
        "貓心沐", "貓自在", "貓瑜", "心沐",
        # Music
        "音樂", "music",
        # Gifts / red envelopes / farewells
        "禮金", "紅包", "白包", "包禮", "喜餅", "奠儀",
        "伴手禮", "離職蛋糕", "花苑", "花坊", "花語",
        "母親節禮物", "父親節禮物",
    )),

    # ------------------------------------------------------------------
    # 8. 日用 — household goods, personal care, department stores, online shopping
    # ------------------------------------------------------------------
    ("日用", (
        # Home goods
        "無印良品", "muji", "ikea", "宜家", "hola", "特力屋", "b&q",
        "家電", "家具", "廚具", "寢具", "清潔", "衛生紙", "洗衣",
        "電池", "燈泡", "工具", "五金", "日本城",
        # Department stores
        "誠品", "新光三越", "sogo", "遠東sogo", "百貨", "統一時代",
        "京站時尚", "微風", "環球購物", "遠百", "三井outlet",
        "忠孝館", "信義新光",
        # Online shopping platforms (default to 日用 when no better signal)
        "shopee", "蝦皮", "露天", "pchome", "momo", "amazon", "樂天",
        "淘寶", "雅虎奇摩", "yahoo購物", "富邦momo",
        # Personal care / beauty / clothing
        "剪髮", "燙髮", "染髮", "洗頭", "美睫", "光療", "指甲",
        "美容", "做臉", "皮秒", "雷射", "美甲", "補睫毛", "睫毛",
        "麗晶精品",
        "uniqlo", "h&m", "zara", "gu ", "lativ", "net ",
        "earth ecologies", "靴下屋", "寶拉珍選",
        "衣服", "鞋子", "new balance", "襪子", "帽子", "耳環",
        "唇筆", "口紅", "粉底", "護手霜", "護髮", "尾牙禮服",
        "髮圈", "短褲", "上衣", "洋裝",
        "apple store", "apple 直營", "iphone", "ipad", "airpods", "macbook",
        "保護貼", "保護殼", "手機殼",
        # Misc household goods seen in data
        "眼罩", "時鐘", "筆記本", "充電線", "充電器", "耳機",
        "記憶卡", "tapo", "監視器", "芯動力", "睿鼎數位",
        "展業儀器", "一般商品買賣", "身分轉移", "紀念品", "明信片",
        "elementi", "scan2pay",
        # Misc daily-use seen in data
        "包裝袋", "折疊傘", "傘",
        "3c襪舍", "面膜", "卸妝膏", "solone", "眉筆", "唇膏",
        "Azure Crème", "azure crème", "Bonny Live", "bonny live",
        "t-shoppi", "t shoppi",
        "ikea", "tops-chiangmai", "signature relax",
        "優衣庫", "blike", "履歷健檢",
        "citylink", "city link", "文具", "九乘九",
        "生活館", "三花", "衛生棉", "棉條", "生理用品",
        "狒狒剪", "剪頭髮", "剪毛",
        "彩妝", "cosmetic", "彩繪", "單車繩梯", "繩梯",
    )),
)

# Note-only fallbacks (applied to note field when merchant gave no hit)
NOTE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("餐飲", ("晚餐", "午餐", "早餐", "消夜", "下午茶", "宵夜",
             "茶", "咖啡", "飲料", "便當", "鹽水雞", "伙食", "餐費")),
    ("娛樂", ("羽球", "練球", "健身")),
    ("醫療", ("物理治療", "復健", "徒手", "看醫生")),
    ("日用", ("購物", "網購")),
)

# Bank-noise patterns that map to 其他
BANK_NOISE = ("本行扣繳", "跨行手續費", "年費扣繳")

# Fixed-cost / subscription / utility signals → 其他
OTHER_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("其他", (
        # Digital subscriptions
        "icloud", "apple 空間", "apple空間", "apple空間",
        "google one", "google*cloud", "google cloud",
        "youtube premium", "youtube 訂閱", "youtube訂閱",
        "office 365", "microsoft 365", "dropbox", "notion",
        "chatgpt", "claude pro", "claude.ai", "openai", "anthropic",
        "spotify", "netflix", "disney+", "disney plus", "kkbox",
        "apple.com/bill", "apple one", "github", "cursor",
        "kure8",
        # iPhone 保護貼 etc are 日用, but "iphone 保護" has iphone - will match elsewhere
        # Actually, iphone accessories should be 日用 not 其他 - handled by "iphone" being absent here
        # Telecom
        "中華電信", "遠傳", "台灣大哥大", "台灣之星", "亞太電信", "hinet",
        "手機月租", "電信費", "網卡", "儲值",
        # Utilities
        "台電", "自來水", "瓦斯", "electricity", "water company", "gas bill",
        "電費", "水費", "瓦斯費",
        # Insurance / tax / government / HOA
        "保險", "insurance", "人壽", "產險", "綠界-中華民國人壽",
        "地方稅", "綜所稅", "稅款", "繳稅", "健保", "勞保",
        "里長伯", "管理費", "房租",
        # Misc
        "雜支", "貓電信", "水電", "網路費",
    )),
)


EXACT_MERCHANT_MAP: dict[str, str] = {
    "珍珠": "寵物",
    "狒狒": "其他",  # ambiguous bare name; only a couple entries
    "貓": "餐飲",  # bare 貓 in ledger almost always = partner food
    "其他": "其他",
}


def classify(merchant: str, note: str, existing_category: str) -> str:
    """Pure function — returns new category."""
    m = (merchant or "").lower()
    n = (note or "").lower()
    hay = f"{m} {n}"

    # Bank noise first (but not higher than Poker)
    if "poker" in m or "poker" in n:
        return "Poker"

    # Exact-merchant overrides (bare disambiguation)
    if merchant.strip() in EXACT_MERCHANT_MAP:
        return EXACT_MERCHANT_MAP[merchant.strip()]

    # Bank noise → 其他
    for tok in BANK_NOISE:
        if tok in hay:
            return "其他"

    # Main rule list (order = priority)
    for cat, kws in RULES:
        for kw in kws:
            if kw.lower() in hay:
                return cat

    # Fixed costs / subscriptions / utilities
    for cat, kws in OTHER_RULES:
        for kw in kws:
            if kw.lower() in hay:
                return cat

    # Note-only rules
    for cat, kws in NOTE_RULES:
        for kw in kws:
            if kw.lower() in n:
                return cat

    return "其他"


def apply_trip_override(date: str, category: str) -> str:
    if category == "Poker":
        return category
    if not date:
        return category
    for start, end, cat in TRIP_DATE_OVERRIDES:
        if start <= date <= end:
            return cat
    return category


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: source backup missing: {SRC}")
        return 1

    stats_before = Counter()
    stats_after = Counter()
    unknowns: Counter = Counter()
    lines_out: list[str] = []

    with SRC.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            old_cat = obj.get("category", "")
            merchant = obj.get("merchant", "") or ""
            note = obj.get("note", "") or ""
            date = obj.get("date", "") or ""

            new_cat = classify(merchant, note, old_cat)
            new_cat = apply_trip_override(date, new_cat)

            stats_before[old_cat] += 1
            stats_after[new_cat] += 1
            if new_cat == "其他":
                unknowns[merchant] += 1

            obj["category"] = new_cat
            lines_out.append(json.dumps(obj, ensure_ascii=False))

    # Write outputs
    DST.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    FINAL_BACKUP.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    total = sum(stats_after.values())
    print(f"Total rows: {total}")
    print("\nBefore:")
    for k, v in stats_before.most_common():
        print(f"  {k}: {v}")
    print("\nAfter:")
    for k, v in stats_after.most_common():
        pct = v / total * 100
        print(f"  {k}: {v} ({pct:.1f}%)")

    other_pct = stats_after["其他"] / total * 100
    print(f"\n其他 比例: {other_pct:.2f}% (目標 <5%)")
    print(f"\nTop 40 uncategorised merchants:")
    for k, v in unknowns.most_common(40):
        print(f"  {v}\t{k}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
