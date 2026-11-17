#!/usr/bin/env python3
"""Static site generator for Dive Dive Digital.

Edit CONFIG below, then run:  python3 build.py
Output goes to ./site  (upload that folder to Cloudflare Pages).
"""
import json, os, shutil, html
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "site")

# ---------------------------------------------------------------- CONFIG
CONFIG = {
    "site_url": "https://divdivedigital.com",          # change if your domain differs
    "brand": "Dive Dive Digital",
    "email": "hello@divdivedigital.com",               # set up this mailbox (or change it)
    "booking_url": "/free-audit/",                       # swap for your Calendly / Cal.com link later
    "founder": "Muhammad Afzal",
    "linkedin": "",                                      # optional, e.g. https://www.linkedin.com/in/...
    "upwork": "",                                        # optional, link to your Upwork profile
    "scheduler": "",                                     # optional, Calendly / Cal.com link for a 20 minute call
}
# Prices shown on the site (USD). Positioned mid-market for US dental specialist marketing.
PRICES = {
    "seo":   {"from": 1500, "unit": "month", "label": "Orthodontist SEO", "note": "per location, Google Business Profile included"},
    "gbp":   {"from": 500,  "unit": "month", "label": "Google Business Profile", "note": "plus a one-time $750 profile rebuild"},
    "web":   {"from": 4500, "unit": "project", "label": "Website design", "note": "most practice sites land between $5,000 and $9,500"},
    "endo":  {"from": 1500, "unit": "month", "label": "Endodontist marketing", "note": "per location, referral pages included"},
}
def price_txt(k):
    v = PRICES[k]; return f'${v["from"]:,}' + ("/month" if v["unit"] == "month" else "")

# Real client reviews only. Add once a client gives permission, e.g.
# {"quote": "...", "name": "Dr. Jane Smith", "role": "Orthodontist", "place": "Austin, TX", "source": "Upwork"}
# The reviews section stays hidden while this list is empty.
REVIEWS = []

OFFICES = [
    {"label": "USA office", "street": "5900 Balcones Drive, Suite 100", "city": "Austin", "region": "TX",
     "postal": "78731", "country": "US", "country_name": "USA", "phone": "+1 321 490-9188", "tel": "+13214909188"},
    {"label": "UK office", "street": "275 New North Road, Islington #1795", "city": "London", "region": "",
     "postal": "N1 7AA", "country": "GB", "country_name": "UK", "phone": "+44 7716 408844", "tel": "+447716408844"},
]
def office_html(o):
    loc = f'{o["city"]}, {o["region"]} {o["postal"]}' if o["region"] else f'{o["city"]} {o["postal"]}'
    return (f'<address><b>{o["label"]}</b><br>{o["street"]}<br>{loc}, {o["country_name"]}<br>'
            f'<a href="tel:{o["tel"]}">{o["phone"]}</a></address>')
TODAY = date.today().isoformat()
S = CONFIG["site_url"].rstrip("/")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)

