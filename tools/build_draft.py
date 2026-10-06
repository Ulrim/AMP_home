#!/usr/bin/env python3
"""에이엠피 홈페이지 리뉴얼 초안 생성기 (수처리 중심 v2).

사용법:  python3 tools/build_draft.py
출력:    site_draft/  (UTF-8 정적 HTML, robots.txt, sitemap.xml)

공통 헤더·푸터·메타 태그를 한 곳에서 관리하기 위한 스크립트이며, 결과물(HTML)만 배포해도 된다.
이미지(site_draft/default/img)와 CSS/JS는 이 스크립트가 만들지 않는다.
"""
import json
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent / "site_draft"
SITE = "https://www.amp0404.co.kr"
MAP_URL = "https://map.naver.com/p/search/" + urllib.parse.quote("전남 광양시 광양읍 익신산단3길 40")
V = "20261006b"  # 캐시 무효화용 버전


def todo(text):
    """AMP 확인이 필요한 자리. 배포 전 `class="todo"`로 검색해 모두 해소한다."""
    return f'<span class="todo">[{text}]</span>'


def img(name, alt, ext="jpg", cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<img src="/default/img/{name}.{ext}" alt="{alt}" loading="lazy"{c}>'


ICONS = {
    "drop": "M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z",
    "battery": "M3 8h15v8H3z M18 10.5h2v3h-2 M9 9.5l-2 3h3l-2 3",
    "recycle": "M20 12a8 8 0 0 1-13.7 5.6 M4 12a8 8 0 0 1 13.7-5.6 M17.7 3v3.4h-3.4 M6.3 21v-3.4h3.4",
    "fish": "M3 12c3-4.5 9-5.5 13-2.5l5-3v11l-5-3c-4 3-10 2-13-2.5z M8 11.5h.01",
    "flask": "M9 3h6 M10 3v6l-5.2 9.2A2 2 0 0 0 6.5 21h11a2 2 0 0 0 1.7-2.8L14 9V3",
    "search": "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z M20 20l-4-4",
    "target": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M12 12h.01",
    "pencil": "M4 20l1-4L16.5 4.5a2 2 0 0 1 3 3L8 19z M14 7l3 3",
    "wrench": "M14.7 6.3a4 4 0 0 0-5.2 5.2L3.5 17.5a2 2 0 0 0 3 3l6-6a4 4 0 0 0 5.2-5.2l-2.6 2.6-2.4-.6-.6-2.4z",
    "play": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M10 8.5v7l5.5-3.5z",
    "activity": "M3 12h4l3-8 4 16 3-8h4",
    "filter": "M3 5h18l-7 8v6l-4 2v-8z",
    "tank": "M5 6c0-1.7 3.1-3 7-3s7 1.3 7 3v12c0 1.7-3.1 3-7 3s-7-1.3-7-3z M5 6c0 1.7 3.1 3 7 3s7-1.3 7-3 M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3",
    "bolt": "M13 2L4 14h7l-1 8 9-12h-7z",
    "gear": "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z M19 12l2-1-1-3-2 .5-1.5-1.5.5-2-3-1-1 2h-2l-1-2-3 1 .5 2L6 8.5 4 8l-1 3 2 1v0l-2 1 1 3 2-.5L7.5 17l-.5 2 3 1 1-2h2l1 2 3-1-.5-2 1.5-1.5 2 .5 1-3z",
    "shield": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z M8.5 12l2.5 2.5L16 9.5",
}


def ico(name):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONS[name]}"/></svg>'


WAVE_D = "M0 70 Q150 20 300 70 T600 70 T900 70 T1200 70 T1500 70 T1800 70 T2100 70 T2400 70 V120 H0Z"


def waves(fill="#fff"):
    svg = ('<svg viewBox="0 0 2400 120" preserveAspectRatio="none" aria-hidden="true">'
           f'<path d="{WAVE_D}" fill="{fill}"%s/></svg>')
    return '<div class="amp-waves">' + (svg % ' fill-opacity=".5"') + (svg % "") + '</div>'


# 메뉴: 수처리를 공조부품보다 앞에 둔다 (수처리 중심 개편)
NAV = [
    ("company", "회사소개", "/default/company/greeting.html", [
        ("인사말", "/default/company/greeting.html"),
        ("연혁", "/default/company/history.html"),
        ("조직도", "/default/company/organization.html"),
        ("인증 및 제증명", "/default/company/certification.html"),
        ("협력기관", "/default/company/partners.html"),
        ("오시는 길", "/default/company/location.html"),
    ]),
    ("water", "수처리·물 매니지먼트", "/default/water/overview.html", [
        ("수처리 시스템 설비", "/default/water/overview.html"),
        ("이차전지 폐수처리", "/default/water/battery.html"),
        ("공정수 재순환", "/default/water/recycle.html"),
        ("육상양식 물관리", "/default/water/aquaculture.html"),
        ("제약·화학 폐수처리", "/default/water/pharma.html"),
    ]),
    ("portfolio", "시공사례·납품실적", "/default/portfolio/water.html", [
        ("수처리·공정장비 실적", "/default/portfolio/water.html"),
        ("공조부품 실적", "/default/portfolio/air.html"),
    ]),
    ("air", "공조부품", "/default/air/products.html", [
        ("제품 소개", "/default/air/products.html"),
        ("생산·품질", "/default/air/quality.html"),
    ]),
    ("cscenter", "고객센터", "/default/cscenter/contact.html", [
        ("견적·기술상담", "/default/cscenter/contact.html"),
        ("공지사항", "/default/cscenter/notice.html"),
        ("FAQ", "/default/cscenter/faq.html"),
    ]),
]

PAGES = []


def header(section):
    items = []
    for key, label, href, subs in NAV:
        cls = " ".join(c for c in ["water" if key == "water" else "", "on" if key == section else ""] if c)
        sub = "".join(f'<li><a href="{h}">{t}</a></li>' for t, h in subs)
        items.append(f'<li class="{cls}"><a href="{href}">{label}</a><ul class="sub">{sub}</ul></li>')
    return (
        '<a class="amp-skip" href="#main">본문 바로가기</a>'
        '<header class="amp-header"><div class="amp-wrap">'
        '<a class="amp-logo" href="/default/index.html"><img src="/default/img/logo-t.png" alt="AMP 에이엠피"></a>'
        '<button class="amp-burger" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>'
        f'<nav class="amp-nav" aria-label="주요 메뉴"><ul>{"".join(items)}</ul></nav>'
        '</div></header>'
    )


def footer():
    return (
        '<footer class="amp-footer"><div class="amp-wrap">'
        '<address><img class="fl" src="/default/img/logo-t.png" alt="AMP 에이엠피"><br>'
        '<b>유한회사 에이엠피</b> · 대표이사 안명원<br>사업자등록번호 171-81-03763<br>'
        '본점 전남 광양시 광양읍 익신산단3길 40, 409호<br>'
        f'TEL {todo("대표번호")} · E-mail {todo("대표 이메일")}</address>'
        '<ul><li><a href="/default/company/greeting.html">회사소개</a></li>'
        '<li><a href="/default/water/overview.html">수처리·물 매니지먼트</a></li>'
        '<li><a href="/default/portfolio/water.html">시공사례</a></li>'
        '<li><a href="/default/air/products.html">공조부품</a></li>'
        '<li><a href="/default/cscenter/contact.html">CS CENTER</a></li></ul>'
        '<div class="amp-copy">© AMP Co., Ltd. All rights reserved.</div>'
        '</div></footer>'
    )


