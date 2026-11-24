import http.server
import urllib.parse
import os

# ==========================================================
#  نرخ پایه: هر ۱ دلار = 288,000 تومان  (قابل تغییر)
# ==========================================================
USD_TO_TOMAN = 288_000

# نرخ تقریبی هر ارز نسبت به ۱ دلار
CURRENCIES = {
    "USD": ("دلار آمریکا",        1.0),
    "EUR": ("یورو",               0.92),
    "GBP": ("پوند انگلیس",        0.79),
    "AED": ("درهم امارات",        3.6725),
    "TRY": ("لیر ترکیه",          34.5),
    "CAD": ("دلار کانادا",        1.37),
    "AUD": ("دلار استرالیا",      1.52),
    "JPY": ("ین ژاپن",            150.0),
    "CNY": ("یوان چین",           7.24),
    "CHF": ("فرانک سوئیس",        0.88),
    "RUB": ("روبل روسیه",         92.0),
    "INR": ("روپیه هند",          83.2),
    "SEK": ("کرون سوئد",          10.5),
    "NOK": ("کرون نروژ",          10.7),
    "DKK": ("کرون دانمارک",       6.85),
    "QAR": ("ریال قطر",           3.64),
    "KWD": ("دینار کویت",         0.31),
    "SAR": ("ریال عربستان",       3.75),
    "OMR": ("ریال عمان",          0.385),
    "BHD": ("دینار بحرین",        0.376),
}


def convert(amount_toman, currency_code):
    if currency_code not in CURRENCIES:
        return None
    name, rate_per_usd = CURRENCIES[currency_code]
    unit_in_toman = USD_TO_TOMAN / rate_per_usd
    result = amount_toman / unit_in_toman
    return result, unit_in_toman, name


BASE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        min-height: 100vh;
        background: #0b0c0f;
        background-image: radial-gradient(circle at 50% -20%, rgba(255,255,255,0.04), transparent 60%);
        color: #d6d8de;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 56px 20px;
    }
    .brand {
        font-size: 26px;
        font-weight: 600;
        letter-spacing: 4px;
        color: #f2f3f5;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .brand .dot { color: #6b6f7a; }
    .brand-sub {
        font-size: 12px;
        color: #5c606b;
        letter-spacing: 6px;
        margin-bottom: 48px;
        text-transform: uppercase;
    }
    .card {
        width: 100%;
        max-width: 440px;
        background: #14161b;
        border: 1px solid #23262e;
        border-radius: 16px;
        padding: 36px 32px;
        box-shadow: 0 24px 60px rgba(0,0,0,0.45);
    }
    label {
        display: block;
        font-size: 12px;
        color: #8a8f9b;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    input, select {
        width: 100%;
        padding: 13px 15px;
        margin-bottom: 22px;
        background: #0e1014;
        border: 1px solid #262a33;
        border-radius: 10px;
        color: #f0f1f3;
        font-size: 15px;
        font-family: inherit;
        outline: none;
        transition: border-color .2s, background .2s;
    }
    input::placeholder { color: #4a4e58; }
    input:focus, select:focus {
        border-color: #4a5568;
        background: #10131a;
    }
    select {
        cursor: pointer;
        appearance: none;
        -webkit-appearance: none;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'><path fill='%238a8f9b' d='M6 8L0 0h12z'/></svg>");
        background-repeat: no-repeat;
        background-position: left 15px center;
        padding-left: 38px;
    }
    select option { background: #14161b; color: #f0f1f3; }
    button {
        width: 100%;
        padding: 14px;
        margin-top: 6px;
        border: 1px solid #2f3440;
        border-radius: 10px;
        font-family: inherit;
        font-size: 15px;
        font-weight: 500;
        color: #f0f1f3;
        cursor: pointer;
        background: #1b1e25;
        transition: background .2s, border-color .2s;
    }
    button:hover { background: #232833; border-color: #3a4150; }
    button:active { background: #171a20; }
    .result {
        margin-top: 26px;
        padding: 20px 18px;
        border-radius: 12px;
        text-align: center;
        background: #10131a;
        border: 1px solid #262a33;
        line-height: 1.9;
    }
    .result .amount { font-size: 22px; font-weight: 600; color: #ffffff; }
    .result .currency-code { font-size: 14px; color: #8a8f9b; font-weight: 400; margin-right: 6px; }
    .result small { display: block; margin-top: 10px; font-size: 12px; color: #5c606b; }
    .result.error { border-color: #4a1f26; background: #1a1113; color: #d98a95; font-size: 14px; }
    a.back { display: inline-block; margin-top: 22px; color: #8a8f9b; text-decoration: none; font-size: 13px; }
    a.back:hover { color: #ffffff; }
    .brand-small { font-size: 13px; letter-spacing: 4px; color: #5c606b; text-transform: uppercase; margin-bottom: 30px; text-align: center; }
</style>
"""


def build_options(selected="USD"):
    opts = []
    for code, (name, _) in CURRENCIES.items():
        sel = "selected" if code == selected else ""
        opts.append(f'<option value="{code}" {sel}>{name} — {code}</option>')
    return "\n".join(opts)


class CurrencyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samyar.hm — مبدل ارز</title>
    {BASE_STYLE}
</head>
<body>
    <div class="brand">Samyar<span class="dot">.hm</span></div>
    <div class="brand-sub">Currency Exchange</div>
    <div class="card">
        <form action="/convert" method="get">
            <label>مقدار به تومان</label>
            <input type="number" name="amount" placeholder="مثلاً 1000000"
                   required step="any" min="0" autofocus>
            <label>ارز مقصد</label>
            <select name="currency" required>
                {build_options("USD")}
            </select>
            <button type="submit">تبدیل</button>
        </form>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))

        elif self.path.startswith("/convert"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            amount_str = params.get("amount", [""])[0]
            currency = params.get("currency", ["USD"])[0].upper()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            try:
                amount = float(amount_str)
                if amount < 0:
                    raise ValueError
            except ValueError:
                self._result_page("مقدار وارد شده معتبر نیست.", error=True)
                return

            if currency not in CURRENCIES:
                self._result_page("ارز انتخاب شده پشتیبانی نمی‌شود.", error=True)
                return

            result, unit_in_toman, name = convert(amount, currency)
            self._result_page(
                f'<div class="amount">{result:,.2f} '
                f'<span class="currency-code">{currency}</span></div>'
                f'<small>{name} · نرخ هر {currency} = {unit_in_toman:,.0f} تومان</small>'
            )
        else:
            self.send_error(404)

    def _result_page(self, message, error=False):
        cls = "result error" if error else "result"
        html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samyar.hm — نتیجه</title>
    {BASE_STYLE}
</head>
<body>
    <div class="brand-small">Samyar.hm</div>
    <div class="card">
        <div class="{cls}">{message}</div>
        <div style="text-align:center;"><a class="back" href="/">← بازگشت</a></div>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = http.server.HTTPServer(("0.0.0.0", port), CurrencyHandler)
    print(f"✅ سرور روی پورت {port} اجرا شد.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 سرور متوقف شد.")
        server.server_close()