# ---------------------------------------------------------------- CSS
CSS = r"""
:root{
  --ink:#0E2240;--ink-2:#2A3C58;--muted:#5A6A7E;--teal:#127C76;--teal-d:#0B5F5A;
  --mint:#E5F1EF;--mint-2:#D3E8E4;--paper:#FAFBFA;--white:#FFFFFF;--saffron:#F2A93B;--saffron-d:#DB8F1C;
  --line:#D7E1DF;--star:#E9A23B;--good:#1E8E5A;--warn:#C9822A;--bad:#C2493D;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --body:"Public Sans",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --wrap:1180px;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
body{margin:0;background:var(--paper);color:var(--ink-2);font:400 17px/1.65 var(--body)}
img,svg{max-width:100%;display:block}
a{color:var(--teal-d);text-underline-offset:3px}
a:hover{color:var(--ink)}
:focus-visible{outline:3px solid var(--saffron);outline-offset:3px;border-radius:4px}
h1,h2,h3,h4{font-family:var(--display);color:var(--ink);line-height:1.08;margin:0 0 .5em;letter-spacing:-.02em}
h1{font-size:clamp(2.35rem,5.2vw,4.1rem);font-weight:800}
h2{font-size:clamp(1.8rem,3.4vw,2.7rem);font-weight:700}
h3{font-size:1.28rem;font-weight:700;letter-spacing:-.01em}
p{margin:0 0 1em;max-width:68ch}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:var(--ink);color:#fff;padding:8px 14px;z-index:99}
.lede{font-size:1.18rem;color:var(--ink-2);max-width:58ch}
.small{font-size:.9rem;color:var(--muted)}
section{padding:88px 0}
.tint{background:var(--mint)}
.ink{background:var(--ink);color:#C9D5E4}
.ink h2,.ink h3{color:#fff}
.ink a{color:var(--saffron)}

/* buttons */
.btn{display:inline-flex;align-items:center;gap:.5em;font:600 1rem/1 var(--body);padding:16px 24px;border-radius:10px;text-decoration:none;border:2px solid transparent;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.btn-primary{background:var(--saffron);color:var(--ink)}
.btn-primary:hover{background:var(--saffron-d);color:var(--ink)}
.btn-ghost{border-color:var(--ink);color:var(--ink);background:transparent}
.btn-ghost:hover{background:var(--ink);color:#fff}
.ink .btn-ghost{border-color:#fff;color:#fff}.ink .btn-ghost:hover{background:#fff;color:var(--ink)}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}

/* header */
.site-head{position:sticky;top:0;z-index:50;background:rgba(250,251,250,.94);backdrop-filter:saturate(1.4) blur(8px);border-bottom:1px solid var(--line)}
.head-in{display:flex;align-items:center;justify-content:space-between;height:72px;gap:20px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font:800 1.22rem/1 var(--display);letter-spacing:-.02em}
.logo svg{width:34px;height:34px}
.nav-desktop{display:flex;align-items:center;gap:26px;list-style:none;margin:0;padding:0}
.nav-desktop a{color:var(--ink);text-decoration:none;font-weight:500;font-size:.97rem}
.nav-desktop a:hover,.nav-desktop a[aria-current]{color:var(--teal)}
.nav-desktop .btn{padding:11px 18px;font-size:.95rem}
.menu{display:none}
@media (max-width:960px){
  .nav-desktop{display:none}
  .menu{display:block;position:relative}
  .menu summary{list-style:none;cursor:pointer;font-weight:600;color:var(--ink);padding:10px 14px;border:2px solid var(--ink);border-radius:10px}
  .menu summary::-webkit-details-marker{display:none}
  .menu ul{position:absolute;right:0;top:52px;background:#fff;border:1px solid var(--line);border-radius:14px;list-style:none;margin:0;padding:10px;width:min(300px,86vw);box-shadow:0 18px 40px rgba(14,34,64,.16)}
  .menu li a{display:block;padding:12px 14px;color:var(--ink);text-decoration:none;border-radius:8px;font-weight:500}
  .menu li a:hover{background:var(--mint)}
  .menu .btn{justify-content:center;margin-top:6px;color:var(--ink)}
}

/* hero */
.hero{padding:64px 0 72px;position:relative;overflow:hidden}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center}
@media (max-width:960px){.hero-grid{grid-template-columns:1fr;gap:40px}}
.hero h1{margin-bottom:.35em}
.proof-strip{display:flex;flex-wrap:wrap;gap:10px 22px;margin:34px 0 0;padding:0;list-style:none}
.proof-strip li{display:flex;align-items:center;gap:8px;font-size:.93rem;color:var(--ink-2);font-weight:500}
.proof-strip svg{width:18px;height:18px;flex:none}

/* map pack mockup (signature element) */
.pack{background:#fff;border:1px solid var(--line);border-radius:20px;box-shadow:0 30px 60px -20px rgba(14,34,64,.28),0 2px 6px rgba(14,34,64,.06);overflow:hidden;max-width:520px;margin-left:auto;width:100%}
.pack-search{display:flex;align-items:center;gap:10px;margin:16px;padding:12px 16px;border:1px solid var(--line);border-radius:999px;font-size:.98rem;color:var(--ink)}
.pack-search svg{width:18px;height:18px;color:var(--muted)}
.pack-map{height:150px;background:#E9F0EE;position:relative}
.pack-map svg{width:100%;height:100%}
.pack-list{position:relative;height:246px;margin:0;padding:0;list-style:none}
.pack-row{position:absolute;left:0;right:0;height:82px;padding:12px 18px;display:grid;grid-template-columns:34px 1fr auto;gap:12px;align-items:center;border-top:1px solid var(--line);background:#fff;transition:top .9s cubic-bezier(.65,0,.25,1),background .5s}
.pack-row .pos{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font:700 .9rem/1 var(--display);background:var(--mint);color:var(--ink)}
.pack-row .nm{font-weight:600;color:var(--ink);font-size:.98rem;line-height:1.25}
.pack-row .meta{font-size:.82rem;color:var(--muted)}
.pack-row .stars{color:var(--star);letter-spacing:1px}
.pack-row .act{font-size:.8rem;font-weight:600;color:var(--teal-d);border:1px solid var(--line);border-radius:999px;padding:6px 10px;white-space:nowrap}
.pack-row.you{background:#FFF8EC}
.pack-row.you .pos{background:var(--saffron)}
.pack-row.you .tag{display:inline-block;font-size:.72rem;font-weight:700;background:var(--ink);color:#fff;border-radius:6px;padding:2px 7px;margin-left:6px;vertical-align:2px}
.r-a{top:0}.r-b{top:82px}.r-c{top:164px}
.ranked .r-c{top:0}.ranked .r-a{top:82px}.ranked .r-b{top:164px}
@media (max-width:560px){.pack-list{height:300px}.pack-row{height:100px;padding:12px 14px;grid-template-columns:30px 1fr}.pack-row .act{display:none}
.r-b{top:100px}.r-c{top:200px}.ranked .r-a{top:100px}.ranked .r-b{top:200px}}
.pack-cap{font-size:.82rem;color:var(--muted);text-align:right;margin:10px 4px 0;max-width:none}

/* problem */
.leaks{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:44px;border-top:2px solid var(--ink)}
.leak{padding:28px 28px 8px 0}
.leak+.leak{padding-left:28px;border-left:1px solid var(--line)}
.leak .big{font:800 3rem/1 var(--display);color:var(--teal);margin-bottom:14px;letter-spacing:-.03em}
@media (max-width:860px){.leaks{grid-template-columns:1fr}.leak+.leak{padding-left:0;border-left:0;border-top:1px solid var(--line)}}

/* patient path */
.path{list-style:none;margin:48px 0 0;padding:0;display:grid;grid-template-columns:repeat(5,1fr);gap:0;counter-reset:step;position:relative}
.path::before{content:"";position:absolute;left:0;right:0;top:23px;height:2px;background:var(--mint-2)}
.path li{position:relative;padding:0 18px 0 0}
.path .dot{width:48px;height:48px;border-radius:50%;background:var(--paper);border:2px solid var(--teal);display:grid;place-items:center;font:700 1.05rem/1 var(--display);color:var(--teal);position:relative;margin-bottom:18px}
.path li:last-child .dot{background:var(--saffron);border-color:var(--saffron);color:var(--ink)}
.path h3{font-size:1.1rem;margin-bottom:.4em}
.path .lose{font-size:.9rem;color:var(--bad);margin:0 0 .5em}
.path .fix{font-size:.92rem;margin:0}
@media (max-width:960px){
  .path{grid-template-columns:1fr;gap:26px}
  .path::before{left:23px;right:auto;top:0;bottom:0;width:2px;height:auto}
  .path li{padding:0 0 0 70px}
  .path .dot{position:absolute;left:0;top:0}
}

/* services */
.svc-grid{display:grid;grid-template-columns:1.25fr 1fr;gap:22px;margin-top:44px}
.svc{background:#fff;border:1px solid var(--line);border-radius:18px;padding:30px;display:flex;flex-direction:column}
.svc.lead{grid-row:span 2;background:var(--ink);border-color:var(--ink);color:#C9D5E4}
.svc.lead h3{color:#fff;font-size:1.7rem}
.svc.lead ul{margin:6px 0 24px;padding-left:1.1em}
.svc.lead li{margin:.35em 0}
.svc p{margin-bottom:.8em}
.svc .more{margin-top:auto;font-weight:600}
.svc.lead .more{color:var(--saffron)}
.svc-ico{width:40px;height:40px;margin-bottom:16px;color:var(--teal)}
.svc.lead .svc-ico{color:var(--saffron)}
.svc.wide{grid-column:1/-1;display:grid;grid-template-columns:auto 1fr auto;gap:8px 28px;align-items:center}
.svc.wide .svc-ico{margin:0}.svc.wide h3,.svc.wide p{margin:0}.svc.wide .more{margin:0}
@media (max-width:860px){.svc-grid{grid-template-columns:1fr}.svc.lead{grid-row:auto}.svc.wide{display:flex}.svc.wide .svc-ico{margin-bottom:16px}.svc.wide p{margin-bottom:.8em}}

/* calculator */
.calc{display:grid;grid-template-columns:1fr 1fr;gap:0;background:#fff;border-radius:20px;overflow:hidden;border:1px solid var(--line);margin-top:40px}
.calc-in{padding:34px}
.calc-out{padding:34px;background:var(--ink);color:#C9D5E4;display:flex;flex-direction:column;justify-content:center}
.field{margin-bottom:22px}
.field label{display:block;font-weight:600;color:var(--ink);margin-bottom:8px}
.field .hint{font-size:.85rem;color:var(--muted);margin-top:6px}
.field input[type=range]{width:100%;accent-color:var(--teal)}
.field output{font:700 1.3rem/1 var(--display);color:var(--ink);float:right}
.calc-out .num{font:800 clamp(2.6rem,5vw,3.6rem)/1 var(--display);color:#fff;letter-spacing:-.03em;margin:8px 0 6px}
.calc-out .num.sub{font-size:1.6rem;color:var(--saffron)}
@media (max-width:860px){.calc{grid-template-columns:1fr}}

/* founder / proof */
.split{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start}
@media (max-width:900px){.split{grid-template-columns:1fr;gap:40px}}
.facts{list-style:none;padding:0;margin:26px 0 0;display:grid;gap:14px}
.facts li{display:grid;grid-template-columns:28px 1fr;gap:10px;align-items:start}
.facts svg{width:22px;height:22px;color:var(--teal);margin-top:3px}

/* report mockup */
.report{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px;box-shadow:0 24px 50px -24px rgba(14,34,64,.25)}
.report-head{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:18px}
.report-head b{font-family:var(--display);color:var(--ink);font-size:1.1rem}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.kpi{background:var(--paper);border-radius:12px;padding:14px}
.kpi .v{font:800 1.7rem/1.1 var(--display);color:var(--ink)}
.kpi .l{font-size:.78rem;color:var(--muted);line-height:1.3}
.kpi .d{font-size:.8rem;font-weight:600;color:var(--good)}
.grid-title{font-weight:600;color:var(--ink);font-size:.92rem;margin-bottom:8px}
.geo{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;max-width:330px}
.geo span{aspect-ratio:1;border-radius:50%;display:grid;place-items:center;font:700 .78rem/1 var(--display);color:#fff}
.g1{background:var(--good)}.g2{background:#58A86F}.g3{background:var(--warn)}.g4{background:var(--bad)}
.report .small{margin:12px 0 0}

/* steps (timeline) */
.timeline{list-style:none;padding:0;margin:44px 0 0;display:grid;grid-template-columns:repeat(4,1fr);gap:22px}
.timeline li{border-top:4px solid var(--teal);padding-top:18px}
.timeline .when{font:700 .95rem/1 var(--display);color:var(--teal-d);margin-bottom:10px;display:block}
@media (max-width:900px){.timeline{grid-template-columns:1fr 1fr}}
@media (max-width:560px){.timeline{grid-template-columns:1fr}}

/* faq */
.faq{max-width:820px;margin-top:36px}
.faq details{border-bottom:1px solid var(--line);padding:4px 0}
.faq summary{cursor:pointer;list-style:none;padding:18px 40px 18px 0;font:700 1.12rem/1.35 var(--display);color:var(--ink);position:relative}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:6px;top:14px;font-size:1.6rem;color:var(--teal);transition:transform .2s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{margin:0 0 20px}

/* cta band */
.band{background:var(--teal);color:#E8F4F2;padding:72px 0}
.band h2{color:#fff;max-width:20ch}
.band .wrap{display:flex;justify-content:space-between;align-items:center;gap:30px;flex-wrap:wrap}
.band .btn-primary{font-size:1.06rem}

/* service pages */
.page-hero{padding:60px 0 64px;border-bottom:1px solid var(--line)}
.crumbs{font-size:.88rem;color:var(--muted);margin-bottom:18px}
.crumbs a{color:var(--muted)}
.incl{display:grid;grid-template-columns:1fr 1fr;gap:26px 48px;margin-top:40px;list-style:none;padding:0}
.incl li{padding-left:34px;position:relative}
.incl li::before{content:"";position:absolute;left:0;top:6px;width:20px;height:20px;border-radius:6px;background:var(--mint-2) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M5 10.5l3 3 7-7' fill='none' stroke='%23127C76' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/16px no-repeat}
.incl h3{font-size:1.1rem;margin-bottom:.3em}
.incl p{margin:0;font-size:.97rem}
@media (max-width:760px){.incl{grid-template-columns:1fr}}
.side-note{background:var(--mint);border-left:4px solid var(--teal);padding:20px 24px;border-radius:0 12px 12px 0;margin:30px 0 0;max-width:760px}
.side-note p{margin:0}
.related{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:30px}
.related a{display:block;padding:22px;border:1px solid var(--line);border-radius:14px;background:#fff;text-decoration:none;color:var(--ink-2)}
.related a:hover{border-color:var(--teal)}
.related b{display:block;font-family:var(--display);color:var(--ink);font-size:1.1rem;margin-bottom:4px}
@media (max-width:760px){.related{grid-template-columns:1fr}}
.kw-table{width:100%;border-collapse:collapse;margin-top:28px;font-size:.96rem;background:#fff;border-radius:14px;overflow:hidden}
.kw-table th,.kw-table td{text-align:left;padding:13px 16px;border-bottom:1px solid var(--line)}
.kw-table th{background:var(--ink);color:#fff;font-weight:600}
.kw-table td:first-child{font-weight:600;color:var(--ink)}

/* form */
.form-wrap{display:grid;grid-template-columns:1fr 1.1fr;gap:56px;align-items:start}
@media (max-width:900px){.form-wrap{grid-template-columns:1fr}}
form.card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:32px;box-shadow:0 24px 50px -28px rgba(14,34,64,.3)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:560px){.row2{grid-template-columns:1fr}}
.f{margin-bottom:18px}
.f label{display:block;font-weight:600;color:var(--ink);font-size:.95rem;margin-bottom:6px}
.f input,.f select,.f textarea{width:100%;font:400 1rem/1.4 var(--body);color:var(--ink);padding:13px 14px;border:1.5px solid #C2CFCC;border-radius:10px;background:#fff}
.f input:focus,.f select:focus,.f textarea:focus{border-color:var(--teal);outline:none;box-shadow:0 0 0 3px var(--mint-2)}
.f .opt{font-weight:400;color:var(--muted)}
form .btn{width:100%;justify-content:center;font-size:1.05rem;padding:18px}
.privacy-line{font-size:.82rem;color:var(--muted);margin:14px 0 0;text-align:center;max-width:none}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.form-err{background:#FBEAE8;border:1px solid #E7B5AF;color:#8E2F25;border-radius:10px;padding:12px 14px;margin-bottom:18px;font-weight:600;font-size:.95rem}
form .btn[disabled]{opacity:.7;cursor:wait}
.contact-cards{list-style:none;padding:0;margin:30px 0 0;display:grid;gap:14px}
.contact-cards li{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;display:grid;grid-template-columns:28px 1fr;gap:12px}
.contact-cards svg{width:22px;height:22px;color:var(--teal);margin-top:2px}
.contact-cards b{display:block;color:var(--ink)}

/* about */
.portrait{aspect-ratio:4/5;border-radius:20px;background:var(--ink);display:grid;place-items:center;color:var(--saffron);font:800 5rem/1 var(--display);overflow:hidden}
.portrait img{width:100%;height:100%;object-fit:cover;border-radius:0}

/* photos */
.ph{width:100%;height:100%;object-fit:cover;border-radius:20px;background:var(--mint-2)}
.stats{background:var(--ink);color:#C9D5E4;padding:44px 0}
.stats ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:24px}
.stats li{border-left:3px solid var(--saffron);padding-left:18px}
.stats b{display:block;font:800 clamp(1.9rem,3.4vw,2.6rem)/1.05 var(--display);color:#fff;letter-spacing:-.02em;margin-bottom:6px}
.stats span{font-size:.95rem;line-height:1.4;display:block}
@media (max-width:860px){.stats ul{grid-template-columns:1fr 1fr;gap:28px 18px}}
.front{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.front .collage{display:grid;grid-template-columns:1.25fr 1fr;grid-template-rows:220px 220px;gap:14px}
.front .collage .ph:first-child{grid-row:span 2}
@media (max-width:900px){.front{grid-template-columns:1fr;gap:36px}.front .collage{grid-template-rows:170px 170px}}
.who{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:40px}
.who article{background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;display:flex;flex-direction:column}
.who .ph{border-radius:0;height:200px}
.who .in{padding:24px 26px 26px;display:flex;flex-direction:column;flex:1}
.who .in p{margin-bottom:.9em}
.who .more{margin-top:auto;font-weight:600}
@media (max-width:900px){.who{grid-template-columns:1fr}}
.cmp{width:100%;border-collapse:separate;border-spacing:0;margin-top:36px;background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;font-size:.97rem}
.cmp th,.cmp td{padding:15px 18px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
.cmp tr:last-child td{border-bottom:0}
.cmp thead th{background:var(--paper);color:var(--ink);font-family:var(--display);font-size:1.02rem}
.cmp thead th.us{background:var(--ink);color:#fff}
.cmp td.us{background:#F2F8F7;color:var(--ink);font-weight:600}
.cmp td:first-child{color:var(--ink);font-weight:600;width:26%}
.cmp-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
@media (max-width:700px){.cmp{min-width:640px}}
.hero-ph{aspect-ratio:4/3;max-width:560px;margin-left:auto}
.page-hero.has-img .wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:56px;align-items:center}
@media (max-width:900px){.page-hero.has-img .wrap{grid-template-columns:1fr;gap:32px}.hero-ph{margin:0}}

/* footer */
.site-foot{background:var(--ink);color:#9FB0C6;padding:64px 0 34px;font-size:.95rem}
.foot-grid{display:grid;grid-template-columns:1.3fr 1fr .8fr 1.1fr;gap:36px}
.site-foot address{font-style:normal;margin:0 0 16px;line-height:1.55}
.site-foot address b{color:#fff;font-weight:600}
@media (max-width:1000px) and (min-width:761px){.foot-grid{grid-template-columns:1fr 1fr}}
.steps3{list-style:none;counter-reset:s;padding:0;margin:0 0 22px;display:grid;gap:10px}
.steps3 li{counter-increment:s;display:grid;grid-template-columns:30px 1fr;gap:10px;align-items:start;font-size:.95rem}
.steps3 li::before{content:counter(s);width:26px;height:26px;border-radius:50%;background:var(--mint-2);color:var(--teal-d);font-weight:700;display:grid;place-items:center;font-size:.85rem}
.ticks{columns:2;column-gap:40px;padding:0;list-style:none;margin:26px 0 0}
.ticks li{break-inside:avoid;padding-left:30px;position:relative;margin:0 0 12px}
.ticks li::before{content:"";position:absolute;left:0;top:7px;width:16px;height:16px;border-radius:5px;background:var(--mint-2)}
@media (max-width:760px){.ticks{columns:1}}
.extra-grid{display:grid;grid-template-columns:1.1fr 1fr;gap:56px;align-items:start}
@media (max-width:860px){.extra-grid{grid-template-columns:1fr;gap:28px}}
.price-line{margin:18px 0 0;font-size:.98rem;color:var(--muted)}.price-line b{color:var(--ink)}
.prices{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:34px}
.prices article{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px;display:flex;flex-direction:column}
.prices .amt{font-family:var(--display);font-weight:800;font-size:1.7rem;color:var(--ink);margin:2px 0 10px}
.prices p{font-size:.95rem;flex:1}
@media (max-width:1000px){.prices{grid-template-columns:1fr 1fr}}@media (max-width:560px){.prices{grid-template-columns:1fr}}
.rv-head{display:flex;justify-content:space-between;align-items:end;gap:24px;flex-wrap:wrap}
.rv-head .lede{margin:0}
.rv-badge{display:inline-block;background:var(--saffron);color:var(--ink);font-weight:700;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;padding:5px 10px;border-radius:999px;margin-bottom:14px}
.rv-note{background:#fff;border:1px dashed var(--saffron-d);border-radius:12px;padding:12px 16px;font-size:.92rem;color:var(--ink-2);margin:22px 0 0}
.rv-feature{margin:34px 0 18px;background:var(--ink);color:#DCE6F2;border-radius:20px;padding:40px 44px;display:grid;grid-template-columns:1fr auto;gap:32px;align-items:center}
.rv-feature blockquote{margin:0;font-family:var(--display);font-size:clamp(1.3rem,2.2vw,1.75rem);line-height:1.3;color:#fff;font-weight:600;letter-spacing:-.01em}
.rv-feature .who{display:flex;align-items:center;gap:14px;margin-top:22px}
.rv-feature .who b{color:#fff}.rv-feature .who span{color:#9FB0C6;font-size:.92rem}
.rv-feature .stat{text-align:center;border-left:1px solid #2A3C58;padding-left:32px}
.rv-feature .stat b{display:block;font-family:var(--display);font-size:2.6rem;color:var(--saffron);line-height:1}
.rv-feature .stat span{font-size:.88rem;color:#9FB0C6}
.reviews{columns:3 300px;column-gap:18px}
.rv{break-inside:avoid;margin:0 0 18px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px 24px 20px;position:relative}
.rv .stars{color:var(--star);letter-spacing:2px;font-size:1rem}
.rv h3{font-size:1.05rem;margin:10px 0 6px}
.rv blockquote{margin:0 0 18px;font-size:.98rem;line-height:1.6;color:var(--ink-2)}
.rv figcaption{display:flex;align-items:center;gap:12px;border-top:1px solid var(--line);padding-top:14px}
.av{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:.9rem;color:#fff;background:var(--teal);flex:none}
.av.a2{background:var(--ink)}.av.a3{background:var(--saffron-d)}
.rv figcaption b{display:block;color:var(--ink);font-size:.95rem;line-height:1.3}
.rv figcaption span{font-size:.85rem;color:var(--muted)}
.rv figcaption .av,.rv-feature .who .av{color:#fff;font-size:.9rem}
.rv .src{position:absolute;top:22px;right:22px;font-size:.75rem;font-weight:600;color:var(--teal-d);background:var(--mint);padding:3px 8px;border-radius:6px}
.rv .src.sample{color:var(--saffron-d);background:#FDF1DD}
@media (max-width:760px){.rv-feature{grid-template-columns:1fr;padding:30px 24px}.rv-feature .stat{border:0;padding:0;text-align:left}}
.offices-inline{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:26px}
.offices-inline address{font-style:normal;background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px;font-size:.95rem}
@media (max-width:560px){.offices-inline{grid-template-columns:1fr}}
.site-foot .logo{color:#fff;margin-bottom:14px}
.site-foot h4{color:#fff;font-size:1rem;margin-bottom:12px}
.site-foot ul{list-style:none;margin:0;padding:0}
.site-foot li{margin:8px 0}
.site-foot a{color:#C9D5E4;text-decoration:none}
.site-foot a:hover{color:#fff;text-decoration:underline}
.foot-base{border-top:1px solid #23395A;margin-top:44px;padding-top:22px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-size:.85rem}
@media (max-width:760px){.foot-grid{grid-template-columns:1fr}}
.prose{max-width:760px}.prose h2{font-size:1.6rem;margin-top:1.6em}
"""