def subhead(h1, crumbs, lead="", kind="water", bg=None):
    crumb = " &gt; ".join(f'<a href="{c[1]}">{c[0]}</a>' if isinstance(c, tuple) else c for c in crumbs)
    p = f"<p>{lead}</p>" if lead else ""
    bgd = (f'<div class="bg" style="background-image:url(/default/img/{bg}.jpg)"></div>') if bg else ""
    w = waves() if kind != "air" else ""
    return (f'<div class="amp-subhead {"air" if kind == "air" else ""}">{bgd}<div class="amp-wrap">'
            f'<div class="amp-crumb"><a href="/default/index.html">HOME</a> &gt; {crumb}</div><h1>{h1}</h1>{p}</div>{w}</div>')


def localnav(section, current):
    for key, label, href, subs in NAV:
        if key == section:
            lis = "".join(f'<li><a href="{h}"{" class=on" if h == current else ""}>{t}</a></li>'.replace("class=on", 'class="on"') for t, h in subs)
            return f'<div class="amp-localnav"><ul>{lis}</ul></div>'
    return ""


def write(path, title, desc, body, section="", extra_head=""):
    url = SITE + path
    PAGES.append(path)
    html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="에이엠피 AMP">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/default/img/og-default.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/default/img/logo.png">
<link rel="stylesheet" href="/default/css/amp-draft.css?v={V}">
{extra_head}</head>
<body class="amp">
{header(section)}
<main id="main">
{body}
</main>
{footer()}
<script src="/default/js/amp-draft.js?v={V}" defer></script>
</body>
</html>
'''
    out = ROOT / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def banner(h="설비·수처리 견적 문의", p="현장 상황을 알려 주시면 담당자가 확인 후 연락드립니다."):
    return (f'<section class="amp-banner"><div class="amp-wrap"><div><h2>{h}</h2><p>{p} &nbsp; 대표번호 {todo("대표번호")}</p></div>'
            '<a class="amp-btn" href="/default/cscenter/contact.html">견적·기술상담 신청</a></div></section>')


def cta(field, label, water=True):
    return (f'<div class="amp-cta{"" if water else " air"} rv"><div><h3>이 분야 견적·기술상담 받기</h3>'
            f'<p>{label} 관련 현장 조건을 알려 주시면 확인 후 연락드립니다.</p></div>'
            f'<a class="amp-btn" href="/default/cscenter/contact.html?field={field}">견적·기술상담 신청</a></div>')


FIELDS = [  # key, 아이콘, 제목, 설명, 이미지, 링크
    ("battery", "battery", "이차전지 폐수처리", "망초폐수·고염폐수 처리, 전구체 공침 공정 장비", "pilot-01", "/default/water/battery.html"),
    ("recycle", "recycle", "공정수 재순환", "재이용 시스템, 입자선별·필터 장치", "module-a1", "/default/water/recycle.html"),
    ("aqua", "fish", "육상양식 물관리", "RAS·BFT 수질 모니터링, 미생물 배양수조", "aqua-02", "/default/water/aquaculture.html"),
    ("pharma", "flask", "제약·화학 폐수처리", "원수 분석 기반 맞춤형 수처리 시스템", None, "/default/water/pharma.html"),
]
PROC = [("search", "현장·수질 진단"), ("target", "처리목표 설정"), ("pencil", "공정설계"), ("flask", "Pilot/시제품 제작"),
        ("wrench", "설비 제작·설치"), ("play", "시운전"), ("activity", "모니터링·유지관리")]
SENSORS = ["pH", "EC", "온도", "탁도", "TDS", "DO"]


def field_cards():
    out = []
    for i, (k, ic, t, d, im, href) in enumerate(FIELDS):
        photo = img(im, t) if im else ""
        out.append(f'<a class="amp-field{"" if im else " nophoto"} rv d{i + 1}" href="{href}">{photo}<span class="ic">{ico(ic)}</span>'
                   f'<div class="t"><h3>{t}</h3><p>{d}</p><span class="go">자세히 보기</span></div></a>')
    return "".join(out)


def steps7(dark=True):
    lis = "".join(f'<li class="rv d{min(i % 4 + 1, 4)}"><div class="c">{ico(ic)}</div><small>STEP 0{i + 1}</small><b>{t}</b></li>'
                  for i, (ic, t) in enumerate(PROC))
    return f'<ol class="amp-steps7">{lis}</ol>'


def flowline(items):
    """items: [(icon, 제목, 부제)]"""
    lis = "".join(f'<li><div class="fi">{ico(ic)}</div>{t}<small>{s}</small></li>' for ic, t, s in items)
    return f'<ol class="amp-flowline rv">{lis}</ol>'


# ───────────────────────── 메인 ─────────────────────────
def build_index():
    org = json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": "유한회사 에이엠피", "alternateName": "AMP", "url": SITE,
        "logo": SITE + "/default/img/logo.png",
        "address": {"@type": "PostalAddress", "addressRegion": "전남", "addressLocality": "광양시",
                    "streetAddress": "광양읍 익신산단3길 40, 409호", "addressCountry": "KR"},
    }, ensure_ascii=False)
    chips = "".join(f"<span>{s}</span>" for s in SENSORS)
    body = f'''
<section class="amp-hero2">
  <div class="bg" style="background-image:url(/default/img/aqua-05.jpg)"></div>
  <div class="amp-bubbles"></div>
  <div class="amp-wrap">
    <div>
      <!-- 슬로건 문구는 AMP 최종 승인 필요 -->
      <span class="eyebrow"><i></i>WATER MANAGEMENT SOLUTION</span>
      <h1>현장에 맞춘 설비,<br><em>데이터로 관리하는 물</em></h1>
      <p class="sub">수처리 설비의 설계·제작·설치·시운전부터 수질 모니터링까지. 이차전지 공정 설비와 공조부품 제조 기술이 뒷받침합니다.</p>
      <div class="btns"><a class="amp-btn" href="/default/cscenter/contact.html">수처리 견적 문의</a>
      <a class="amp-btn ghost" href="/default/water/overview.html">수처리 설비 보기</a></div>
    </div>
    <div class="amp-panel"><div class="bar"><i></i>실시간 수질 모니터링 프로그램</div>
      {img("monitor-screen", "실시간 모니터링 프로그램(AMP) 화면")}
      <div class="amp-chips">{chips}</div></div>
  </div>
  {waves()}
</section>

<section class="amp-stats"><div class="amp-wrap"><div>
  <div class="amp-stat"><b><span data-count="7">7</span><small>단계</small></b><span>수행 프로세스</span><em>진단부터 유지관리까지</em></div>
  <div class="amp-stat"><b><span data-count="4">4</span><small>개 분야</small></b><span>수처리 적용 분야</span><em>이차전지·재순환·양식·제약화학</em></div>
  <div class="amp-stat"><b><span data-count="6">6</span><small>종</small></b><span>수질 측정 항목</span><em>pH·EC·온도·탁도·TDS·DO</em></div>
  <div class="amp-stat"><b><span data-count="3">3</span><small>개 인증</small></b><span>공신력 있는 확인</span><em>벤처·뿌리기업·ISO 9001</em></div>