# ---------------------------------------------------------------- icons
def ico(name):
    p = {
        "check": '<path d="M5 12.5l4 4 10-10" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
        "search": '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 10-14 0c0 5.8 7 12 7 12z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2.6" fill="currentColor"/>',
        "screen": '<rect x="3" y="4" width="18" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 21h8M12 17v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        "tooth": '<path d="M7 3c-2.5 0-4 2-4 4.6 0 3 1.4 4.4 2 7 .6 3 1 6.4 2.6 6.4 1.8 0 1.6-4.4 4.4-4.4s2.6 4.4 4.4 4.4c1.6 0 2-3.4 2.6-6.4.6-2.6 2-4 2-7C21 5 19.5 3 17 3c-2 0-3 1.2-5 1.2S9 3 7 3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
        "chart": '<path d="M4 20V4M4 20h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M7 15l4-4 3 3 5-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
        "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" fill="currentColor"/>',
        "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M8.5 12l2.5 2.5 4.5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        "clock": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    }[name]
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg>'

LOGO = ('<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#0E2240"/>'
        '<path d="M11 12l9 8 9-8" fill="none" stroke="#2BB3A8" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M11 21l9 8 9-8" fill="none" stroke="#F2A93B" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="10" fill="#0E2240"/>'
           '<path d="M11 12l9 8 9-8" fill="none" stroke="#2BB3A8" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
           '<path d="M11 21l9 8 9-8" fill="none" stroke="#F2A93B" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

UNS = "https://images.unsplash.com/"
def photo(pid, alt, w=1200, h=900, cls="ph", eager=False):
    src = f"{UNS}{pid}?auto=format&fit=crop&w={w}&h={h}&q=72"
    src2 = f"{UNS}{pid}?auto=format&fit=crop&w={w*2}&h={h*2}&q=60"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img class="{cls}" src="{src}" srcset="{src} 1x, {src2} 2x" alt="{html.escape(alt)}" width="{w}" height="{h}" {load}>'

IMG = {
  "aligners": ("photo-1564420228450-d9a5bc8d6565", "Hands holding clear aligners and a storage case"),
  "consult": ("photo-1777331903190-341a3dd0441b", "Dentist talking with a patient in a modern dental office"),
  "office": ("photo-1629909613654-28e377c37b09", "Modern dental treatment room with chair and equipment"),
  "room": ("photo-1704455306251-b4634215d98f", "Bright dental practice room with a desk and chairs"),
  "braces": ("photo-1598256989809-394fa4f6cd26", "Close up of a smile with metal braces"),
  "bracesmodel": ("photo-1720685193942-5a1c5ac7fd80", "Dental model with braces"),
  "endo": ("photo-1588776814546-daab30f310ce", "Two dentists performing a procedure on a patient"),
  "exam": ("photo-1667133295352-ef4c83620e8e", "Dentist examining a patient with a dental mirror"),
  "waiting": ("photo-1762625570087-6d98fca29531", "Modern waiting room with chairs"),
  "smile": ("photo-1773243906614-875ddb4918b6", "Young man smiling at the camera"),
}
def P(key, **kw):
    pid, alt = IMG[key]; return photo(pid, alt, **kw)

NAV = [
    ("/orthodontist-seo/", "Orthodontist SEO"),
    ("/google-business-profile-optimization/", "Google Business Profile"),
    ("/orthodontic-website-design/", "Website design"),
    ("/endodontist-marketing/", "Endodontists"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
]

def header(path):
    def li(href, label):
        cur = ' aria-current="page"' if href == path else ""
        return f'<li><a href="{href}"{cur}>{label}</a></li>'
    items = "".join(li(h, l) for h, l in NAV)
    cta = f'<li><a class="btn btn-primary" href="/free-audit/">Get a free audit</a></li>'
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap head-in">
<a class="logo" href="/" aria-label="{CONFIG["brand"]} home">{LOGO}<span>{CONFIG["brand"]}</span></a>
<nav aria-label="Main"><ul class="nav-desktop">{items}{cta}</ul>
<details class="menu"><summary>Menu</summary><ul>{items}{cta}</ul></details></nav>
</div></header>'''

def footer():
    extra = ""
    if CONFIG["linkedin"]:
        extra += f'<li><a href="{CONFIG["linkedin"]}" rel="me noopener">LinkedIn</a></li>'
    if CONFIG["upwork"]:
        extra += f'<li><a href="{CONFIG["upwork"]}" rel="me noopener">Upwork profile</a></li>'
    return f'''<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div><a class="logo" href="/">{LOGO}<span>{CONFIG["brand"]}</span></a>
<p>Local SEO, Google Business Profile optimization and conversion-focused websites for orthodontic and endodontic practices in the United States.</p>
<p><a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a><br>Small team, working US business hours.</p></div>
<div><h4>Services</h4><ul>
<li><a href="/orthodontist-seo/">SEO for orthodontists</a></li>
<li><a href="/google-business-profile-optimization/">Google Business Profile optimization</a></li>
<li><a href="/orthodontic-website-design/">Orthodontic website design</a></li>
<li><a href="/endodontist-marketing/">Endodontist marketing</a></li></ul></div>
<div><h4>Company</h4><ul>
<li><a href="/about/">About</a></li>
<li><a href="/free-audit/">Free practice audit</a></li>
<li><a href="/contact/">Contact</a></li>
<li><a href="/privacy-policy/">Privacy policy</a></li>{extra}</ul></div>
<div><h4>Offices</h4>{"".join(office_html(o) for o in OFFICES)}</div>
</div>
<div class="foot-base"><span>&copy; {date.today().year} {CONFIG["brand"]}. All rights reserved.</span><span>Practice names shown in examples are fictional.</span></div>
</div></footer>'''

ORG_ID = S + "/#organization"
ORG = {
    "@type": "ProfessionalService",
    "@id": ORG_ID,
    "name": CONFIG["brand"],
    "url": S + "/",
    "logo": S + "/logo-512.png",
    "image": S + "/og-image.png",
    "email": CONFIG["email"],
    "telephone": OFFICES[0]["phone"],
    "address": [{"@type": "PostalAddress", "streetAddress": o["street"], "addressLocality": o["city"],
                 **({"addressRegion": o["region"]} if o["region"] else {}), "postalCode": o["postal"],
                 "addressCountry": o["country"]} for o in OFFICES],
    "contactPoint": [{"@type": "ContactPoint", "telephone": o["phone"], "contactType": "sales",
                      "email": CONFIG["email"], "areaServed": "US"} for o in OFFICES],
    "description": "Dental marketing agency providing local SEO, Google Business Profile optimization and website design for orthodontists and endodontists in the United States.",
    "areaServed": {"@type": "Country", "name": "United States"},
    "founder": {"@type": "Person", "name": CONFIG["founder"], "url": S + "/about/"},
    "knowsAbout": ["Orthodontist SEO", "Dental SEO", "Google Business Profile optimization", "Local SEO",
                   "Orthodontic website design", "Endodontist marketing", "Conversion rate optimization"],
    "sameAs": [u for u in [CONFIG["linkedin"], CONFIG["upwork"]] if u],
}

def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def crumbs_schema(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": S + p} for i, (n, p) in enumerate(trail)]}

def service_schema(name, desc, path, stype, pkey=None):
    return {"@type": "Service", "name": name, "serviceType": stype, "description": desc,
            "provider": {"@id": ORG_ID}, "areaServed": {"@type": "Country", "name": "United States"},
            "url": S + path,
            **({"offers": {"@type": "Offer", "priceCurrency": "USD", "price": PRICES[pkey]["from"],
                "description": "Starting price, " + PRICES[pkey]["note"]}} if pkey else {})}

def faq_html(faqs):
    return '<div class="faq">' + "".join(
        f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in faqs) + "</div>"

def crumbs_html(trail):
    parts = [f'<a href="{p}">{n}</a>' for n, p in trail[:-1]] + [trail[-1][0]]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"

FONTS = ('<link rel="preconnect" href="https://images.unsplash.com"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">')

def page(path, title, desc, body, schema=None, noindex=False, script="", og="og-image.png"):
    graph = [ORG, {"@type": "WebSite", "@id": S + "/#website", "url": S + "/", "name": CONFIG["brand"], "publisher": {"@id": ORG_ID}}]
    graph += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    robots = '<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    canon = S + path
    doc = f'''<!doctype html>
<html lang="en-US">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-48HJDGG4NW"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-48HJDGG4NW');
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{robots}
<link rel="canonical" href="{canon}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#0E2240">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{CONFIG["brand"]}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{S}/{og}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{S}/{og}">
{FONTS}
<style>{CSS}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
{script}
</body>
</html>'''
    if path.endswith(".html"):
        os.makedirs(OUT, exist_ok=True)
        fn = os.path.join(OUT, path.strip("/"))
    else:
        d = os.path.join(OUT, path.strip("/"))
        os.makedirs(d, exist_ok=True)
        fn = os.path.join(d, "index.html")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(doc)
    return path

FORM_ERR = '<div class="form-err" role="alert" hidden id="formErr"></div>'
FORM_JS = """<script>
(function(){
  var e=new URLSearchParams(location.search).get('error'),box=document.getElementById('formErr');
  var msg={missing:'Please fill in all required fields and try again.',email:'Please enter a valid email address.',server:'Something went wrong on our side. Please try again, or email us directly.'};
  if(e&&box&&msg[e]){box.textContent=msg[e];box.hidden=false;box.scrollIntoView({block:'center'});}
  document.querySelectorAll('form[action="/api/lead"]').forEach(function(f){f.addEventListener('submit',function(){var b=f.querySelector('button[type=submit]');if(b){b.disabled=true;b.textContent='Sending...';}});});
})();
</script>"""

def cta_band(h="Find out what is holding your practice back on Google.", sub="A free, recorded audit of your map rankings, Google Business Profile and website. No sales call needed to get it."):
    return f'''<section class="band"><div class="wrap"><div><h2>{h}</h2><p style="color:#E8F4F2;margin:0">{sub}</p></div>
<a class="btn btn-primary" href="/free-audit/">Get your free practice audit</a></div></section>'''

# ---------------------------------------------------------------- HOME
MAP_SVG = '''<svg viewBox="0 0 520 150" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<rect width="520" height="150" fill="#E6EFEC"/>
<path d="M0 98 C120 80 200 120 320 92 S470 60 520 70" stroke="#fff" stroke-width="14" fill="none"/>
<path d="M140 0 L180 150 M360 0 L330 150 M0 38 L520 30" stroke="#fff" stroke-width="8" fill="none"/>
<path d="M0 98 C120 80 200 120 320 92 S470 60 520 70" stroke="#F6D78F" stroke-width="5" fill="none"/>
<rect x="400" y="96" width="90" height="44" rx="8" fill="#CFE5D6"/><rect x="30" y="112" width="70" height="30" rx="8" fill="#CFE5D6"/>
<g font-family="Bricolage Grotesque, sans-serif" font-weight="700" font-size="13">
<g transform="translate(245 54)"><path d="M0 26 C-14 12 -14 -2 0 -6 C14 -2 14 12 0 26z" fill="#F2A93B" stroke="#0E2240" stroke-width="2"/><text x="0" y="11" font-size="11" text-anchor="middle" fill="#0E2240">1</text></g>
<g transform="translate(110 64)"><path d="M0 26 C-14 12 -14 -2 0 -6 C14 -2 14 12 0 26z" fill="#127C76"/><text x="0" y="11" font-size="11" text-anchor="middle" fill="#fff">2</text></g>
<g transform="translate(405 46)"><path d="M0 26 C-14 12 -14 -2 0 -6 C14 -2 14 12 0 26z" fill="#127C76"/><text x="0" y="11" font-size="11" text-anchor="middle" fill="#fff">3</text></g>
</g></svg>'''

def pack_row(cls, pos, name, rating, reviews, meta, you=False):
    tag = '<span class="tag">Your practice</span>' if you else ""
    return f'''<li class="pack-row {cls}{" you" if you else ""}"><span class="pos" data-pos>{pos}</span>
<div><div class="nm">{name}{tag}</div><div class="meta"><span class="stars" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span> {rating} ({reviews}) <br>{meta}</div></div>
<span class="act">Call</span></li>'''

HOME_FAQ = [
    ("How long does SEO take to work for an orthodontic practice?",
     "Google Business Profile fixes often show movement in the map pack within 4 to 8 weeks. Organic rankings for competitive terms like orthodontist near me or Invisalign in your city usually take 3 to 6 months, depending on your competition and how much work your site needs."),
    ("Do you work with competing practices in the same area?",
     "No. We take one orthodontic practice per local market, so we are never ranking you against another client of ours."),
    ("What do you need from us to get started?",
     "Manager access to your Google Business Profile, access to your website and Google Search Console if you have it, and 30 minutes with you or your office manager to understand your treatments, ideal patients and service area."),
    ("Is your work HIPAA conscious?",
     "Yes. Our marketing forms only ask for contact details and the treatment a person is interested in, never health history. We never put patient information into analytics or ad platforms, and we can set up HIPAA compliant form tools when your practice needs them."),
    ("Are we locked into a long contract?",
     "No. Monthly SEO and Google Business Profile work runs month to month after the first 90 days, because results should be the reason you stay."),
    ("How much does orthodontist marketing cost?",
     "Orthodontist SEO starts at $1,500 per month per location with Google Business Profile included, profile management alone starts at $500 per month, and new practice websites start at $4,500. Everything runs month to month after the first 90 days."),
    ("Do you also work with endodontists?",
     "Yes. Endodontic practices get a version of our program built around referral relationships and urgent searches like root canal near me or emergency endodontist."),
]

def reviews_section(items, sample=False, metric=None):
    if not items: return ""
    def stars(n=5): return '<span class="stars" aria-label="' + str(n) + ' out of 5 stars">' + "&#9733;" * n + "</span>"
    def initials(n): return "".join(w[0] for w in n.replace("Dr. ", "").split()[:2]).upper()
    src = lambda r: '<span class="src sample">Sample</span>' if sample else (f'<span class="src">{html.escape(r["source"])}</span>' if r.get("source") else "")
    first, rest = items[0], items[1:]
    feat = (f'<div class="rv-feature"><div>{stars()}<blockquote>&ldquo;{html.escape(first["quote"])}&rdquo;</blockquote>'
            f'<div class="who"><span class="av a3">{initials(first["name"])}</span><div><b>{html.escape(first["name"])}</b><br><span>{html.escape(first["role"])}, {html.escape(first["place"])}</span></div></div></div>'
            + (f'<div class="stat"><b>{metric[0]}</b><span>{metric[1]}</span></div>' if metric else "") + '</div>')
    cards = "".join(
        f'<figure class="rv">{src(r)}{stars(r.get("stars", 5))}' + (f'<h3>{html.escape(r["title"])}</h3>' if r.get("title") else "")
        + f'<blockquote>{html.escape(r["quote"])}</blockquote><figcaption><span class="av {["","a2","a3"][i % 3]}">{initials(r["name"])}</span>'
        f'<div><b>{html.escape(r["name"])}</b><span>{html.escape(r["role"])}, {html.escape(r["place"])}</span></div></figcaption></figure>'
        for i, r in enumerate(rest))
    badge = '<span class="rv-badge">Design preview</span>' if sample else ""
    note = ('<p class="rv-note"><b>Sample content.</b> These reviews are placeholders written to show the layout. '
            'They are not from real clients and will be replaced with genuine, approved testimonials before this section goes live.</p>') if sample else ""
    return (f'<section class="tint" id="reviews"><div class="wrap">{badge}<div class="rv-head"><div><h2>What practices say.</h2>'
            f'<p class="lede">Orthodontists and endodontists on working with {CONFIG["brand"]}.</p></div>'
            f'<a class="btn btn-ghost" href="/free-audit/">Get your free practice audit</a></div>{note}{feat}<div class="reviews">{cards}</div></div></section>')

SAMPLE_REVIEWS = [
    {"name": "Dr. Sample A", "role": "Orthodontist", "place": "Texas", "quote": "We went from page two of the map results to the top three for orthodontist near me in our main town, and the monthly report finally shows which calls came from Google."},
    {"name": "Office Manager", "role": "Orthodontic practice", "place": "Florida", "title": "Reporting we actually read", "quote": "Every month we get a short report with calls, consult requests and the map grid. It takes five minutes to read and tells us exactly what changed."},
    {"name": "Dr. Sample B", "role": "Endodontist", "place": "Arizona", "title": "Referrals got easier", "quote": "The new referral form saves our referring offices a phone call. Dentists send patients through the website now, and the front desk spends less time chasing paperwork."},
    {"name": "Practice Owner", "role": "Orthodontics, 2 locations", "place": "Ohio", "title": "Both offices ranking", "quote": "Each location finally has its own page and its own Google profile set up properly. Our second office started showing up for searches it never appeared in before."},
    {"name": "Dr. Sample C", "role": "Orthodontist", "place": "Georgia", "title": "Website that books", "quote": "The redesign kept our rankings through launch and the consult form is much shorter. Parents tell us the site was easy to use on their phone."},
    {"name": "Marketing Lead", "role": "Orthodontic group", "place": "California", "title": "Straight answers", "quote": "No jargon and no long contract. When something was not working, we heard about it before we had to ask."},
    {"name": "Dr. Sample D", "role": "Orthodontist", "place": "North Carolina", "title": "Profile that wins the click", "quote": "Our Google profile used to have old photos and half our treatments missing. Now it is complete, active every week, and the review routine is easy for our team."},
    {"name": "Office Manager", "role": "Endodontic practice", "place": "Colorado", "title": "Urgent calls", "quote": "We show up for root canal searches in our area and the click to call setup works. More same day calls come straight from our Google listing."},
    {"name": "Dr. Sample E", "role": "Orthodontist", "place": "Illinois", "title": "One practice per market", "quote": "Knowing they will not work with the practice down the road mattered to us. It feels like a partner, not a vendor."},
    {"name": "Practice Owner", "role": "Orthodontics", "place": "Washington", "title": "Clear first 90 days", "quote": "The audit showed us exactly where we were losing patients, and the first 90 days followed the plan we were shown on day one."},
]
home_body = f'''
<section class="hero"><div class="wrap hero-grid">
<div>
<h1>Orthodontist marketing that books more consults straight from Google.</h1>
<p class="lede">Dive Dive Digital is an orthodontist marketing agency for practices that want more consult requests from Google. We combine local SEO, Google Business Profile optimization and conversion focused website work, and we take one orthodontic practice per local market.</p>
<div class="cta-row"><a class="btn btn-primary" href="/free-audit/">Get your free practice audit</a><a class="btn btn-ghost" href="#how">See how it works</a></div>
<ul class="proof-strip">
<li>{ico("check")}Specialist dental practices only</li>
<li>{ico("check")}One practice per local market</li>
<li>{ico("check")}Month to month after 90 days</li>
<li>{ico("check")}Building websites since 2014</li>
</ul>
</div>
<div>
<div class="pack" id="pack" aria-label="Illustration of a Google map pack where your practice moves from third to first place">
<div class="pack-search">{ico("search")}<span>orthodontist near me</span></div>
<div class="pack-map">{MAP_SVG}</div>
<ol class="pack-list">
{pack_row("r-a","1","Summit Smiles Orthodontics","4.8","212","Braces and clear aligners, 1.2 mi")}
{pack_row("r-b","2","Parkside Braces &amp; Aligners","4.6","98","Open until 6 PM, 2.0 mi")}
{pack_row("r-c","3","Brightline Orthodontics","4.9","341","Free consultations, 0.8 mi", you=True)}
</ol>
</div>
<p class="pack-cap">Illustrative example. Practice names are fictional.</p>
</div>
</div></section>

<section class="stats" aria-label="Experience at a glance"><div class="wrap"><ul>
<li><b>10+</b><span>US orthodontic and endodontic practices worked with</span></li>
<li><b>Since 2014</b><span>building and optimizing websites</span></li>
<li><b>Since 2018</b><span>Top Rated on Upwork, including healthcare clients</span></li>
<li><b>1 per market</b><span>we never rank you against another client of ours</span></li>
</ul></div></section>

<section><div class="wrap front">
<div class="collage">{P("consult", w=700, h=900)}{P("aligners", w=600, h=440)}{P("smile", w=600, h=440)}</div>
<div>
<h2>Your Google profile and website are your new front desk.</h2>
<p class="lede">Before a parent calls about braces, they have already seen your photos, read your reviews and decided whether your practice feels right.</p>
<p>We make sure that first impression matches the care you give in the chair: real team and office photos, complete treatment information, fresh reviews and a website that makes booking a consultation feel easy.</p>
<div class="cta-row"><a class="btn btn-ghost" href="/google-business-profile-optimization/">See how we optimize profiles</a></div>
</div>
</div></section>

<section class="tint"><div class="wrap">
<h2>Most practices lose new patients in three quiet places.</h2>
<p class="lede">Parents and adults searching for braces or Invisalign decide fast. They compare three practices in the map pack, skim reviews, tap a website, and call whoever makes it easiest.</p>
<div class="leaks">
<div class="leak"><div class="big">Map pack</div><h3>You are not in the top three</h3><p>Around three practices get most of the calls from a local search. If your Google Business Profile has the wrong categories, thin services and few fresh reviews, you sit below the fold on a phone.</p></div>
<div class="leak"><div class="big">Profile</div><h3>Your profile does not convince</h3><p>Old photos, no treatment details, missing services and a review count that lags competitors. People compare profiles side by side, and the more complete one wins the tap.</p></div>
<div class="leak"><div class="big">Website</div><h3>Your site does not book</h3><p>Slow pages on mobile, a buried phone number, no clear price or free consult offer, and a contact form that asks too much. Visitors leave and call the next practice.</p></div>
</div>
</div></section>

<section id="how"><div class="wrap">
<h2>We fix the whole path from search to booked consult.</h2>
<p class="lede">Rankings alone do not fill a schedule. We work on every step a new patient takes, and we measure what comes out at the end.</p>
<ol class="path">
<li><span class="dot">1</span><h3>Search</h3><p class="lose">Not showing for treatment searches</p><p class="fix">Keyword map for braces, Invisalign, early treatment and your towns.</p></li>
<li><span class="dot">2</span><h3>Map pack</h3><p class="lose">Ranked fourth or lower</p><p class="fix">Categories, services, citations and local signals tuned to your area.</p></li>
<li><span class="dot">3</span><h3>Profile</h3><p class="lose">Profile loses the comparison</p><p class="fix">Photos, posts, services, offers and reviews.</p></li>
<li><span class="dot">4</span><h3>Website</h3><p class="lose">Visitors bounce on mobile</p><p class="fix">Fast pages, clear offer, click to call and a short consult form.</p></li>
<li><span class="dot">5</span><h3>Consult booked</h3><p class="lose">No idea which channel worked</p><p class="fix">Call tracking and form tracking so you see real new patient numbers.</p></li>
</ol>
</div></section>

<section class="tint"><div class="wrap">
<h2>Services built for specialist practices.</h2>
<div class="svc-grid">
<article class="svc lead">{ico("chart").replace("<svg", '<svg class="svc-ico"')}<h3>SEO for orthodontists</h3>
<p>A complete local SEO program that gets your practice found for the treatments patients actually search for, in the towns you actually serve.</p>
<ul><li>Treatment pages for braces, Invisalign, clear aligners and early treatment</li><li>City and neighborhood pages that are useful, not copy and paste</li><li>Technical fixes, site speed and schema markup</li><li>Local citations and links from real community sources</li><li>Monthly reporting on calls, forms and map positions</li></ul>
<a class="more" href="/orthodontist-seo/">How orthodontist SEO works</a></article>
<article class="svc">{ico("pin").replace("<svg", '<svg class="svc-ico"')}<h3>Google Business Profile optimization</h3><p>Rank higher in the map pack and win the side by side comparison with a complete, active profile and a review system your team can run in minutes.</p><a class="more" href="/google-business-profile-optimization/">See what we optimize</a></article>
<article class="svc">{ico("screen").replace("<svg", '<svg class="svc-ico"')}<h3>Orthodontic website design</h3><p>A fast, modern site designed by a conversion specialist, with every page built to turn a curious parent into a booked consultation.</p><a class="more" href="/orthodontic-website-design/">View the website process</a></article>
<article class="svc wide">{ico("tooth").replace("<svg", '<svg class="svc-ico"')}<div><h3>Endodontist marketing</h3><p>Show up for urgent root canal searches and make it easy for referring dentists to send patients your way.</p></div><a class="more" href="/endodontist-marketing/">Marketing for endodontists</a></article>
</div>
</div></section>

<section><div class="wrap">
<h2>Who we work with.</h2>
<p class="lede">Specialist practices where a single new patient is worth a lot, and where local search decides who gets the call.</p>
<div class="who">
<article>{P("braces", w=800, h=400)}<div class="in"><h3>Orthodontists</h3><p>Single and multi-doctor practices offering braces, Invisalign and early treatment, competing for parents and adults in a 10 to 20 mile radius.</p><a class="more" href="/orthodontist-seo/">SEO for orthodontists</a></div></article>
<article>{P("endo", w=800, h=400)}<div class="in"><h3>Endodontists</h3><p>Practices that need to show up for urgent root canal searches and stay the easy choice for referring dentists.</p><a class="more" href="/endodontist-marketing/">Endodontist marketing</a></div></article>
<article>{P("office", w=800, h=400)}<div class="in"><h3>Multi-location groups</h3><p>Groups with several offices that need every location ranking on its own, with one clear report across all of them.</p><a class="more" href="/free-audit/">Audit all your locations</a></div></article>
</div>
</div></section>

<section class="tint"><div class="wrap">
<h2>How we compare.</h2>
<p class="lede">Most practices have tried a big dental marketing company or doing it in-house. Here is what changes with us.</p>
<div class="cmp-wrap"><table class="cmp">
<thead><tr><th scope="col"></th><th scope="col" class="us">{CONFIG["brand"]}</th><th scope="col">Typical dental agency</th><th scope="col">Doing it in-house</th></tr></thead>
<tbody>
<tr><td>Who does the work</td><td class="us">The specialist you speak with</td><td>Account manager, work passed to a team</td><td>Your office manager, between patients</td></tr>
<tr><td>What gets reported</td><td class="us">Calls, consult requests and map positions</td><td>Rankings and traffic</td><td>Usually nothing</td></tr>
<tr><td>Website conversion</td><td class="us">Included, built by a CRO specialist</td><td>Template site, rarely tested</td><td>Whatever the site already does</td></tr>
<tr><td>Competing clients</td><td class="us">One practice per local market</td><td>Often several in the same city</td><td>Not applicable</td></tr>
<tr><td>Contract</td><td class="us">Month to month after 90 days</td><td>12 month lock-in is common</td><td>None, but costs staff time</td></tr>
<tr><td>Who owns the assets</td><td class="us">You own your site, profile and data</td><td>Site sometimes stays with the agency</td><td>You</td></tr>
</tbody></table></div>
</div></section>

<section id="pricing"><div class="wrap">
<h2>Simple, published pricing.</h2>
<p class="lede">No setup traps or 12 month lock-ins. Every program runs month to month after the first 90 days, and the audit is free.</p>
<div class="prices">
<article><h3>Orthodontist SEO</h3><div class="amt">From {price_txt("seo")}</div><p>{PRICES["seo"]["note"][:1].upper()}{PRICES["seo"]["note"][1:]}. Treatment pages, technical SEO, citations and call tracking.</p><a class="more" href="/orthodontist-seo/">What is included</a></article>
<article><h3>Google Business Profile</h3><div class="amt">From {price_txt("gbp")}</div><p>{PRICES["gbp"]["note"][:1].upper()}{PRICES["gbp"]["note"][1:]}. Posts, photos, review replies and rank grids.</p><a class="more" href="/google-business-profile-optimization/">What is included</a></article>
<article><h3>Website design</h3><div class="amt">From {price_txt("web")}</div><p>{PRICES["web"]["note"][:1].upper()}{PRICES["web"]["note"][1:]}. Built for speed, SEO and booked consults.</p><a class="more" href="/orthodontic-website-design/">What is included</a></article>
<article><h3>Endodontist marketing</h3><div class="amt">From {price_txt("endo")}</div><p>{PRICES["endo"]["note"][:1].upper()}{PRICES["endo"]["note"][1:]}. Urgent search visibility and a dentist referral form.</p><a class="more" href="/endodontist-marketing/">What is included</a></article>
</div>
<p class="small" style="margin-top:18px">Prices in USD. Multi-location groups and very competitive metro areas are quoted after the free audit.</p>
</div></section>
{reviews_section(REVIEWS) if REVIEWS else reviews_section(SAMPLE_REVIEWS, sample=True, metric=("Top 3", "map pack position for the main search, example metric"))}
<section><div class="wrap">
<h2>What is one more case start worth to you?</h2>
<p class="lede">Orthodontic treatment is a high value decision, so a small lift in new patients goes a long way. Enter your own numbers.</p>
<div class="calc">
<div class="calc-in">
<div class="field"><label for="fee">Average treatment fee <output id="feeOut" for="fee">$5,500</output></label><input id="fee" type="range" min="2000" max="9000" step="250" value="5500"><div class="hint">Comprehensive braces or aligner case, your typical fee.</div></div>
<div class="field"><label for="starts">Extra case starts per month <output id="startsOut" for="starts">2</output></label><input id="starts" type="range" min="1" max="10" step="1" value="2"><div class="hint">New patients who start treatment because they found you on Google.</div></div>
</div>
<div class="calc-out" aria-live="polite">
<span>Added production per year</span>
<div class="num" id="yearOut">$132,000</div>
<span>Added production per month</span>
<div class="num sub" id="monthOut">$11,000</div>
<p class="small" style="color:#9FB0C6;margin:14px 0 0">Simple estimate: fee multiplied by extra starts. It does not include family referrals or retainer revenue.</p>
</div>
</div>
<div class="cta-row" style="margin-top:28px"><a class="btn btn-primary" href="/free-audit/">Get your free practice audit</a></div>
</div></section>

<section class="tint"><div class="wrap split">
<div>
<h2>Built by a conversion specialist, not a generalist agency.</h2>
<p>{CONFIG["brand"]} is led by {CONFIG["founder"]}. Before starting the agency, he spent a year delivering SEO and Google Business Profile optimization for dental practices, and years running A/B tests and conversion audits for brands in the US and Europe.</p>
<p>That combination is the point. Most dental marketing companies stop at rankings. We also fix what happens after the click, because a page one ranking that does not produce phone calls is not a result.</p>
<ul class="facts">
<li>{ico("check")}<span>Building and optimizing websites since 2014</span></li>
<li>{ico("check")}<span>Top Rated on Upwork since 2018, including healthcare clients</span></li>
<li>{ico("check")}<span>Websites built for US orthodontic practices on Webflow and WordPress</span></li>
<li>{ico("check")}<span>Hands-on A/B testing in VWO, Intelligems, Instapage and Unbounce</span></li>
</ul>
<div class="cta-row"><a class="btn btn-ghost" href="/about/">More about how we work</a></div>
</div>
<div>
<div class="report" role="img" aria-label="Sample monthly report layout showing calls, consult requests, direction requests and a map rank grid">
<div class="report-head"><b>Monthly practice report</b><span class="small">Sample layout</span></div>
<div class="kpis">
<div class="kpi"><div class="l">Calls from Google profile</div><div class="v">64</div><div class="d">+18 vs last month</div></div>
<div class="kpi"><div class="l">Website consult requests</div><div class="v">23</div><div class="d">+9 vs last month</div></div>
<div class="kpi"><div class="l">Direction requests</div><div class="v">117</div><div class="d">+31 vs last month</div></div>
</div>
<div class="grid-title">Map rank grid for "orthodontist near me"</div>
<div class="geo" aria-hidden="true">
{"".join(f'<span class="g{1 if n==1 else 2 if n<=3 else 3 if n<=7 else 4}">{n}</span>' for c, n in [(3,5),(2,3),(2,2),(1,2),(2,3),(3,4),(4,9),(2,3),(1,1),(1,1),(1,1),(1,2),(2,3),(3,6),(2,2),(1,1),(1,1),(1,1),(1,1),(2,2),(3,4),(2,3),(1,1),(1,1),(1,1),(1,2),(2,3),(3,5),(3,4),(2,3),(1,2),(1,1),(2,2),(2,3),(4,8),(4,10),(3,5),(2,3),(2,2),(2,3),(3,6),(4,12),(4,14),(3,7),(3,4),(2,3),(3,5),(4,9),(4,15)])}
</div>
<p class="small">Each dot is a point around your office. Green means you appear in the top three there. Example numbers.</p>
</div>
</div>
</div></section>

<section><div class="wrap">
<h2>Your first 90 days.</h2>
<ol class="timeline">
<li><span class="when">Week 1</span><h3>Audit and plan</h3><p>Map rank grid, profile and website audit, competitor review and a keyword map for your treatments and towns.</p></li>
<li><span class="when">Weeks 2 to 4</span><h3>Fix the foundations</h3><p>Profile categories and services, tracking setup, technical fixes, speed and the pages that matter most.</p></li>
<li><span class="when">Months 2 to 3</span><h3>Build authority</h3><p>Treatment and location pages, citations, local links and a review routine your front desk can keep up.</p></li>
<li><span class="when">Every month</span><h3>Report and improve</h3><p>A short report on calls, consult requests and map positions, plus what we are doing next and why.</p></li>
</ol>
</div></section>

<section class="tint"><div class="wrap">
<h2>Questions practices ask us.</h2>
{faq_html(HOME_FAQ)}
</div></section>
{cta_band()}
'''

HOME_JS = '''<script>
(function(){
  if(new URLSearchParams(location.search).get('preview')==='reviews' && !document.getElementById('reviews')){
    fetch('/reviews-preview/').then(function(r){return r.text();}).then(function(t){
      var sec=new DOMParser().parseFromString(t,'text/html').getElementById('reviews');
      var anchor=document.getElementById('pricing');
      if(sec&&anchor){anchor.after(document.importNode(sec,true));
        if(location.hash==='#reviews'){document.getElementById('reviews').scrollIntoView();}}
    });
  }
})();
(function(){
  var pack=document.getElementById('pack');
  if(pack){
    var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function rank(){pack.classList.add('ranked');
      var rows=pack.querySelectorAll('.pack-row');
      var order={'r-c':'1','r-a':'2','r-b':'3'};
      rows.forEach(function(r){for(var k in order){if(r.classList.contains(k)){r.querySelector('[data-pos]').textContent=order[k];}}});}
    if(reduce){rank();}else{
      if('IntersectionObserver' in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){setTimeout(rank,900);io.disconnect();}},{threshold:.5});io.observe(pack);}else{rank();}
    }
  }
  var fee=document.getElementById('fee'),st=document.getElementById('starts');
  if(fee&&st){
    var f=function(n){return '$'+Math.round(n).toLocaleString('en-US');};
    var up=function(){var m=fee.value*st.value;
      document.getElementById('feeOut').textContent=f(fee.value);
      document.getElementById('startsOut').textContent=st.value;
      document.getElementById('monthOut').textContent=f(m);
      document.getElementById('yearOut').textContent=f(m*12);};
    fee.addEventListener('input',up);st.addEventListener('input',up);up();
  }
})();
</script>'''

page("/", "Orthodontist Marketing & SEO Agency | " + CONFIG["brand"],
     "Orthodontist marketing agency for local SEO, Google Business Profile and website conversion. One practice per market. Get a free practice audit in 2 days.",
     home_body,
     schema=[faq_schema(HOME_FAQ),
             {"@type": "WebPage", "@id": S + "/#webpage", "url": S + "/", "name": "Orthodontist marketing and SEO agency",
              "isPartOf": {"@id": S + "/#website"}, "about": {"@id": ORG_ID}}],
     script=HOME_JS)

# ---------------------------------------------------------------- SERVICE PAGES
def service_page(path, crumb, title, desc, h1, lede, incl, steps, kw_rows, note, faqs, related, stype, sname, img="office", extra="", og="og-image.png", pkey=None):
    incl_html = "".join(f'<li><h3>{h}</h3><p>{p}</p></li>' for h, p in incl)
    steps_html = "".join(f'<li><span class="when">{w}</span><h3>{h}</h3><p>{p}</p></li>' for w, h, p in steps)
    kw_html = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in kw_rows)
    rel_html = "".join(f'<a href="{p}"><b>{t}</b>{d}</a>' for p, t, d in related)
    trail = [("Home", "/"), (crumb, path)]
    body = f'''
<section class="page-hero has-img"><div class="wrap">
<div>
{crumbs_html(trail)}
<h1>{h1}</h1>
<p class="lede">{lede}</p>
<div class="cta-row"><a class="btn btn-primary" href="/free-audit/">Get your free practice audit</a><a class="btn btn-ghost" href="#included">What is included</a></div>
{(f'<p class="price-line">Starting at <b>{price_txt(pkey)}</b>, {PRICES[pkey]["note"]}. Month to month after 90 days.</p>' if PRICES[pkey]["unit"] == "month" else f'<p class="price-line">Starting at <b>{price_txt(pkey)}</b>, {PRICES[pkey]["note"]}.</p>') if pkey else ""}
</div>
<div class="hero-ph">{P(img, w=900, h=675, eager=True)}</div>
</div></section>
<section id="included"><div class="wrap">
<h2>What is included</h2>
<ul class="incl">{incl_html}</ul>
<div class="side-note"><p>{note}</p></div>
</div></section>
{extra}
<section class="tint"><div class="wrap">
<h2>How it works</h2>
<ol class="timeline">{steps_html}</ol>
</div></section>
<section><div class="wrap">
<h2>The searches we go after</h2>
<p class="lede">Every practice gets its own keyword map. These are the kinds of searches that bring in people ready to book.</p>
<table class="kw-table"><thead><tr><th>Search type</th><th>Examples</th></tr></thead><tbody>{kw_html}</tbody></table>
</div></section>
<section class="tint"><div class="wrap">
<h2>Common questions</h2>
{faq_html(faqs)}
<h2 style="margin-top:64px;font-size:1.6rem">Related services</h2>
<div class="related">{rel_html}</div>
</div></section>
{cta_band()}
'''
    page(path, title, desc, body, schema=[service_schema(sname, desc, path, stype, pkey), faq_schema(faqs), crumbs_schema(trail)], og=og)

REL = {
    "seo": ("/orthodontist-seo/", "Orthodontist SEO", "Rank for braces and Invisalign searches in your towns."),
    "gbp": ("/google-business-profile-optimization/", "Google Business Profile", "Win the map pack and the side by side comparison."),
    "web": ("/orthodontic-website-design/", "Website design", "A fast site built to turn visits into consults."),
    "endo": ("/endodontist-marketing/", "Endodontist marketing", "Urgent searches and referral friendly pages."),
}

service_page(
    "/orthodontist-seo/", "Orthodontist SEO",
    "Orthodontist SEO Services | " + CONFIG["brand"],
    "Orthodontist SEO services for braces, Invisalign and early treatment searches: keyword map, treatment pages, map pack growth and call tracking. Free audit.",
    "Orthodontist SEO services that fill your consult calendar.",
    "We get your practice ranking for the treatment searches parents and adults make before they book, in the towns you serve, and we track the calls and consult requests that come from it.",
    [("Keyword and location map", "We map searches for braces, Invisalign, clear aligners, early treatment and adult orthodontics to the right pages and towns."),
     ("Treatment pages that rank", "Detailed pages for each treatment you offer, written for patients and structured for Google, with costs, timelines and FAQs."),
     ("Location pages done properly", "Useful pages for each community you draw from, with real local detail, not thin copies with the city name swapped."),
     ("Technical SEO", "Site speed, mobile usability, indexing, internal links, redirects and schema markup for your practice, doctors and services."),
     ("Local citations and links", "Consistent listings across the directories that matter, plus links from schools, sports clubs and local organizations you already support."),
     ("Reporting you can read", "Monthly calls, consult requests and map positions, with a short note on what changed and what we are doing next.")],
    [("Week 1", "Audit", "Technical crawl, rankings baseline, competitor gap review and tracking check."),
     ("Weeks 2 to 4", "Foundations", "Fix technical issues, improve key pages and set up call and form tracking."),
     ("Months 2 to 3", "Content and authority", "Publish treatment and location pages, build citations and earn local links."),
     ("Ongoing", "Grow", "Expand to new treatments and towns, refresh content and improve conversion.")],
    [("Near me", "orthodontist near me, braces near me, Invisalign near me"),
     ("City and treatment", "orthodontist in [city], Invisalign [city], braces for kids [city]"),
     ("Cost and comparison", "how much do braces cost, Invisalign vs braces, payment plans for braces"),
     ("Adult treatment", "adult braces, clear aligners for adults, orthodontist for adults"),
     ("Early treatment", "when should my child see an orthodontist, phase 1 orthodontic treatment")],
    "We work with one orthodontic practice per local market, so we never compete against our own client for the same searches.",
    [("How long does orthodontist SEO take?", "Map pack improvements often show in 4 to 8 weeks. Organic rankings for competitive treatment searches usually take 3 to 6 months, depending on competition and your current site."),
     ("Do I need a new website for SEO to work?", "Not always. If your current site is fast and easy to edit, we optimize it. If it is slow, outdated or hard to update, a rebuild usually pays for itself in better rankings and more consult requests."),
     ("Will you write the content?", "Yes. We write treatment and location pages for patients, then send them to you for a quick clinical accuracy check before publishing."),
     ("How do you report results?", "Every month you get calls from your Google profile, consult requests from your website, map rank grids for your main searches and a short summary of next steps."),
     ("How much does orthodontist SEO cost?", "Our orthodontist SEO starts at $1,500 per month per location, with Google Business Profile optimization included. Most dental SEO programs in the US cost between $1,000 and $2,500 per month. Competitive metro areas or multi-location groups need more work, and we quote those after the free audit. It runs month to month after the first 90 days.")],
    [REL["gbp"], REL["web"], REL["endo"]],
    "Local SEO for orthodontic practices", "Orthodontist SEO", img="bracesmodel", og="og-orthodontist-seo.png", pkey="seo",
    extra=f'''<section class="tint"><div class="wrap extra-grid">