</div></div></section>

<section class="amp-sec"><div class="amp-wrap">
  <div class="amp-head-row"><div><span class="amp-eyebrow">APPLICATION</span>
  <h2 class="rv">물이 다르면, 설비도 달라야 합니다</h2>
  <p class="lead rv">현장마다 다른 물의 성상에 맞춰 네 가지 분야에서 수처리 설비를 설계·제작합니다.</p></div></div>
  <div class="amp-grid c4">{field_cards()}</div>
</div></section>

<section class="amp-sec dark"><div class="amp-wrap">
  <span class="amp-eyebrow">PROCESS</span>
  <h2 class="rv">진단에서 유지관리까지, 한 흐름으로</h2>
  <p class="lead rv">자체 공장에서 구조물과 장치를 직접 제작하기 때문에 설계 변경에도 빠르게 대응합니다.</p>
  {steps7()}
  <p style="margin-top:44px"><a class="amp-btn ghost" href="/default/water/overview.html">수행 프로세스 자세히 보기</a></p>
</div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <span class="amp-eyebrow">SOLUTION · 이차전지 폐수</span>
  <h2 class="rv">고염 폐수를 처리하고, 물은 다시 씁니다</h2>
  <p class="lead rv">전구체·양극재 공정에서 나오는 망초폐수(Na₂SO₄)를 전처리, 농축, 전기투석역전(EDR)으로 처리해 공정수로 재이용하는 흐름입니다.</p>
  {flowline([("filter", "전처리", "Micro Filter"), ("tank", "농축탱크", "농축"), ("bolt", "EDR", "전기투석역전"), ("drop", "처리수 재이용", "중앙 모니터링")])}
  <p><a class="amp-btn line" href="/default/water/battery.html">이차전지 폐수처리 보기</a></p>
</div></section>

<section class="amp-sec"><div class="amp-wrap"><div class="amp-split">
  <div><span class="amp-eyebrow">MONITORING</span>
  <h2 class="rv">경험이 아니라, 데이터로 관리합니다</h2>
  <p class="lead rv" style="margin-bottom:22px">수질 센서로 측정한 값을 실시간 프로그램에서 확인하고, 이상이 생기면 알림으로 대응합니다. 육상양식 물관리와 공정수 모니터링에 적용됩니다.</p>
  <div class="amp-chips dark">{chips}</div>
  <ul class="amp-checks" style="margin-top:22px"><li>실시간 모니터링 프로그램과 원격 대시보드·알림</li><li>pH·투입량 이상 감지 및 제어 프로그램</li></ul></div>
  <figure class="amp-figure rv">{img("monitoring-field", "수질 센서와 모니터링 프로그램을 점검하는 현장")}<figcaption>수질 센서와 실시간 모니터링 프로그램 현장</figcaption></figure>
</div></div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <div class="amp-head-row"><div><span class="amp-eyebrow">REFERENCES</span><h2 class="rv">제작·설치한 설비</h2>
  <p class="lead rv" style="margin-bottom:0">실제 제작한 수처리 설비와 수행한 과제의 일부입니다.</p></div>
  <a class="amp-btn line" href="/default/portfolio/water.html">시공사례 전체 보기</a></div>
  <div class="amp-grid c3" style="margin-top:36px">
    <a class="amp-card rv d1" href="/default/portfolio/water.html"><div class="imgwrap">{img("reactor-lab-01", "전구체 공침반응기")}</div><div class="body"><span class="tag">이차전지</span><h3>전구체 공침반응기</h3><p>실험실 규모(Lab 5L~50L급) 맞춤 제작, pH·투입량 제어.</p></div></a>
    <a class="amp-card rv d2" href="/default/portfolio/water.html"><div class="imgwrap">{img("pilot-02", "이차전지 폐수처리 Pilot 시스템")}</div><div class="body"><span class="tag">이차전지</span><h3>폐수처리 Pilot 시스템</h3><p>고염 폐수 처리 공정을 현장 조건에 맞춰 시험하는 Pilot 설비.</p></div></a>
    <a class="amp-card rv d3" href="/default/portfolio/water.html"><div class="imgwrap">{img("aqua-01", "육상양식 수조 현장")}</div><div class="body"><span class="tag">육상양식</span><h3>양식장 수질관리</h3><p>수질 센서와 모니터링 프로그램으로 물 상태를 확인·관리.</p></div></a>
  </div>
</div></section>

<section class="amp-sec"><div class="amp-wrap"><div class="amp-heritage">
  <div><span class="amp-eyebrow air">MANUFACTURING</span>
  <h2 class="rv">수처리 설비를 만드는 제조 기반</h2>
  <p class="lead rv" style="margin-bottom:24px">에이엠피는 Clad Aluminum Header Pipe 등 공조부품을 제조해 온 기업입니다. 이때 쌓은 용접·절단·가공 역량과 공정별 작업표준서 기반 품질관리가 수처리 설비 제작의 바탕입니다.</p>
  <a class="amp-btn line" href="/default/air/products.html">공조부품 보기</a></div>
  <div class="thumbs rv">{img("product-header-pipe", "Clad AL Header Pipe")}{img("product-pipe-assembly", "Clad AL Pipe 및 Assembly")}{img("product-heat-exchanger", "열교환기")}</div>
</div></div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <span class="amp-eyebrow">TRUST</span><h2 class="rv">신뢰 지표</h2>
  <ul class="amp-trust"><li>ISO 9001</li><li>벤처기업 확인</li><li>뿌리기업 확인</li><li>연구전담부서</li><li>전라남도지사 표창</li></ul>
  <div class="amp-certrow">{img("cert-venture", "벤처기업확인서")}{img("cert-root", "뿌리기업확인서")}{img("award-jeonnam", "전라남도지사 표창장")}{img("award-smba", "중소벤처기업청장 상장")}</div>
</div></section>
{banner()}
'''
    write("/default/index.html",
          "에이엠피 AMP – 수처리 시스템 설비·Clad AL Header Pipe 제조",
          "에이엠피는 이차전지 폐수처리·공정수 재순환·육상양식·제약화학 수처리 설비를 설계·제작·설치하고 Clad AL Header Pipe 등 공조부품을 제조합니다.",
          body, extra_head=f'<script type="application/ld+json">{org}</script>\n')


# ───────────────────────── 회사소개 ─────────────────────────
def company_page(path, title, desc, h1, body_inner, lead=""):
    body = (subhead(h1, ["회사소개", h1], lead, bg="aqua-05") + localnav("company", path) +
            f'<section class="amp-sec"><div class="amp-wrap">{body_inner}</div></section>')
    write(path, title, desc, body, "company")


def build_company():
    values = "".join(f'<div class="amp-tile rv"><b>{a}</b><span>{b}</span></div>' for a, b in [
        ("도전 정신 Challenge", "새로운 분야에 도전합니다."),
        ("윤리 경영 Ethics", "투명하고 책임 있게 경영합니다."),
        ("창조성 Creativity", "창조적 혁신으로 가치를 만듭니다."),
        ("전문성 Professionalism", "현장 경험과 기술로 전문성을 쌓습니다.")])
    company_page("/default/company/greeting.html", "인사말 | 에이엠피",
        "공조부품 제조로 쌓은 가공·품질관리 역량을 바탕으로 수처리·물 매니지먼트로 사업을 넓힌 에이엠피의 인사말.",
        "인사말", f'''
<!-- 인사말은 컬리버 초안. AMP 최종 승인 필요 -->
<div class="amp-prose" style="max-width:820px">
  <h2>홈페이지를 방문해 주신 여러분께 감사드립니다.</h2>
  <p>에이엠피는 <b>수처리·물 매니지먼트</b> 분야에서 현장·수질 진단부터 공정 설계, 설비 제작·설치, 시운전, 모니터링까지 한 흐름으로 수행합니다.
  이차전지 공정 폐수, 공정수 재순환, 육상양식, 제약·화학 폐수까지 현장마다 물의 성상이 다르다는 점에서 출발합니다.</p>
  <p>이 사업의 바탕에는 공조부품 제조가 있습니다. 대형·소형·원형·사각 알루미늄 파이프를 가공해 공조기 제품 제작에 쓰이는
  Clad Aluminum Header Pipe를 고객 요구에 맞춰 주문 생산하며 쌓은 가공·품질관리 역량이 수처리 설비 제작의 기반입니다.</p>
  <p>현장에 맞춘 설계·제작과 사후관리로 신뢰받는 파트너가 되겠습니다.
  필요하신 설비와 제품은 전화 또는 <a href="/default/cscenter/contact.html" style="text-decoration:underline">견적·기술상담</a>으로 문의해 주십시오.</p>
  <p style="margin-top:28px"><b>대표이사 안명원</b></p>
</div>
<h3 style="margin-top:56px">윤리·책임경영</h3>
<p class="amp-prose">창조적 혁신을 통해 사회적 가치를 실현하는 책임 있는 경영을 추구합니다.</p>
<div class="amp-grid c4">{values}</div>''')

    tl = [
        ("2026", "스마트제조 전환지원 사업, AI솔루션 구축지원 사업 등 수행 " + todo("공개 가능 범위 AMP 확인")),
        ("2026.03", "벤처기업 확인 (혁신성장유형, 유효기간 2029.03.16까지)"),
        ("2025.12", "지점 등록 (여수 융합지구)"),
        ("2025.11", "전라남도지사 표창 (벤처기업인으로서 지역경제 활성화 공로)"),
        ("2025.10", "뿌리기업 확인 (한국생산기술연구원, 유효기간 2028.10.20까지)"),
        ("2025.01", "유한회사 에이엠피 사업 개시"),
        ("2024.11", "광주·전남지방중소벤처기업청장 상장 (모범적인 기업경영)"),
        ("이전", "기존 연혁 이관 " + todo("현 홈페이지 company 연혁 원문 붙여넣기")),
    ]
    company_page("/default/company/history.html", "연혁 | 에이엠피",
        "에이엠피의 주요 연혁 – 뿌리기업·벤처기업 확인, 전라남도지사 표창, 여수 지점 등록 등.", "연혁",
        '<ol class="amp-timeline" style="max-width:760px">' + "".join(f"<li><time>{a}</time>{b}</li>" for a, b in tl) + "</ol>")

    company_page("/default/company/organization.html", "조직도 | 에이엠피",
        "에이엠피 조직도 – 대표이사, 생산팀, 품질·설계, 연구전담부서.", "조직도",
        f'<p class="amp-prose">{todo("실제 조직 구성 AMP 확인 후 수정")}</p>'
        '<div class="amp-org"><div class="top">대표이사</div><div class="bar"></div>'
        '<div class="row"><div>생산팀</div><div>품질·설계</div><div>연구전담부서</div></div></div>')

    def cert(n, cap, sub):
        return f'<figure class="amp-cert amp-figure">{img(n, cap)}<figcaption>{cap}<small>{sub}</small></figcaption></figure>'
    company_page("/default/company/certification.html", "인증 및 제증명 | 에이엠피",
        "에이엠피의 벤처기업확인서, 뿌리기업확인서, ISO 9001, 전라남도지사 표창, 중소벤처기업청장 상장.", "인증 및 제증명",
        f'''<div class="amp-grid c4">{cert("cert-venture", "벤처기업확인서", "혁신성장유형 · 2026.03.17 ~ 2029.03.16")}{cert("cert-root", "뿌리기업확인서", "2025.10.21 ~ 2028.10.20")}{cert("award-jeonnam", "전라남도지사 표창장", "2025.11.19")}{cert("award-smba", "중소벤처기업청장 상장", "2024.11.14")}</div>
<div class="amp-box" style="margin-top:28px"><h3>ISO 9001:2015</h3><p>품질경영시스템 인증을 보유하고 있습니다. {todo("ISO 9001 인증서 이미지 수령 후 추가")}</p></div>''')

    partners = [("전남테크노파크", "지역 기업 지원기관"), ("전남대학교", "산학 협력(MOU)"),
                ("순천대학교", "산학 협력(MOU)"), ("광양시", "이차전지 산업 협약")]
    company_page("/default/company/partners.html", "협력기관 | 에이엠피",
        "에이엠피의 협력기관 – 전남테크노파크, 전남대학교, 순천대학교, 광양시 등.", "협력기관",
        '<div class="amp-grid c4">' + "".join(f'<div class="amp-tile"><b>{a}</b><span>{b}</span></div>' for a, b in partners) +
        f'</div><p class="amp-prose" style="margin-top:24px">{todo("기존 협력기관 4곳(현 홈페이지 파트너) 추가")}</p>')

    company_page("/default/company/location.html", "오시는 길 | 에이엠피",
        "에이엠피 본점(광양 익신산단), 공장(광양 태인동 국가산단), 지점·연구(여수 주삼동) 위치 안내.", "오시는 길",
        f'''<table class="amp-table">
<tr><th>본점</th><td>전남 광양시 광양읍 익신산단3길 40, 409호 (광양만권 소재부품 지식산업센터)<br>
<a href="{MAP_URL}" target="_blank" rel="noopener" style="text-decoration:underline">지도 보기</a></td></tr>
<tr><th>공장</th><td>전남 광양시 태인동 국가산업단지 {todo("공장 상세 주소")}</td></tr>
<tr><th>지점·연구</th><td>전남 여수시 주삼동 (여수 융합지구) {todo("여수 지점 호수 106호 vs 202-01 확인")}</td></tr>
<tr><th>전화</th><td>{todo("대표번호")}</td></tr></table>''')


# ───────────────────────── 공조부품 ─────────────────────────
def build_air():
    def air_page(path, h1, title, desc, inner):
        body = (subhead(h1, ["공조부품", h1], "Clad Aluminum Header Pipe", kind="air") + localnav("air", path) +
                f'<section class="amp-sec"><div class="amp-wrap">{inner}</div></section>')
        write(path, title, desc, body, "air")

    gal = "".join(f'<figure>{img(n, a)}</figure>' for n, a in [
        ("product-header-pipe", "Clad Aluminum Header Pipe"), ("product-pipe-assembly", "Clad Aluminum Pipe 및 Assembly"),
        ("product-heat-exchanger", "알루미늄 열교환기"), ("product-atf-warmer", "ATF Warmer"),
        ("product-ev-cooler", "전기차 배터리 Cooler"), ("product-tube-stack", "알루미늄 튜브 적층 가공품")])
    air_page("/default/air/products.html", "제품 소개", "Clad Aluminum Header Pipe 제조 | 에이엠피",
        "Clad AL Header Pipe, Clad AL Pipe & Assembly, ATF Warmer, 전기차 배터리 Cooler, D-type 실내기(증발기) 등 공조부품을 제조합니다.",
        f'''