<div>
<h2>Why orthodontist SEO is different</h2>
<p>General dental SEO treats every service the same. Orthodontics does not work that way.</p>
<p><b>Each treatment needs its own page.</b> Braces, Invisalign and early treatment are searched by different people with different questions, so one services page cannot rank for all of them.</p>
<p><b>Parents decide over several weeks.</b> They compare practices, read reviews and come back more than once, so your <a href="/google-business-profile-optimization/">Google Business Profile optimization</a> and your site have to answer cost, timing and first visit questions every time.</p>
<p><b>Success is consult requests, not traffic.</b> We track calls and consult forms, and we fix the pages that get visits but no bookings, often as part of <a href="/orthodontic-website-design/">orthodontic website design</a> work.</p>
</div>
<div>
<h2>What you get in the first 90 days</h2>
<ul class="facts">
<li>{ico("check")}<span><b>Keyword map</b> for your treatments and the towns you serve.</span></li>
<li>{ico("check")}<span><b>Google profile rebuild</b>: categories, services, photos and review routine.</span></li>
<li>{ico("check")}<span><b>Treatment pages</b> for braces, Invisalign and early treatment.</span></li>
<li>{ico("check")}<span><b>Call tracking</b> and consult form tracking.</span></li>
<li>{ico("check")}<span><b>Your first monthly report</b> on calls, consult requests and map positions.</span></li>
</ul>
</div>
</div></section>''')

service_page(
    "/google-business-profile-optimization/", "Google Business Profile optimization",
    "Orthodontist Google Business Profile Optimization",
    "Google Business Profile optimization for orthodontists: categories, services, photos, reviews and map rank tracking to win the local pack. Get a free audit.",
    "Google Business Profile optimization for orthodontic practices.",
    "Your Google Business Profile is often the first thing a new patient sees. We optimize it to rank in the top three of the map pack and to win the comparison against the practices next to you.",
    [("Category and service setup", "Primary and secondary categories, every treatment listed as a service with a clear description, and the right service area."),
     ("Photos and videos", "A photo plan for your team, office, technology and smiles, uploaded on a steady schedule that keeps the profile active."),
     ("Weekly posts and offers", "Posts about free consults, aligner promotions, community events and new technology to keep the profile fresh."),
     ("Review system", "A simple routine and message templates your front desk can use, plus replies to reviews written in your voice."),
     ("Accurate answers about your practice", "Complete services, attributes and descriptions, plus review replies, so the answers Google gives about your practice are accurate. Google has retired public Q&A and now uses Ask Maps."),
     ("Map rank tracking", "Grid based rank tracking across your service area so you see exactly where you appear in the top three and where you do not.")],
    [("Week 1", "Profile audit", "Benchmark against your top three competitors and run a map rank grid for your main searches."),
     ("Weeks 2 to 3", "Optimize", "Fix categories, services, descriptions, hours, links, photos and attributes."),
     ("Month 2", "Activate", "Start the posting schedule and review routine, complete attributes and clean up citations."),
     ("Ongoing", "Maintain and grow", "Monthly posts, photos, review replies and rank grid reporting.")],
    [("Map pack searches", "orthodontist near me, braces near me, Invisalign provider near me"),
     ("Branded searches", "your practice name, your doctor's name, practice name reviews"),
     ("Urgent and endodontic", "emergency endodontist, root canal specialist near me"),
     ("Comparison", "best orthodontist in [city], top rated orthodontist [city]")],
    "Many practices have duplicate or unverified listings for past locations or doctors. We find and fix these, because duplicates split your reviews and hold back rankings.",
    [("What is the difference between GMB and Google Business Profile?", "They are the same thing. Google renamed Google My Business to Google Business Profile, but many people still call it GMB."),
     ("How fast can map rankings improve?", "Practices with clear gaps, like wrong categories or missing services, often see movement within 4 to 8 weeks of fixes."),
     ("Will you post fake reviews?", "Never. Fake reviews break Google's rules and can get your profile suspended. We help you ask real patients at the right moment, which works better anyway."),
     ("Do you need ownership of our profile?", "No. We request manager access. Your practice always stays the primary owner."),
     ("How much does Google Business Profile optimization cost?", "A one-time profile rebuild is $750. Ongoing management, with weekly posts, photos, review replies and monthly rank grids, starts at $500 per month per location. It is also included in our orthodontist SEO and endodontist marketing programs.")],
    [REL["seo"], REL["web"], REL["endo"]],
    "Google Business Profile optimization", "Google Business Profile optimization for orthodontists", img="consult", og="og-google-business-profile.png", pkey="gbp",
    extra=f'''<section class="tint"><div class="wrap">