<div class="amp-split top">
  <div class="amp-prose">
    <h2>Clad Aluminum Header Pipe란?</h2>
    <p>공조시스템에 적용되는 브레이징 제품에 사용되는 부품입니다. 주로 자동차 열교환기(콘덴서, 에바, 히터, 라디에이터 등)와
    가정용 에어컨 열교환기(콘덴서, 에바)에 적용됩니다.</p>
    <p>용융점이 다른 알루미늄 합금(3000계, 4000계 등)을 클래딩한 판재를 <b>고주파 유도용접</b>으로 조관해 제작합니다.</p>
    <table class="amp-table"><tr><th>심재(Core)</th><td>알루미늄 합금(3000계 등), 용융점 630~660℃</td></tr>
    <tr><th>클래드층</th><td>Al-Si 합금(4000계 등), 용융점 577~610℃</td></tr>
    <tr><th>제작 방식</th><td>클래드 판재 → 고주파 유도용접 조관</td></tr></table>
  </div>
  <figure class="amp-figure">{img("air-diagram-clad", "알루미늄 클래딩 라인과 클래드 판재 단면 도식")}<figcaption>용융점이 서로 다른 알루미늄 클래드 판재</figcaption></figure>
</div>
<h2 style="margin-top:56px">주력 제품</h2>
<ul class="amp-prose"><li>Clad Aluminum Header Pipe</li><li>Clad AL Pipe &amp; Assembly</li><li>ATF Warmer</li>
<li>전기차 배터리 Cooler</li><li>D-type 실내기(증발기)</li></ul>
<div class="amp-gallery" style="margin-top:20px">{gal}</div>
<p class="amp-prose" style="margin-top:14px">{todo("제품 사진 원본 수령 후 교체 (현재 현 홈페이지 캡처 크롭)")}</p>
{cta("air", "공조부품(Clad AL Header Pipe)", water=False)}''')

    qs = "".join(f'<figure class="amp-figure">{img(n, a)}<figcaption>{a}</figcaption></figure>' for n, a in [
        ("qs-cutting", "작업표준서 – 절단 공정"), ("qs-deburring", "작업표준서 – 디버링 공정"), ("qs-washing", "작업표준서 – 세척 공정")])
    flow = "".join(f"<li>{s}</li>" for s in ["원소재 조관", "사이징/인발", "절단", "디버링", "표면처리(세척)", "검사", "포장·출고"])
    air_page("/default/air/quality.html", "생산·품질", "공조부품 생산공정·품질관리 | 에이엠피",
        "Clad AL Header Pipe 생산공정(조관·사이징·절단·디버링·세척·검사)과 공정별 작업표준서, ISO 9001:2015 품질관리를 소개합니다.",
        f'''
<h2>생산공정</h2>
<ol class="amp-steps">{flow}</ol>
<h2 style="margin-top:48px">품질관리</h2>
<div class="amp-prose" style="max-width:820px">
<p>절단·디버링·세척 등 공정별로 <b>작업표준서</b>를 운영합니다. 작업 순서와 방법, 작업 조건 관리 항목, 자주 검사 항목,
품질 문제·비상 상황 발생 시 조치 사항을 공정마다 명시하고, 개정 이력을 관리합니다.</p>
<ul><li>절단: 수입검사, 초물 검사, 길이·진직도·수직도 자주검사</li>
<li>디버링: 브러쉬 간격 설정, 버(Burr)·모서리 및 절단면 상태 확인</li>
<li>세척: 세척액 온도·상태 관리, 건조 및 내경 검사</li>
<li>품질경영시스템 ISO 9001:2015</li></ul></div>
<div class="amp-gallery" style="margin-top:28px">{qs}</div>
<p class="amp-prose" style="margin-top:12px">{todo("작업표준서에 고객사명·품번·담당자 실명이 보임 – 게시 범위 AMP 최종 확인(필요 시 해당 부분 가림 처리)")}</p>
{cta("air", "공조부품", water=False)}''')


# ───────────────────────── 수처리 ─────────────────────────
def water_page(path, h1, title, desc, lead, bg, inner):
    body = subhead(h1, ["수처리·물 매니지먼트", h1], lead, bg=bg) + localnav("water", path) + inner
    write(path, title, desc, body, "water")


def block(no, title, content):
    return (f'<div class="amp-block rv"><div class="amp-bhead"><span class="no">{no}</span><h2>{title}</h2></div>{content}</div>')


def field_page(path, field, label, h1, title, desc, lead, bg, problem, solution, results):
    inner = (f'<section class="amp-sec" style="padding-top:56px"><div class="amp-wrap">'
             f'{block("01", "고객 문제", f"""<div class="amp-problem">{problem}</div>""")}'
             f'{block("02", "해결 방식", solution)}{block("03", "실적·성과", results)}'
             f'{cta(field, label)}</div></section>')
    water_page(path, h1, title, desc, lead, bg, inner)


def checks(items):
    return '<ul class="amp-checks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def gallery(items, cls=""):
    return f'<div class="amp-gallery {cls}">' + "".join(
        f'<figure class="rv">{img(n, a)}<figcaption>{a}</figcaption></figure>' for n, a in items) + "</div>"


def build_water():
    chips = "".join(f"<span>{s}</span>" for s in SENSORS)
    strengths = "".join(f'''<div class="amp-card rv d{i + 1}"><div class="body"><div style="font-size:34px;color:var(--blue);margin-bottom:10px">{ico(ic)}</div><h3>{t}</h3><p>{d}</p></div></div>'''
                        for i, (ic, t, d) in enumerate([
        ("flask", "화학공학·품질관리 기반 공정조건 설정", "원수 특성과 처리 목표에 맞춰 공정 조건을 정합니다."),
        ("gear", "자체 공장에서 구조물·장치 직접 제작", "용접·절단·가공 설비를 갖춰 설계 변경에 빠르게 대응합니다."),
        ("activity", "수질 센서 기반 실시간 모니터링", "pH, EC, 온도, 탁도, TDS, DO를 측정하고 데이터를 관리합니다.")]))
    inner = f'''
<section class="amp-sec"><div class="amp-wrap">
  <span class="amp-eyebrow">PROCESS</span>
  <h2 class="rv">수행 프로세스 7단계</h2>
  <p class="lead rv">원수 성상이 현장마다 달라 표준 설비만으로는 처리 목표를 맞추기 어렵습니다. 진단에서 유지관리까지 한 흐름으로 수행합니다.</p>
  {steps7(dark=False)}