<h2>What a complete orthodontist profile has</h2>
<p class="lede">Whether you call it your Google Business Profile or still call it GMB, this is the checklist we work from.</p>
<ul class="ticks">
<li><b>Primary category</b> set to Orthodontist, with only relevant secondary categories</li>
<li><b>Every treatment as a service</b>: braces, Invisalign, clear aligners, early treatment and more</li>
<li><b>A clear description</b> of who you treat, where and what makes you different</li>
<li><b>Accurate hours</b>, including holiday and extended hours</li>
<li><b>Real photos</b> of your team, office, technology and smiles</li>
<li><b>Weekly posts</b> about consults, offers and practice news</li>
<li><b>Tagged website links</b> so calls and visits from the profile show up in your reports</li>
</ul>
</div></section>''')

service_page(
    "/orthodontic-website-design/", "Orthodontic website design",
    "Orthodontic Website Design & Redesign | " + CONFIG["brand"],
    "Orthodontic website design built for SEO and bookings: fast mobile pages, click to call, schema and redirect maps that protect rankings. Launch in 4 to 6 weeks.",
    "Orthodontic websites designed to book consultations.",
    "A modern, fast website that looks like the quality of care you provide, and is built by a conversion specialist so every page moves visitors toward a free consult.",
    [("Conversion-first structure", "Clear free consult offer, click to call on every page, transparent cost and payment plan information and a short booking form."),
     ("Fast on mobile", "Most visitors are on a phone. We build to Google's good Core Web Vitals thresholds and test on a mid range phone."),
     ("SEO built in", "Clean page structure, treatment and location pages, schema markup for your practice and doctors, and redirects that protect existing rankings."),
     ("Doctor and team pages", "Pages that build trust with credentials, real photos and the personality of your team."),
     ("Smile gallery and reviews", "Before and after galleries and review highlights placed where they help people decide."),
     ("Easy to update", "Built on Webflow, WordPress or a fast static setup, with training so your team can edit content without calling us.")],
    [("Week 1", "Discovery", "Goals, treatments, competitors, brand and a review of what your current site does well."),
     ("Weeks 2 to 3", "Design", "Homepage and key page designs for your feedback, mobile first."),
     ("Weeks 4 to 6", "Build", "Development, content, SEO setup, tracking and redirects."),
     ("Launch", "Go live and measure", "Launch, Search Console setup and a 30 day check on rankings and consult requests.")],
    [("Treatment pages", "braces, Invisalign, clear aligners, early treatment, adult orthodontics"),
     ("Practice pages", "meet the doctor, first visit, cost and insurance, payment plans"),
     ("Location pages", "orthodontist in [city], braces in [neighborhood]"),
     ("Conversion pages", "free consultation, virtual consult, smile assessment")],
    "Redesigning a site can lose rankings if old URLs are not redirected properly. Every redesign we do includes a full redirect map and a post launch rankings check.",
    [("How long does a new orthodontic website take?", "Most practice websites take 4 to 6 weeks from kickoff to launch, depending on how quickly content and feedback come back."),
     ("Will we lose our Google rankings?", "Not when it is done right. We map every old URL to its new page, keep what is working and monitor rankings closely after launch."),
     ("Can we keep our current domain and branding?", "Yes. We can work with your existing brand or refresh it as part of the project."),
     ("Is the contact form HIPAA safe?", "Our consult forms only collect contact details and the treatment of interest. If you need intake forms with health information, we connect a HIPAA compliant form provider."),
     ("How much does an orthodontic website cost?", "Our orthodontic websites start at $4,500, and most single-location practice sites land between $5,000 and $9,500 depending on the number of treatment and location pages, the smile gallery and integrations. Hosting and care plans start at $150 per month. You own the site and the domain.")],
    [REL["seo"], REL["gbp"], REL["endo"]],
    "Website design for orthodontic practices", "Orthodontic website design", img="office", og="og-orthodontic-website-design.png", pkey="web",
    extra=f'''<section class="tint"><div class="wrap">
<h2>Pages every orthodontic site needs</h2>
<p class="lede">The structure we start from, adjusted to the treatments and locations you actually offer.</p>
<ul class="ticks">
<li><b>Home</b> with a clear free consult offer and click to call</li>
<li><b>One page per treatment</b>: braces, Invisalign, clear aligners, early treatment</li>
<li><b>Cost and insurance</b>, including payment plans</li>
<li><b>Meet the team</b> with doctor credentials and real photos</li>
<li><b>Reviews</b> and before and after results</li>
<li><b>Each office</b> with its own location page</li>
<li><b>First visit guide</b> so new patients know what to expect</li>
</ul>
</div></section>''')

service_page(
    "/endodontist-marketing/", "Endodontist marketing",
    "Endodontist SEO & Marketing | " + CONFIG["brand"],
    "Endodontist marketing and SEO for urgent root canal searches and referral growth: map pack visibility, same day call paths and a referral form. Free audit.",
    "Endodontist marketing and SEO built around urgent searches and referrals.",
    "Endodontic patients search when they are in pain and want an answer today. Referring dentists want a practice that is easy to work with. We help you win both.",
    [("Urgent search visibility", "Rank for root canal, tooth pain and emergency endodontist searches in your area, especially in the map pack."),
     ("Same day call paths", "Click to call, clear hours and same day appointment messaging so patients in pain call you first."),
     ("Referral friendly website", "An easy referral form, doctor resources and clear communication standards for referring offices."),
     ("Google Business Profile", "Complete services, urgent care attributes, photos and a review routine tuned for an endodontic practice."),
     ("Treatment education pages", "Clear pages on root canals, retreatment, apicoectomy and cracked teeth that answer the questions people search."),
     ("Tracking calls and referrals", "See how many calls come from Google and how many referrals come through your site each month.")],
    [("Week 1", "Audit", "Map pack rankings, profile review, site speed and referral path review."),
     ("Weeks 2 to 4", "Fix and set up", "Profile optimization, call tracking and referral form improvements."),
     ("Months 2 to 3", "Content", "Treatment pages, urgent care pages and local citations."),
     ("Ongoing", "Report and grow", "Monthly calls, referrals and rank tracking.")],
    [("Urgent", "emergency endodontist, root canal near me, tooth pain dentist open now"),
     ("Treatment", "root canal specialist [city], root canal retreatment, apicoectomy"),
     ("Cost and comfort", "how much is a root canal, does a root canal hurt"),
     ("Referral", "endodontist referral form [city], refer a patient to an endodontist")],
    "Most endodontic revenue comes from referrals. A website that makes referring easy is marketing to dentists, and we treat it that way.",
    [("Is SEO worth it for endodontists if most patients are referred?", "Yes. Patients often search your name after a referral, and many search for root canal help directly. A strong profile and site support both routes."),
     ("Can you build a referral form for dentists?", "Yes. We build a simple online referral form and can connect it to a HIPAA compliant provider when it includes patient details."),
     ("Do you work with multi-location endodontic groups?", "Yes. Each location gets its own profile optimization, location page and tracking."),
     ("How do you measure results?", "Calls from Google, website referral submissions, appointment requests and map pack positions for your urgent searches."),
     ("How much does endodontist marketing cost?", "Endodontist marketing starts at $1,500 per month per location, including Google Business Profile management, urgent search pages and the referral section of your site. It runs month to month after the first 90 days."),
     ("Does emergency endodontist SEO work if we do not take walk ins?", "Yes. Most people searching for an emergency endodontist want to be seen quickly, not to walk in. We write your pages and Google profile around your real policy, whether that is same day or next day appointments, so callers know what to expect and the right patients call.")],
    [REL["gbp"], REL["seo"], REL["web"]],
    "Endodontist marketing and local SEO", "Endodontist marketing", img="endo", og="og-endodontist-marketing.png", pkey="endo",
    extra=f'''<section class="tint"><div class="wrap extra-grid">
<div>
<h2>Built for referring dentists</h2>
<p>Referring offices choose the endodontist who is easiest to work with. We build a referral section on your site that makes sending a patient take a minute, and we keep your <a href="/google-business-profile-optimization/">Google Business Profile</a> in line with it so dentists and patients see the same information.</p>
</div>
<ul class="facts">
<li>{ico("check")}<span><b>Online referral form</b> that a front desk can fill in quickly.</span></li>
<li>{ico("check")}<span><b>What to send</b>: radiographs, notes and urgency, listed clearly.</span></li>
<li>{ico("check")}<span><b>Your response time</b>, stated plainly so offices know when to expect a call.</span></li>
<li>{ico("check")}<span><b>How you report back</b> to the referring dentist after treatment.</span></li>
</ul>
</div></section>''')

# ---------------------------------------------------------------- ABOUT
about_trail = [("Home", "/"), ("About", "/about/")]
about_body = f'''
<section class="page-hero"><div class="wrap split">
<div>
{crumbs_html(about_trail)}
<h1>Meet {CONFIG["founder"]}, the specialist behind {CONFIG["brand"]}</h1>
<p class="lede">{CONFIG["brand"]} is a small team that helps orthodontists and endodontists get more new patients from Google. We are deliberately small and focused, so you work directly with the specialist doing the work.</p>
<div class="cta-row"><a class="btn btn-primary" href="/free-audit/">Get your free practice audit</a></div>
</div>
<div class="portrait"><!-- Swap for your own photo: <img src="/muhammad.jpg" alt="{CONFIG["founder"]}, founder of {CONFIG["brand"]}" width="800" height="1000"> -->{P("room", w=800, h=1000, eager=True)}</div>
</div></section>
<section><div class="wrap split">
<div>
<h2>About {CONFIG["founder"]}</h2>
<p>{CONFIG["founder"]} is a search and conversion specialist with more than a decade of experience building websites that turn visitors into customers. He holds a degree in computer science and has been building and optimizing websites since 2014.</p>
<p>Before founding {CONFIG["brand"]}, he spent a year delivering local SEO and Google Business Profile optimization for dental practices through a US marketing agency, and has since worked with more than 10 orthodontic and endodontic practices across the United States. He has designed and built websites for orthodontists on Webflow and WordPress, rebuilt Google profiles that were losing the map pack, and set up the call and form tracking that shows a doctor which channel actually produced a new patient.</p>
<p>Alongside dental work, he has spent years as a conversion rate optimization specialist for e-commerce, SaaS and service brands in the US and Europe: running A/B tests in VWO and Intelligems, building landing pages and funnels in Instapage, Unbounce and GoHighLevel, and auditing websites for the small changes that lift bookings. He has been Top Rated on Upwork since 2018, including work for healthcare clients.</p>
<p>He started {CONFIG["brand"]} because most dental marketing companies stop at rankings. Specialist practices deserve SEO and conversion handled by the same person, one practice per market, with honest monthly reporting on calls and consult requests rather than traffic charts.</p>
{('<p>' + ' &middot; '.join(x for x in [('<a href="' + CONFIG["linkedin"] + '" rel="me noopener">LinkedIn</a>') if CONFIG["linkedin"] else '', ('<a href="' + CONFIG["upwork"] + '" rel="me noopener">Upwork profile and reviews</a>') if CONFIG["upwork"] else ''] if x) + '</p>') if (CONFIG["linkedin"] or CONFIG["upwork"]) else ''}
</div>
<div>
<h2>How we work</h2>
<ul class="facts">
<li>{ico("check")}<span><b>One practice per market.</b> We never rank you against another client of ours.</span></li>
<li>{ico("check")}<span><b>You own everything.</b> Your profile, your site, your content and your data stay yours.</span></li>
<li>{ico("check")}<span><b>No fake reviews or shortcuts.</b> Nothing that puts your Google profile at risk.</span></li>
<li>{ico("check")}<span><b>Patient privacy first.</b> No health information in forms, analytics or ad platforms.</span></li>
<li>{ico("check")}<span><b>Month to month after 90 days.</b> Results should be the reason you stay.</span></li>
<li>{ico("check")}<span><b>US business hours.</b> A small team that answers email the same day, with offices in Austin and London.</span></li>
</ul>
</div>
</div></section>
{cta_band()}
'''
page("/about/", "About " + CONFIG["brand"] + " | Dental Marketing for Specialists",
     "Meet " + CONFIG["founder"] + ", the specialist behind " + CONFIG["brand"] + ": local SEO, Google Business Profile and conversion work for orthodontists and endodontists.",
     about_body, schema=[crumbs_schema(about_trail),
                         {"@type": "AboutPage", "url": S + "/about/", "about": {"@id": ORG_ID}}])

# ---------------------------------------------------------------- FREE AUDIT
audit_trail = [("Home", "/"), ("Free practice audit", "/free-audit/")]
audit_body = f'''
<section class="page-hero" style="border:0"><div class="wrap form-wrap">
<div>
{crumbs_html(audit_trail)}
<h1>Get a free audit of your practice on Google.</h1>
<p class="lede">We record a short video walkthrough showing where you rank, why competitors are ahead and the first fixes we would make. It is yours to keep, whether or not you work with us.</p>
<h2 style="font-size:1.4rem;margin-top:34px">What you get</h2>
<ul class="facts">
<li>{ico("pin")}<span><b>Map rank grid</b> for your top three searches across your service area.</span></li>
<li>{ico("star")}<span><b>Profile comparison</b> against the three practices ranking above you.</span></li>
<li>{ico("screen")}<span><b>Website review</b> of speed, mobile experience and how easy it is to book.</span></li>
<li>{ico("chart")}<span><b>A short action list</b> ordered by what will bring in the most new patients first.</span></li>
<li>{ico("clock")}<span><b>Delivered within 2 business days</b> by email.</span></li>
</ul>
</div>
<form class="card" action="/api/lead" method="POST">
{FORM_ERR}
<input type="hidden" name="form_type" value="audit">
<input type="text" name="company_fax" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<ol class="steps3">
<li><span>Send your practice website below.</span></li>
<li><span>Receive a recorded audit within 2 business days.</span></li>
<li><span>Get an action list, with no obligation.</span></li>
</ol>
<div class="row2">
<div class="f"><label for="name">Your name</label><input id="name" name="name" required autocomplete="name"></div>
<div class="f"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email"></div>
</div>
<div class="row2">
<div class="f"><label for="website">Practice website</label><input id="website" name="website" type="url" placeholder="https://" required></div>
<div class="f"><label for="city">City and state</label><input id="city" name="city" required placeholder="Austin, TX"></div>
</div>
<div class="row2">
<div class="f"><label for="phone">Phone <span class="opt">(optional)</span></label><input id="phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="f"><label for="role">Your role <span class="opt">(optional)</span></label><select id="role" name="role"><option value="">Select</option><option>Doctor or owner</option><option>Office or practice manager</option><option>Marketing lead</option><option>Other</option></select></div>
</div>
<div class="row2">
<div class="f"><label for="practice">Practice name <span class="opt">(optional)</span></label><input id="practice" name="practice" autocomplete="organization"></div>
<div class="f"><label for="specialty">Specialty</label><select id="specialty" name="specialty"><option>Orthodontics</option><option>Endodontics</option></select></div>
</div>
<div class="f"><label for="goal">What would you most like to improve? <span class="opt">(optional)</span></label><textarea id="goal" name="goal" rows="3" placeholder="For example: more Invisalign consults, ranking in a new town"></textarea></div>
<button class="btn btn-primary" type="submit">Send me my free audit</button>
<p class="privacy-line">We only use these details to prepare your audit. Please do not include any patient information.</p>
</form>
</div></section>
'''
page("/free-audit/", "Free Orthodontic Practice SEO Audit | " + CONFIG["brand"],
     "Free recorded audit of your orthodontic or endodontic practice: map rank grid, Google profile comparison and website review in 2 business days.",
     audit_body, schema=[crumbs_schema(audit_trail)], script=FORM_JS)

# ---------------------------------------------------------------- CONTACT
contact_trail = [("Home", "/"), ("Contact", "/contact/")]
CONTACT_FAQ = [
    ("How quickly will you reply?", "Within one business day, usually the same day during US business hours."),
    ("Do you offer calls?", "Yes. Mention a good time in your message and we will send a calendar invite for a 20 minute call."),
    ("Can I just get the free audit?", "Yes. The free practice audit is the fastest way to see where you stand, and there is no obligation to work with us."),
]
contact_body = f'''
<section class="page-hero" style="border:0"><div class="wrap form-wrap">
<div>
{crumbs_html(contact_trail)}
<h1>Contact us.</h1>
<p class="lede">Questions about SEO, your Google Business Profile or a new website for your practice? Send a message and you will hear back from the specialist who would do the work.</p>
<ul class="contact-cards">
<li>{ico("clock")}<span><b>Reply within one business day</b>We work US business hours, Eastern to Pacific.</span></li>
<li>{ico("shield")}<span><b>No patient information, please</b>Keep messages to your practice and marketing questions.</span></li>
<li>{ico("chart")}<span><b>Want numbers first?</b><a href="/free-audit/">Request the free practice audit</a> instead.</span></li>
<li>{ico("pin")}<span><b>Email us directly</b><a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a>{(' or <a href="' + CONFIG["scheduler"] + '" rel="noopener">book a 20 minute call</a>') if CONFIG["scheduler"] else ""}</span></li>
</ul>
<div class="offices-inline">{"".join(office_html(o) for o in OFFICES)}</div>
</div>
<form class="card" action="/api/lead" method="POST">
{FORM_ERR}
<input type="hidden" name="form_type" value="contact">
<input type="text" name="company_fax" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="row2">
<div class="f"><label for="c-name">Your name</label><input id="c-name" name="name" required autocomplete="name"></div>
<div class="f"><label for="c-email">Email</label><input id="c-email" name="email" type="email" required autocomplete="email"></div>
</div>
<div class="row2">
<div class="f"><label for="c-phone">Phone <span class="opt">(optional)</span></label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="f"><label for="c-practice">Practice name <span class="opt">(optional)</span></label><input id="c-practice" name="practice" autocomplete="organization"></div>
</div>
<div class="f"><label for="c-topic">What can we help with?</label><select id="c-topic" name="topic"><option>SEO for my practice</option><option>Google Business Profile</option><option>New website or redesign</option><option>Endodontic marketing</option><option>Something else</option></select></div>
<div class="f"><label for="c-msg">Message</label><textarea id="c-msg" name="message" rows="5" required placeholder="Tell us a little about your practice and goals"></textarea></div>
<button class="btn btn-primary" type="submit">Send message</button>
<p class="privacy-line">We reply within one business day. Please do not include any patient information.</p>
</form>
</div></section>
<section class="tint"><div class="wrap"><h2>Before you write</h2>{faq_html(CONTACT_FAQ)}</div></section>
'''
page("/contact/", "Contact | " + CONFIG["brand"] + " Dental Marketing",
     "Contact " + CONFIG["brand"] + " about SEO, Google Business Profile optimization or a new website for your orthodontic or endodontic practice. Reply within one business day.",
     contact_body, schema=[crumbs_schema(contact_trail), faq_schema(CONTACT_FAQ),
                           {"@type": "ContactPage", "url": S + "/contact/", "about": {"@id": ORG_ID}}], script=FORM_JS)

# ---------------------------------------------------------------- THANK YOU / PRIVACY / 404
page("/thank-you/", "Thank you | " + CONFIG["brand"], "Your request has been received.",
     f'''<section class="page-hero" style="border:0"><div class="wrap"><h1 id="tyH">Your audit request is in.</h1>