</div></section>
<section class="amp-sec soft"><div class="amp-wrap">
  <span class="amp-eyebrow">STRENGTH</span><h2 class="rv">에이엠피의 강점</h2>
  <div class="amp-grid c3" style="margin-top:32px">{strengths}</div>
</div></section>
<section class="amp-sec dark"><div class="amp-wrap"><div class="amp-split">
  <div><span class="amp-eyebrow">MONITORING</span><h2 class="rv">수질 데이터를 실시간으로 봅니다</h2>
  <p class="lead rv" style="margin-bottom:24px">센서로 측정한 값을 모니터링 프로그램에서 확인하고 데이터로 관리합니다.</p>
  <div class="amp-chips">{chips}</div></div>
  <div class="amp-grid c2"><figure class="amp-figure rv">{img("monitoring-field", "수질 센서와 모니터링 프로그램 현장")}</figure>
  <figure class="amp-figure rv d2">{img("monitor-screen", "실시간 모니터링 프로그램(AMP) 화면")}</figure></div>
</div></div></section>
<section class="amp-sec"><div class="amp-wrap">
  <span class="amp-eyebrow">APPLICATION</span><h2 class="rv">적용 분야</h2>
  <p class="lead rv">분야별 고객 문제, 해결 방식, 실적을 확인하세요.</p>
  <div class="amp-grid c4">{field_cards()}</div>
  {cta("etc", "수처리 시스템 설비")}