<p class="lede" id="tyP">We will send your recorded audit to your email within 2 business days. If you have a question in the meantime, email <a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a>.</p>
<div class="cta-row"><a class="btn btn-ghost" href="/">Back to the homepage</a></div></div></section>''', noindex=True,
     script="""<script>(function(){var q=new URLSearchParams(location.search).get('form');if(q&&typeof gtag==='function'){gtag('event','generate_lead',{form_id:q==='contact'?'contact':'free_audit',method:'website_form'});history.replaceState(null,'',location.pathname);}})();</script><script>if(new URLSearchParams(location.search).get('form')==='contact'){document.getElementById('tyH').textContent='Thanks, your message is in.';document.getElementById('tyP').firstChild.textContent='We will reply within one business day. If it is urgent, email ';}</script>""")

page("/privacy-policy/", "Privacy Policy | " + CONFIG["brand"], "How " + CONFIG["brand"] + " collects and uses information submitted through this website.",
     f'''<section><div class="wrap prose"><h1>Privacy policy</h1><p class="small">Last updated {TODAY}</p>
<p>This policy explains how {CONFIG["brand"]} handles information you share through this website. {CONFIG["brand"]} is a dental marketing agency based in the United States (Austin, Texas), with an office in London, United Kingdom.</p>
<h2>Information we collect</h2><p>When you request an audit or contact us, we collect the details you enter, such as your name, practice name, website, location, email address and phone number. We do not ask for, and you should not submit, any patient or health information.</p>
<h2>How we use it</h2><p>We use your details to prepare your audit, reply to you and, if you become a client, to deliver our services. We do not sell your information.</p>
<h2>Service providers</h2><p>Form submissions are stored securely on our hosting provider (Cloudflare) and delivered to our email. We use Google Analytics 4 and Cloudflare Web Analytics to understand how visitors use the site. Google Analytics may set cookies. You can block them in your browser or use Google's opt out add on.</p>
<h2>Your rights</h2><p>Email <a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a> to access, correct or delete your information. We do not sell personal information.</p>
<h2>Contact</h2>{"".join(office_html(o) for o in OFFICES)}
</div></section>''')

page("/reviews-preview/", "Reviews section preview | " + CONFIG["brand"], "Design preview of the reviews section with sample content.",
     f'''<section class="page-hero" style="border:0;padding-bottom:40px"><div class="wrap"><span class="rv-badge">Internal preview</span>
<h1>Reviews section preview</h1>
<p class="lede">This page shows how the reviews section will look on the home page. All reviews below are sample placeholders, not real clients. It is not linked from the site and is hidden from search engines.</p></div></section>
{reviews_section(SAMPLE_REVIEWS, sample=True, metric=("Top 3", "map pack position for the main search, example metric"))}''', noindex=True)

page("/404.html", "Page not found | " + CONFIG["brand"], "This page could not be found.",
     '''<section class="page-hero" style="border:0"><div class="wrap"><h1>That page is not here.</h1>
<p class="lede">The link may be old or mistyped. Try one of these instead.</p>
<div class="cta-row"><a class="btn btn-primary" href="/free-audit/">Get a free audit</a><a class="btn btn-ghost" href="/">Go to the homepage</a></div></div></section>''', noindex=True)

# ---------------------------------------------------------------- static files
INDEXABLE = ["/", "/orthodontist-seo/", "/google-business-profile-optimization/", "/orthodontic-website-design/",
             "/endodontist-marketing/", "/about/", "/contact/", "/free-audit/", "/privacy-policy/"]
PRIO = {"/": "1.0", "/free-audit/": "0.9", "/privacy-policy/": "0.2", "/about/": "0.6"}
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in INDEXABLE:
    sm.append(f"<url><loc>{S}{p}</loc><lastmod>{TODAY}</lastmod><priority>{PRIO.get(p, '0.8')}</priority></url>")
sm.append("</urlset>")
open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /thank-you/\nDisallow: /api/\n\nSitemap: {S}/sitemap.xml\n")
open(os.path.join(OUT, "favicon.svg"), "w").write(FAVICON)
open(os.path.join(OUT, "_headers"), "w").write("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/favicon.svg
  Cache-Control: public, max-age=604800
/og-*.png
  Cache-Control: public, max-age=604800
/favicon.ico
  Cache-Control: public, max-age=604800
/apple-touch-icon.png
  Cache-Control: public, max-age=604800
""")
# redirect www and old GMB-style URL to canonical paths
open(os.path.join(OUT, "_redirects"), "w").write(
    "/seo /orthodontist-seo/ 301\n/seo/ /orthodontist-seo/ 301\n/gmb /google-business-profile-optimization/ 301\n"
    "/gmb-optimization /google-business-profile-optimization/ 301\n/website-design /orthodontic-website-design/ 301\n"
    "/contact-us /contact/ 301\n/audit /free-audit/ 301\n")

# OG images and icons (Pillow)
try:
    from PIL import Image, ImageDraw, ImageFont
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def mark(size):
        """Logo mark: navy rounded square with teal and saffron chevrons, drawn at 4x then downscaled."""
        k = 4; z = size * k
        im = Image.new("RGBA", (z, z), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        u = z / 40
        d.rounded_rectangle([0, 0, z - 1, z - 1], int(10 * u), fill="#0E2240")
        w = max(1, int(3.4 * u))
        d.line([(11*u, 12*u), (20*u, 20*u), (29*u, 12*u)], fill="#2BB3A8", width=w, joint="curve")
        d.line([(11*u, 21*u), (20*u, 29*u), (29*u, 21*u)], fill="#F2A93B", width=w, joint="curve")
        return im.resize((size, size), Image.LANCZOS)

    def og(fname, lines, foot="Orthodontist SEO  |  Google Business Profile  |  Website design"):
        W, H = 1200, 630
        im = Image.new("RGB", (W, H), "#0E2240"); d = ImageDraw.Draw(im)
        im.paste(mark(80), (80, 80), mark(80))
        d.text((185, 100), CONFIG["brand"], font=ImageFont.truetype(fb, 40), fill="white")
        y = 230
        for line in lines:
            d.text((80, y), line, font=ImageFont.truetype(fb, 64), fill="white"); y += 80
        d.rectangle([80, 500, 1120, 503], fill="#F2A93B")
        d.text((80, 525), foot, font=ImageFont.truetype(fr, 30), fill="#C9D5E4")
        im.save(os.path.join(OUT, fname), optimize=True)

    og("og-image.png", ["Orthodontist marketing that", "books more consults", "straight from Google."])
    og("og-orthodontist-seo.png", ["Orthodontist SEO services", "that fill your", "consult calendar."], "Braces  |  Invisalign  |  Early treatment  |  Map pack")
    og("og-google-business-profile.png", ["Google Business Profile", "optimization for", "orthodontists."], "Categories  |  Services  |  Photos  |  Reviews  |  Rank tracking")
    og("og-orthodontic-website-design.png", ["Orthodontic websites", "designed to book", "consultations."], "Fast mobile pages  |  Click to call  |  SEO built in")
    og("og-endodontist-marketing.png", ["Endodontist marketing", "built around urgent", "searches and referrals."], "Root canal searches  |  Same day calls  |  Referral form")

    big = mark(512); big.save(os.path.join(OUT, "logo-512.png"), optimize=True)
    tc = Image.new("RGB", (180, 180), "#0E2240"); tc.paste(mark(180), (0, 0), mark(180))
    tc.save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
    mark(64).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
except Exception as e:
    print("Images skipped:", e)

print("Built", OUT)