</div></section>'''
    water_page("/default/water/overview.html", "수처리 시스템 설비",
        "수처리 시스템 설비 설계·제작·설치 | 에이엠피",
        "광양 소재 에이엠피는 현장·수질 진단, 공정설계, 설비 제작·설치, 시운전, 모니터링까지 수처리 시스템 설비를 한 흐름으로 수행합니다.",
        "현장마다 다른 물, 현장에 맞춘 수처리 설비를 설계·제작·설치합니다", "monitoring-field", inner)

    field_page("/default/water/battery.html", "battery", "이차전지 폐수처리", "이차전지 폐수처리",
        "이차전지 폐수처리·망초폐수 재이용 | 에이엠피",
        "이차전지 전구체·양극재 공정의 망초폐수·고염폐수 처리, 전구체 공침반응기(Lab 5L~50L급) 제작, 무방류(ZLD) 지향 공정 설계.",
        "고염·고농도 폐수 처리와 공정수 재이용, 전구체 공침 공정 장비", "pilot-01",
        "<p>전구체·양극재 공정에서는 고염·고농도 폐수(망초폐수, Na₂SO₄)가 발생합니다.</p><p>폐수 처리비가 늘어나고, 공정수를 확보하는 부담도 함께 커집니다.</p>",
        flowline([("filter", "전처리", "Micro Filter"), ("tank", "농축탱크", "농축"), ("bolt", "EDR", "전기투석역전"), ("drop", "처리수 재이용", "공정수로 재사용")]) +
        checks(["중앙 모니터링으로 공정 상태를 확인합니다.",
                "무방류(ZLD)를 지향하는 공정으로 설계합니다. 실제 공정 구성은 현장 수질에 따라 달라집니다.",
                "연계 장비: 전구체 공침반응기(Lab 5L ~ 50L급), pH·투입량 이상 감지 및 제어 프로그램"]) +
        f'''<div class="amp-split top" style="margin-top:30px">
  <figure class="amp-figure rv">{img("reactor-diagram-50l", "50L 공침 반응기 구성 개념도")}<figcaption>50L 공침 반응기 구성 개념도</figcaption></figure>
  <figure class="amp-figure rv d2">{img("zld-diagram", "무방류 ZLD 공정 개념도")}<figcaption>무방류(ZLD) 공정 개념도 – 현장 수질에 따라 공정 구성이 달라집니다</figcaption></figure></div>''',
        '<p class="amp-prose">이차전지 폐수처리 Pilot, 실험실 맞춤형 공침반응기, 전구체 입자선별·필터 장치를 제작했습니다.</p>' +
        gallery([("pilot-01", "폐수처리 Pilot 시스템"), ("pilot-02", "폐수처리 Pilot 시스템(측면)"),
                 ("reactor-lab-01", "전구체 공침반응기"), ("reactor-lab-02", "공침반응기 제어부"),
                 ("module-b1", "전구체 입자선별 및 필터 장치"), ("module-b2", "입자선별 필터 장치(S社 양극재)")]) +
        '<h3>공침반응기 제작 과정</h3>' +
        gallery([("reactor-01", "판재 절단·가공"), ("reactor-02", "스테인리스 용접"), ("reactor-03", "조립·치수 확인"),
                 ("reactor-04", "교반부(임펠러)"), ("reactor-05", "상부 포트·클램프 조립"), ("reactor-site-01", "설치·점검")]) +
        f'<p class="amp-prose" style="margin-top:12px">{todo("고객사명은 익명(S社) 표기 유지 – 공개 범위 AMP 확인")}</p>')

    field_page("/default/water/recycle.html", "recycle", "공정수 재순환", "공정수 재순환",
        "공정수 재순환 시스템 | 에이엠피",
        "공정수 사용량과 폐수 배출을 줄이는 현장 맞춤형 공정수 재순환·재이용 시스템과 입자선별·필터 장치, 수질 모니터링 연동.",
        "공정수 사용량·폐수 배출량을 줄이는 현장 맞춤형 재이용 시스템", "module-a1",
        "<p>공정수 사용량과 폐수 배출량이 늘면서 원가와 ESG 부담이 커지고 있습니다.</p>",
        flowline([("search", "현장·수질 진단", "원수 확인"), ("tank", "재순환 모듈", "현장 맞춤 설계"), ("filter", "입자선별·필터", "고형물 분리"), ("activity", "모니터링 연동", "수질 확인")]) +
        checks(["현장 맞춤형 재순환 모듈", "입자선별·필터 장치", "수질 모니터링 연동"]),
        '<p class="amp-prose">공정수 재순환 현장 맞춤형 시스템을 제작했습니다. ' + todo("모듈 사진 매핑 확인(콜라주 하단 좌측 2컷 가정)") + '</p>' +
        gallery([("module-a1", "공정수 재순환 현장 맞춤형 시스템"), ("module-a2", "재순환 모듈 설치 구성")], "c2"))

    field_page("/default/water/aquaculture.html", "aqua", "육상양식 물관리", "육상양식 물관리",
        "육상양식 수처리·수질 모니터링 | 에이엠피",
        "RAS·바이오플락(BFT) 육상양식장의 수질 센서·컨트롤러, 순환여과 수처리, 미생물 자동 배양수조, 원격 모니터링을 제공합니다.",
        "RAS·BFT 양식장의 수질을 데이터로 관리합니다", "aqua-05",
        "<p>RAS·바이오플락(BFT) 양식장은 수질 관리가 경험에 의존하는 경우가 많습니다.</p><p>수온·pH·DO가 급변하면 대량 폐사로 이어질 위험이 있습니다.</p>",
        flowline([("filter", "순환여과 수처리", "수질 정화"), ("activity", "수질 센서·컨트롤러", "pH·DO·온도 등"), ("flask", "미생물 자동 배양수조", "DO·pH·염도·온도 보정"), ("bolt", "원격 대시보드·알림", "이상 시 알림")]) +
        f'<p class="amp-prose">연계 과제: 미생물 자동 배양수조 개발 (블루스타트업) {todo("과제 완료 후 사진 추가, 대외 표기 가능 여부 확인")}</p>',
        checks(["양식어가 수질 센서 및 물관리 시스템 검증 (2025)", "무안 소재 양식장 유지보수"]) +
        gallery([("aqua-01", "육상양식 수조 현장"), ("aqua-02", "원형 수조"), ("aqua-05", "양식장 수조 전경"),
                 ("aqua-06", "수조 수질 상태"), ("aqua-07", "수조 점검"), ("aqua-04", "수조 표면 상태")]) +
        f'<p class="amp-prose" style="margin-top:12px">{todo("고객은 C社(양식어가) 익명 – 양식장 위치 노출 가능 여부 확인")}</p>')

    field_page("/default/water/pharma.html", "pharma", "제약·화학 폐수처리", "제약·화학 폐수처리",
        "제약·화학 폐수처리 시스템 | 에이엠피",
        "원수 성상이 현장마다 다른 제약·화학 폐수를 원수 분석 기반으로 공정을 구성하고 소규모·Pilot 규모로 맞춤 제작합니다.",
        "원수 분석에서 출발하는 맞춤형 수처리 시스템", "monitoring-field",
        "<p>제약·화학 공정은 원수 성상이 현장마다 달라, 표준 설비만으로는 처리 목표를 달성하기 어렵습니다.</p>",
        flowline([("flask", "원수 분석", "성상 파악"), ("target", "공정 구성", "처리목표 기반"), ("tank", "맞춤 제작", "소규모·Pilot"), ("play", "설치·시운전", "처리 확인")]) +
        checks(["원수 분석 결과를 기준으로 공정을 구성합니다.", "소규모·Pilot 규모부터 맞춤 제작합니다."]),
        '<p class="amp-prose">제약공정 수처리 시스템을 제작·설치했습니다.</p>' +
        f'<p class="amp-prose">{todo("제약공정 수처리 시스템 사진 수령 후 추가 (현재 이 분야 사진 없음)")}</p>')


# ───────────────────────── 시공사례 ─────────────────────────
def build_portfolio():
    def card(n, alt, cat, tag, title, text, meta, tagcls=""):
        im = f'<div class="imgwrap">{img(n, alt)}</div>' if n else f'<div class="noimg">{ico("drop")}</div>'
        return (f'<div class="amp-card rv" data-cat="{cat}">{im}<div class="body"><span class="tag {tagcls}">{tag}</span>'
                f'<h3>{title}</h3><p>{text}</p><div class="meta">{meta}</div></div></div>')

    water = [
        card("reactor-lab-01", "실험실 맞춤형 공침반응기", "battery", "이차전지", "실험실 맞춤형 공침반응기(5L)", "전구체 공침 공정용 실험실 규모 반응기를 맞춤 제작.", "고객: 대학·연구소 / 양극재사"),
        card("pilot-01", "이차전지 폐수처리 Pilot", "battery", "이차전지", "이차전지 폐수처리 Pilot", "고염 폐수 처리 공정을 시험하는 Pilot 설비 제작.", ""),
        card("module-a1", "공정수 재순환 시스템", "recycle", "공정수", "공정수 재순환 현장 맞춤형 시스템", "현장 조건에 맞춘 재순환 모듈 제작.", ""),
        card("module-b1", "전구체 입자선별 및 필터 장치", "battery", "이차전지", "전구체 입자선별 및 필터 장치", "전구체 입자 선별용 필터 장치 제작.", "고객: S社(양극재)"),
        card(None, "", "pharma", "제약·화학", "제약공정 수처리 시스템", "제약공정 수처리 시스템 제작·설치. " + todo("사진 확인 필요"), ""),
        card("monitor-screen", "수질 실시간 모니터링 프로그램 화면", "common", "공통", "수질 실시간 모니터링 프로그램·센서", "pH, EC, 온도, 탁도, TDS, DO 측정 및 데이터 관리.", ""),
        card("aqua-01", "육상양식 수조", "aqua", "육상양식", "양식어가 수질센서·물관리 시스템 검증", "양식 수조 수질 센서와 물관리 시스템을 검증.", "고객: C社(양식어가) · 2025"),
        card(None, "", "battery", "이차전지", "원료 가공·소모품 납품", "이차전지 양극재 공정용 원료 가공 및 소모품 납품.", "고객: S社(양극재) · 2025"),
    ]
    flt = '<div class="amp-filter">' + "".join(
        f'<button data-filter="{k}"{" class=on" if k == "all" else ""}>{v}</button>'.replace("class=on", 'class="on"') for k, v in
        [("all", "전체"), ("battery", "이차전지"), ("recycle", "공정수"), ("aqua", "육상양식"), ("pharma", "제약·화학"), ("common", "공통")]) + "</div>"
    body = (subhead("수처리·공정장비 실적", ["시공사례·납품실적", "수처리·공정장비 실적"], "분야별로 제작·설치한 설비와 납품 실적입니다.", bg="pilot-02") +
            localnav("portfolio", "/default/portfolio/water.html") +
            f'<section class="amp-sec"><div class="amp-wrap">{flt}<div class="amp-grid c3">{"".join(water)}</div></div></section>' + banner())
    write("/default/portfolio/water.html", "시공사례·납품실적 | 에이엠피",
          "에이엠피의 수처리·공정장비 시공사례와 납품실적 – 공침반응기, 폐수처리 Pilot, 공정수 재순환, 수질 모니터링, 육상양식.", body, "portfolio")

    air = [card("product-header-pipe", "Clad AL Header Pipe", "air", "공조부품", "Clad AL Header Pipe 가공", "알루미늄 클래드 파이프 가공품.", "", "air"),
           card("product-pipe-assembly", "Clad AL Pipe 및 Assembly", "air", "공조부품", "Clad AL Pipe 및 Assembly", "파이프 및 조립품.", "", "air"),
           card("product-heat-exchanger", "열교환기", "air", "공조부품", "열교환기용 부품", "자동차·가정용 에어컨 열교환기 적용.", "", "air")]
    body = (subhead("공조부품 실적", ["시공사례·납품실적", "공조부품 실적"], "Clad AL Header Pipe 등 공조부품 가공·납품 실적입니다.", kind="air") +
            localnav("portfolio", "/default/portfolio/air.html") +
            f'<section class="amp-sec"><div class="amp-wrap"><div class="amp-grid c3">{"".join(air)}</div>'
            f'<p class="amp-prose" style="margin-top:14px">{todo("기존 갤러리 3건 이관 – 현 사이트 gallery01.php 원본 이미지·설명으로 교체")}</p>'
            f'{cta("air", "공조부품", water=False)}</div></section>')
    write("/default/portfolio/air.html", "공조부품 납품실적 | 에이엠피",
          "에이엠피의 Clad AL Header Pipe 등 공조부품 가공·납품실적.", body, "portfolio")


# ───────────────────────── 고객센터 ─────────────────────────
FAQ = [
    ("견적은 어떻게 진행되나요?", "문의 접수 후 현장·수질을 확인하고 개략 견적을 드립니다. 이후 상세 설계를 거쳐 상세 견적을 안내합니다."),
    ("현장 방문 상담이 가능한가요?", "가능합니다. 수처리 설비는 현장·수질 진단이 첫 단계이므로, 상담 시 방문 일정을 협의합니다."),
    ("소량·Pilot 규모도 제작하나요?", "네. Pilot/시제품 제작 단계를 수행 프로세스에 두고 있으며, 실험실 규모(5L급)부터 맞춤 제작한 실적이 있습니다."),
    ("제작 기간은 얼마나 걸리나요?", "설비 규모와 사양에 따라 달라집니다. 요구 사양을 알려 주시면 상담 시 예상 일정을 안내합니다."),
    ("설치 후 유지보수·소모품 공급이 되나요?", "설치·시운전 이후 모니터링과 유지관리까지 수행합니다. 소모품은 설비별로 상담해 안내합니다."),
    ("원격 모니터링을 지원하나요?", "수질 센서(pH, EC, 온도, 탁도, TDS, DO) 기반의 실시간 모니터링 프로그램과 원격 대시보드·알림을 지원합니다."),
    ("Clad AL Header Pipe 주문 사양은 어떻게 전달하나요?", "견적·기술상담에서 문의 분야를 '공조부품'으로 선택하고 사양(규격, 수량, 도면 등)을 남겨 주시면 확인 후 연락드립니다."),
    ("정부지원사업과 연계한 도입 상담이 가능한가요?", "스마트제조 전환지원 등 지원사업을 수행한 경험이 있어 상담이 가능합니다. 지원사업명과 일정을 함께 알려 주세요."),
]


def build_cscenter():
    def cs(path, h1, title, desc, inner, extra_head=""):
        body = (subhead(h1, ["고객센터", h1], bg="aqua-05") + localnav("cscenter", path) +
                f'<section class="amp-sec"><div class="amp-wrap">{inner}</div></section>')
        write(path, title, desc, body, "cscenter", extra_head)

    opts = [("etc", "기타"), ("battery", "이차전지 폐수"), ("recycle", "공정수 재순환"), ("aqua", "육상양식"), ("pharma", "제약·화학"), ("air", "공조부품")]
    options = "".join(f'<option value="{k}">{v}</option>' for k, v in opts)
    cs("/default/cscenter/contact.html", "견적·기술상담", "견적·기술상담 | 에이엠피",
       "에이엠피에 수처리 설비 견적과 기술상담, 공조부품 주문을 문의하세요. 분야를 선택해 현장 조건을 남기면 확인 후 연락드립니다.",
       f'''
<div class="amp-split top">
<div>
<p id="sentMsg" class="amp-box hl" style="display:none"><b>문의가 접수되었습니다.</b> 확인 후 연락드리겠습니다.</p>
<form class="amp-form" method="post" action="/default/cscenter/contact_ok.php">
  <div class="amp-hp" aria-hidden="true"><label>비워 두세요 <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
  <div><label for="field">문의 분야 <span class="req">*</span></label><select id="field" name="field" required>{options}</select></div>
  <div class="two">
    <div><label for="name">성명 <span class="req">*</span></label><input type="text" id="name" name="name" required autocomplete="name"></div>
    <div><label for="company">회사명</label><input type="text" id="company" name="company" autocomplete="organization"></div>
  </div>
  <div class="two">
    <div><label for="tel">연락처 <span class="req">*</span></label><input type="tel" id="tel" name="tel" required autocomplete="tel"></div>
    <div><label for="email">이메일 <span class="req">*</span></label><input type="email" id="email" name="email" required autocomplete="email"></div>
  </div>
  <div><label for="water">처리 유량·원수 종류 (선택)</label><input type="text" id="water" name="water" placeholder="예) 일 10톤, 고염 폐수">
    <div class="hint">수처리 설비 문의 시 알고 계신 범위에서 적어 주세요.</div></div>
  <div><label for="msg">문의 내용 <span class="req">*</span></label><textarea id="msg" name="msg" rows="7" required></textarea></div>
  <div class="amp-privacy"><h4>개인정보 수집·이용 동의</h4>
    <table><tr><th>수집 항목</th><td>성명, 회사명, 연락처, 이메일, 문의 내용(처리 유량·원수 종류 포함)</td></tr>
    <tr><th>이용 목적</th><td>견적·기술상담 문의에 대한 확인 및 회신</td></tr>
    <tr><th>보유 기간</th><td>문의 처리 완료 후 1년 보관 후 파기 {todo("보유기간 AMP 확인")}</td></tr></table>
    <p style="margin:8px 0 0">동의를 거부할 수 있으며, 거부 시 상담 접수가 제한됩니다.</p></div>
  <label class="amp-check"><input type="checkbox" id="agree" name="agree" value="1" required> 개인정보 수집·이용에 동의합니다. <span class="req">(필수)</span></label>
  <div><button class="amp-btn" type="submit">문의 접수</button></div>
</form></div>
<aside class="amp-box"><h3>직접 문의</h3>
<table class="amp-table"><tr><th>전화</th><td>{todo("대표번호")}</td></tr><tr><th>이메일</th><td>{todo("대표 이메일")}</td></tr>
<tr><th>본점</th><td>전남 광양시 광양읍 익신산단3길 40, 409호</td></tr></table>
<p style="font-size:14px;color:var(--ink-soft);margin-top:14px">견적 진행: 문의 → 현장·수질 확인 → 개략 견적 → 상세 설계 견적</p></aside>
</div>''')

    cs("/default/cscenter/notice.html", "공지사항", "공지사항 | 에이엠피", "에이엠피 공지사항.",
       f'<div class="amp-empty"><p>등록된 공지사항이 없습니다.</p><p>{todo("기존 게시판(DB 연동) 페이지와 연결하거나, 공지가 생기면 이 화면에 목록 추가")}</p></div>')

    faq_html = "".join(f'<details><summary>{q}</summary><div class="a"><p>{a}</p></div></details>' for q, a in FAQ)
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False)
    cs("/default/cscenter/faq.html", "FAQ", "자주 묻는 질문 | 에이엠피",
       "에이엠피 견적 절차, 현장 방문, Pilot 제작, 유지보수, 원격 모니터링, Clad AL Header Pipe 주문 방법 등 자주 묻는 질문.",
       f'<div class="amp-faq" style="max-width:860px">{faq_html}</div><p style="margin-top:28px"><a class="amp-btn" href="/default/cscenter/contact.html">견적·기술상담 신청</a></p>',
       f'<script type="application/ld+json">{ld}</script>\n')


def build_seo_files():
    urls = sorted(set(PAGES))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{SITE}{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /default/cscenter/contact_ok.php\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def main():
    build_index()
    build_company()
    build_air()
    build_water()
    build_portfolio()
    build_cscenter()
    build_seo_files()
    print("pages:", len(PAGES))


if __name__ == "__main__":
    main()
