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
PHONE = "0507-1486-0997"  # 공장등록증명(신청)서 기재 번호 – 대표번호로 공개 가능한지 AMP 확인 필요
MAP_URL = "https://map.naver.com/p/search/" + urllib.parse.quote("전남 광양시 광양읍 익신산단3길 40")
MAP_URL_FACTORY = "https://map.naver.com/p/search/" + urllib.parse.quote("전남 광양시 태인5길 51-17")
V = "20261006b"  # 캐시 무효화용 버전


TODO_USED = {}  # 표식 문구 -> set(페이지)


def todo(text):
    """AMP 확인이 필요한 자리. 배포 전 `class="todo"`로 검색해 모두 해소한다."""
    TODO_USED.setdefault(text, set())
    return f'<span class="todo">[{text}]</span>'


IMG_DIR = ROOT / "default" / "img"
DEFAULT_SPEC = "가로형(4:3 권장) · 가로 1600px 이상 · JPG"
# 사진이 아직 없는 자리. 같은 파일명으로 default/img/<key>.jpg 를 넣고 다시 빌드하면 자동으로 채워진다.
# key: (필요한 사진, 규격/비고, 비율, 선택 여부)
PHOTO_SPEC = {
    "pilot-01": ("이차전지 폐수처리 Pilot 설비 전경(정면)", "설비 전체가 보이게", "4/3", False),
    "pilot-02": ("이차전지 폐수처리 Pilot 설비(다른 각도)", "", "4/3", False),
    "reactor-lab-01": ("전구체 공침반응기 전경", "반응기 본체와 교반부가 보이게", "4/3", False),
    "reactor-lab-02": ("공침반응기 제어부(펌프·pH 제어)", "", "4/3", False),
    "module-a1": ("공정수 재순환 현장 맞춤형 시스템 전경", "", "4/3", False),
    "module-a2": ("공정수 재순환 모듈 설치 구성(다른 각도)", "", "4/3", False),
    "module-b1": ("전구체 입자선별 및 필터 장치", "", "4/3", False),
    "module-b2": ("입자선별 필터 장치(다른 각도)", "", "4/3", False),
    "monitor-screen": ("실시간 모니터링 프로그램(AMP) 화면 캡처", "스크린샷 · 16:9 · 시험 데이터만 보이게", "16/9", False),
    "pharma-01": ("제약공정 수처리 시스템 제작·설치 사진", "", "4/3", False),
    "pharma-02": ("제약공정 수처리 시스템(다른 각도)", "", "4/3", True),
    "supply-01": ("원료 가공·소모품 납품 사진", "", "4/3", True),
    "product-header-pipe": ("Clad AL Header Pipe 제품", "정사각 또는 4:3 · 단색 배경", "4/3", False),
    "product-pipe-assembly": ("Clad AL Pipe 및 Assembly", "", "4/3", False),
    "product-heat-exchanger": ("열교환기(콘덴서·에바) 적용품", "", "4/3", False),
    "product-atf-warmer": ("ATF Warmer", "", "4/3", False),
    "product-ev-cooler": ("전기차 배터리 Cooler", "", "4/3", False),
    "product-tube-stack": ("D-type 실내기(증발기) 또는 튜브 적층 가공품", "", "4/3", False),
    "air-case-01": ("공조부품 납품 사례 1 (기존 갤러리 원본)", "현 홈페이지 gallery01 사진", "4/3", False),
    "air-case-02": ("공조부품 납품 사례 2 (기존 갤러리 원본)", "", "4/3", False),
    "air-case-03": ("공조부품 납품 사례 3 (기존 갤러리 원본)", "", "4/3", False),
}
PH_USED = {}  # key -> set(페이지)


def placeholder(name, alt):
    title, spec, ratio, optional = PHOTO_SPEC.get(name, (alt, "", "4/3", False))
    PH_USED.setdefault(name, set())
    opt = "(선택) " if optional else ""
    return (f'<div class="amp-ph" data-ph="{name}" style="aspect-ratio:{ratio}" role="img" aria-label="사진 필요: {title}">'
            f'<div>{ico("camera")}<b>{opt}사진 필요</b><span>{title}</span><small>{name}.jpg · {spec or DEFAULT_SPEC}</small></div></div>')


def img(name, alt, ext="jpg", cls=""):
    if ext == "jpg" and not (IMG_DIR / f"{name}.jpg").exists():
        return placeholder(name, alt)
    c = f' class="{cls}"' if cls else ""
    return f'<img src="/default/img/{name}.{ext}" alt="{alt}" loading="lazy"{c}>'


ICONS = {
    "camera": "M4 8h3l2-3h6l2 3h3v11H4z M12 11a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z",
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
        ("언론보도·활동", "/default/company/news.html"),
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
        f'TEL {PHONE} · E-mail {todo("대표 이메일")}</address>'
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
    bgd = (f'<div class="bg" style="background-image:url(/default/img/{bg}.jpg)"></div>') if bg and (IMG_DIR / f"{bg}.jpg").exists() else ""
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
    for k in PH_USED:
        if f'data-ph="{k}"' in html:
            PH_USED[k].add(path)
    for t in TODO_USED:
        if f'>[{t}]</span>' in html:
            TODO_USED[t].add(path)
    out = ROOT / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def banner(h="설비·수처리 견적 문의", p="현장 상황을 알려 주시면 담당자가 확인 후 연락드립니다."):
    return (f'<section class="amp-banner"><div class="amp-wrap"><div><h2>{h}</h2><p>{p} &nbsp; 대표번호 {PHONE}</p></div>'
            '<a class="amp-btn" href="/default/cscenter/contact.html">견적·기술상담 신청</a></div></section>')


def cta(field, label, water=True):
    return (f'<div class="amp-cta{"" if water else " air"} rv"><div><h3>이 분야 견적·기술상담 받기</h3>'
            f'<p>{label} 관련 현장 조건을 알려 주시면 확인 후 연락드립니다.</p></div>'
            f'<a class="amp-btn" href="/default/cscenter/contact.html?field={field}">견적·기술상담 신청</a></div>')


FIELDS = [  # key, 아이콘, 제목, 설명, 이미지, 링크
    ("battery", "battery", "이차전지 폐수처리", "망초폐수·고염폐수 처리, 전구체 공침 공정 장비", "pilot-01", "/default/water/battery.html"),
    ("recycle", "recycle", "공정수 재순환", "재이용 시스템, 입자선별·필터 장치", "module-a1", "/default/water/recycle.html"),
    ("aqua", "fish", "육상양식 물관리", "RAS·BFT 수질 모니터링, 미생물 배양수조", "aqua-02", "/default/water/aquaculture.html"),
    ("pharma", "flask", "제약·화학 폐수처리", "원수 분석 기반 맞춤형 수처리 시스템", "pharma-01", "/default/water/pharma.html"),
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
  <div class="amp-stat"><b><span data-count="7">7</span><small>개 인증·지정</small></b><span>공신력 있는 확인</span><em>ISO 9001·벤처·뿌리기업·연구개발전담부서 등</em></div>
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
  <div class="thumbs rv">{img("air-case-01", "차량용 Clad AL Header Pipe 출고")}{img("air-case-02", "Clad AL Header Pipe 포장")}{img("air-drawbench", "3구 인발기")}</div>
</div></div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <div class="amp-head-row"><div><span class="amp-eyebrow">NEWS</span><h2 class="rv">최근 활동</h2></div>
  <a class="amp-btn line" href="/default/company/news.html">언론보도·활동 전체 보기</a></div>
  <div class="amp-grid c3" style="margin-top:32px">
    <a class="amp-card rv d1" href="/default/company/news.html"><div class="imgwrap">{img("ev-xiamen-12", "중국 샤먼시 국제무역투자상담회 업무협약")}</div><div class="body"><span class="tag">2026.09</span><h3>중국 샤먼 국제무역투자상담회</h3><p>이차전지 폐수처리 분야 협력기업과 업무협약 체결.</p></div></a>
    <a class="amp-card rv d2" href="/default/company/news.html"><div class="imgwrap">{img("ev-bk-03", "배터리 코리아 2026 전시")}</div><div class="body"><span class="tag">2026</span><h3>배터리 코리아 2026</h3><p>광양 스마트그린산단 공동관 참가.</p></div></a>
    <a class="amp-card rv d3" href="/default/company/news.html"><div class="imgwrap">{img("ev-export-02", "전남·광주 해외수출페스티벌 상담")}</div><div class="body"><span class="tag">2026</span><h3>전남·광주 해외수출페스티벌</h3><p>해외 바이어 수출 상담.</p></div></a>
  </div>
</div></section>

<section class="amp-sec"><div class="amp-wrap">
  <span class="amp-eyebrow">NETWORK</span><h2 class="rv">함께하는 기관과 기업</h2>
  <p class="lead rv">광양시 이차전지 산업 협약, 대학 산학협력, 이차전지 폐수처리 분야 해외 협력으로 현장 적용 범위를 넓히고 있습니다.</p>
  <div class="amp-grid c4">
    <a class="amp-tile rv d1" href="/default/company/partners.html"><b>광양시 이차전지 산업 협약</b><span>광양시·전남테크노파크·포스코퓨처엠·SNNC 등 14개 기관과 함께 참여 (2025.09)</span></a>
    <a class="amp-tile rv d2" href="/default/company/partners.html"><b>대학 산학협력</b><span>국립순천대학교·전남대학교·한영대학교와 협약</span></a>
    <a class="amp-tile rv d3" href="/default/company/partners.html"><b>해외 협력</b><span>이차전지 폐수처리 분야 중국 협력기업과 업무협약 (2026.09)</span></a>
    <a class="amp-tile rv d4" href="/default/company/certification.html"><b>순천대 G-SCNU 강소지역기업</b><span>국립순천대학교 지정 · 가족회사 인증</span></a>
  </div>
</div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <span class="amp-eyebrow">TRUST</span><h2 class="rv">신뢰 지표</h2>
  <ul class="amp-trust"><li>ISO 9001</li><li>벤처기업 확인</li><li>뿌리기업 확인</li><li>연구개발전담부서 인정</li><li>전라남도 청년기업</li><li>G-SCNU 강소지역기업</li><li>전라남도지사 표창</li></ul>
  <div class="amp-certrow">{img("cert-iso", "ISO 9001 품질경영시스템 인증서")}{img("cert-venture", "벤처기업확인서")}{img("cert-root", "뿌리기업확인서")}{img("cert-rnd", "연구개발전담부서 인정서")}</div>
  <p style="margin-top:18px"><a href="/default/company/certification.html" style="text-decoration:underline">인증 및 제증명 전체 보기</a> <span style="color:var(--ink-soft);font-size:14px">· ISO 9001 인증범위: 알루미늄 합금 파이프 가공 제조</span></p>
</div></section>
{banner()}
'''
    write("/default/index.html",
          "에이엠피 AMP – 수처리 시스템 설비·Clad AL Header Pipe 제조",
          "에이엠피는 이차전지 폐수처리·공정수 재순환·육상양식·제약화학 수처리 설비를 설계·제작·설치하고 Clad AL Header Pipe 등 공조부품을 제조합니다.",
          body, extra_head=f'<script type="application/ld+json">{org}</script>\n')


# ───────────────────────── 회사소개 ─────────────────────────
def company_page(path, title, desc, h1, body_inner, lead=""):
    body = (subhead(h1, ["회사소개", h1], lead, bg="factory-exterior") + localnav("company", path) +
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
<h2 style="margin-top:64px">회사 개요</h2>
<div class="amp-overview">
<table class="amp-table">
<tr><th>회사명</th><td>유한회사 에이엠피 (AMP)</td></tr>
<tr><th>대표</th><td>안명원 · 화학공학 석사, 제조업 부설연구소 및 품질 업무 10년 이상</td></tr>
<tr><th>설립일</th><td>2025년 1월 1일 (법인 전환, 2023년 4월 창업)</td></tr>
<tr><th>사업자</th><td>법인사업자 (171-81-03763)</td></tr>
<tr><th>본사</th><td>전라남도 광양시 광양읍 익신산단3길 40, 409호</td></tr>
<tr><th>지점·공장</th><td>전라남도 광양시 태인5길 51-17, 가동 1층</td></tr>
<tr><th>업종·업태</th><td>제조업 / 비철금속, 알루미늄, 파이프<br>제조업 / 산업용 특수목적 기계, 액체여과장치 제조업<br>제조업 / 이차전지 관련 자재부품 및 도소매</td></tr>
</table>
<div class="pics">{img("factory-exterior", "광양 태인동 지점·공장 외관")}{img("factory-interior", "공장 내부 생산 공간")}</div>
</div>
<h3 style="margin-top:56px">윤리·책임경영</h3>
<p class="amp-prose">창조적 혁신을 통해 사회적 가치를 실현하는 책임 있는 경영을 추구합니다.</p>
<div class="amp-grid c4">{values}</div>''')

    tl = [  # 회사 소개자료(2026.11) 연혁 + 인증·협약서 날짜
        ("2026.09", "2026 중국 샤먼시 국제무역투자상담회 참가, 이차전지 폐수처리 분야 중국 협력기업과 업무협약 (09.08~09.10)"),
        ("2026.09", "ISO 9001:2015 품질경영시스템 인증 갱신 (유효기간 2029.09.07까지)"),
        ("2026.05", "한영대학교 제철케미칼전공 산학협력위원회 위원 위촉 (2026.05.01~2028.05.31)"),
        ("2026.04", "국립순천대학교 가족회사 인증 (04.30), 한영대학교와 산학협력 협약 (04.24)"),
        ("2026.03", "벤처기업 확인 (제20260317030006호, 혁신성장유형)"),
        ("2026.02", "국립순천대학교 AI중심대학사업단과 상호협력 협약 (02.09)"),
        ("2026", "스마트제조 전환지원 사업, AI솔루션 구축지원 사업 등 수행 " + todo("공개 가능 범위 AMP 확인")),
        ("2025.12", "지점 등록 (융합지구 – 여수 주삼동)"),
        ("2025.11", "전라남도지사 표창 수여"),
        ("2025.10", "연구개발전담부서 설립 (제2025155989호), 뿌리기업 확인 (제25122-28120호)"),
        ("2025.09", "광양시 이차전지 산업 상호협력과 공동발전을 위한 업무협약 참여 (09.24)"),
        ("2025.08", "지점 및 공장 등록 (국가산단 – 광양 태인동), 전라남도 청년기업 인증, 국립순천대학교 글로컬대학·RISE사업 업무협약, 전남대학교 그린바이오 혁신융합대학사업단 산학협력 협약"),
        ("2025.07", "전남형 청년창업사관학교 1기 입교, 국립순천대학교 G-SCNU 강소지역기업 지정"),
        ("2025.05", "본점 이전: 지식산업센터(광양 익신산단) 및 전남테크노파크 입주"),
        ("2025.01", "법인 전환: 유한회사 에이엠피 및 공장 이전"),
        ("2024.11", "광주·전남지방중소벤처기업청장 표창 수여"),
        ("2024.04", "2024년 청년창업사관학교(전남 14기) 수행 완료"),
        ("2023.09", "ISO 9001:2015 품질경영시스템 인증"),
        ("2023.04", "에이엠피(AMP) 설립, 2023년 예비창업패키지(전남) 수행 완료"),
        ("2023.03", "1인 창조기업 입주 – 전남여수산학융합원, 제조 공장 설립(전남 광양)"),
    ]
    company_page("/default/company/history.html", "연혁 | 에이엠피",
        "에이엠피의 주요 연혁 – ISO 9001 인증, 뿌리기업·벤처기업 확인, 연구개발전담부서 인정, 대학·광양시 협약, 전라남도지사 표창 등.", "연혁",
        '<ol class="amp-timeline" style="max-width:760px">' + "".join(f"<li><time>{a}</time>{b}</li>" for a, b in tl) + "</ol>")

    company_page("/default/company/organization.html", "조직도 | 에이엠피",
        "에이엠피 조직도 – 대표이사, 생산팀, 품질·설계, 연구개발부서.", "조직도",
        f'<p class="amp-prose">{todo("생산팀·품질·설계 조직 구성 AMP 확인 후 수정")}</p>'
        '<div class="amp-org"><div class="top">대표이사</div><div class="bar"></div>'
        '<div class="row"><div>생산팀</div><div>품질·설계</div><div>연구개발부서<br><small style="font-weight:500">연구개발전담부서 인정</small></div></div></div>')

    def cert(n, cap, sub):
        return f'<figure class="amp-cert amp-figure rv">{img(n, cap)}<figcaption>{cap}<small>{sub}</small></figcaption></figure>'
    certs = [
        ("cert-iso", "ISO 9001:2015 품질경영시스템 인증서", "한국품질보증원(KQA) · 유효 2026.09.08 ~ 2029.09.07 · 인증범위: 알루미늄 합금 파이프 가공에 대한 제조"),
        ("cert-venture", "벤처기업확인서", "혁신성장유형 · 2026.03.17 ~ 2029.03.16"),
        ("cert-root", "뿌리기업확인서", "2025.10.21 ~ 2028.10.20"),
        ("cert-rnd", "연구개발전담부서 인정서", "한국산업기술진흥협회 · 2025.10.14"),
        ("cert-youth", "전라남도 청년기업 인증서", "2025.08.25 ~ 2028.08.24"),
        ("cert-gscnu", "G-SCNU 강소지역기업 지정증서", "국립순천대학교 · 2025.07.10 ~ 2028.02.29"),
        ("cert-family-scnu", "국립순천대학교 가족회사 인증서", "2026.04.30"),
    ]
    awards = [("award-jeonnam", "전라남도지사 표창장", "2025.11.19"), ("award-smba", "중소벤처기업청장 상장", "2024.11.14")]
    company_page("/default/company/certification.html", "인증 및 제증명 | 에이엠피",
        "에이엠피의 ISO 9001, 벤처기업확인서, 뿌리기업확인서, 연구개발전담부서 인정서, 전라남도 청년기업 인증, G-SCNU 강소지역기업, 전라남도지사 표창, 중소벤처기업청장 상장.", "인증 및 제증명",
        '<h3 style="margin-top:0">인증·확인·지정</h3><div class="amp-grid c4">' + "".join(cert(*c) for c in certs) + '</div>'
        '<h3 style="margin-top:56px">수상</h3><div class="amp-grid c4">' + "".join(cert(*c) for c in awards) + '</div>'
        '<p class="amp-prose" style="margin-top:24px;font-size:14px;color:var(--ink-soft)">※ ISO 9001 인증범위는 알루미늄 합금 파이프 가공 제조입니다.</p>')

    def pc(title, lines):
        return ('<div class="amp-card rv"><div class="body"><h3>' + title + '</h3>' +
                "".join(f'<p style="margin-top:8px">{l}</p>' for l in lines) + '</div></div>')
    partners_html = (
        '<h3 style="margin-top:0">지자체·산업 협약</h3><div class="amp-grid c2">' +
        pc("광양시 이차전지 산업 상호협력과 공동발전을 위한 업무협약", [
            "2025.09.24 · 광양시와 이차전지 관련 기업이 이차전지 산업 생태계 조성과 산업경쟁력 강화를 위해 협력",
            "참여: 광양시, 전남테크노파크, 포스코퓨처엠, 포스코리튬솔루션, 포스코필바라리튬솔루션, 포스코HY클린메탈, SNNC, CIS케미칼, 광양이엔에스, 에이비알, 에콤, 엘케이엔텍, SE2Material, 에버인더스, 에이엠피"]) +
        pc("전남테크노파크", ["지역 기업 지원기관 · 위 협약에 함께 참여"]) +
        '</div>'
        '<h3 style="margin-top:48px">대학 산학협력</h3><div class="amp-grid c3">' +
        pc("국립순천대학교", ["글로컬대학 및 RISE사업 업무협약 (2025.08.14)", "AI중심대학사업단 상호협력 협약 (2026.02.09)",
                         "G-SCNU 강소지역기업 지정 (2025.07.10)", "가족회사 인증 (2026.04.30)"]) +
        pc("전남대학교", ["그린바이오 혁신융합대학사업단 산학협력 협약 (2025.08.29)"]) +
        pc("한영대학교", ["산학협력 협약 (2026.04.24)", "제철케미칼전공 산학협력위원회 위원 위촉 (2026.05.01~2028.05.31)"]) +
        '</div>'
        '<h3 style="margin-top:48px">해외 협력 · 이차전지 폐수처리</h3><div class="amp-grid c3">' +
        pc("ERAGON ENVIRO", ["이차전지 폐수처리 분야 업무협약 (2026.09.09)"]) +
        pc("厦门嘉戎技术股份有限公司", ["이차전지 폐수처리 분야 업무협약 (2026.09.10)"]) +
        pc("Jimei International Cooperation Center (集美国际合作中心)", ["이차전지 폐수처리 분야 업무협약 (2026.09.09)"]) +
        f'</div><p class="amp-prose" style="margin-top:14px">{todo("중국 협력사 1곳(2026.09.08 협약) 표기명 확인 및 해외 협력사 명칭 공개 동의 확인")}</p>'
        f'<p class="amp-prose" style="margin-top:24px">{todo("기존 협력기관 4곳(현 홈페이지 파트너) 추가")}</p>')
    company_page("/default/company/partners.html", "협력기관 | 에이엠피",
        "에이엠피의 협력기관 – 광양시 이차전지 산업 협약, 전남테크노파크, 순천대·전남대·한영대 산학협력, 이차전지 폐수처리 해외 협력.", "협력기관", partners_html)

    company_page("/default/company/location.html", "오시는 길 | 에이엠피",
        "에이엠피 본사(광양 익신산단), 지점·공장(광양 태인동 국가산단), 지점(여수 주삼동) 위치 안내.", "오시는 길",
        f'''<table class="amp-table">
<tr><th>본사</th><td>전남 광양시 광양읍 익신산단3길 40, 409호 (광양만권 소재부품 지식산업센터)<br>
<a href="{MAP_URL}" target="_blank" rel="noopener" style="text-decoration:underline">지도 보기</a></td></tr>
<tr><th>지점·공장</th><td>전남 광양시 태인5길 51-17, 가동 1층 (태인동, 광양국가산업단지) · 연구개발전담부서<br>
<a href="{MAP_URL_FACTORY}" target="_blank" rel="noopener" style="text-decoration:underline">지도 보기</a></td></tr>
<tr><th>사진</th><td><div class="amp-gallery c2" style="max-width:620px">{"".join(f'<figure>{img(n, a)}</figure>' for n, a in [("factory-exterior", "지점·공장 외관"), ("factory-interior", "공장 내부")])}</div></td></tr>
<tr><th>지점</th><td>전남 여수시 주삼동 (여수 융합지구) {todo("여수 지점 호수 106호 vs 202-01 확인")}</td></tr>
<tr><th>전화</th><td>{PHONE}</td></tr></table>''')


NEWS = [  # 회사 소개자료(2026.11) '뉴스 및 보도자료' – 제목은 원문 확인 후 기입
    ("인더스트리뉴스", "https://www.industrynews.co.kr/news/articleView.html?idxno=86403"),
    ("아시아경제 (네이버 뉴스)", "https://n.news.naver.com/article/277/0005791858?sid=102"),
    ("focusnjn.com", "https://www.focusnjn.com/article/1065599369053877"),
    ("국립순천대학교 소식", "https://www.scnu.ac.kr/SCNU/na/ntt/selectNttInfo.do?nttSn=281285119&mi=9097&currPage=1&listCo=10&searchType=sj&nttSttus=&searchValue=%EB%B2%A4%EC%B2%98"),
    ("매일일보", "https://www.m-i.kr/news/articleView.html?idxno=1286696"),
    ("광양시민신문", "https://www.gycitizen.com/news/articleView.html?idxno=50141"),
    ("focusnjn.com", "https://www.focusnjn.com/article/1065623432630770"),
    ("헤럴드경제 (네이버 뉴스)", "https://n.news.naver.com/article/016/0002487472?sid=102"),
    ("dailyjn.com", "https://www.dailyjn.com/news/articleView.html?idxno=87626"),
    ("내외뉴스통신", "https://www.naewaynews.com/316487"),
    ("YouTube 라이브", "https://www.youtube.com/live/tguODB7HDDE?feature=shared"),
    ("gndnews.co.kr", "https://www.gndnews.co.kr/news/articleView.html?idxno=260"),
]
EVENTS = [
    ("2026 중국 샤먼시 국제무역투자상담회", "광양시 대표단으로 참가해 이차전지 폐수처리 분야 협력기업과 업무협약을 체결했습니다.", [f"ev-xiamen-{i:02d}" for i in range(1, 13)]),
    ("2026 배터리 코리아", "전남 광양 스마트그린산단 공동관에서 이차전지 공정 수처리 기술을 소개했습니다.", ["ev-bk-01", "ev-bk-02", "ev-bk-03"]),
    ("2026 제5회 전남·광주 해외수출페스티벌", "해외 바이어와 수출 상담을 진행했습니다.", ["ev-export-01", "ev-export-02", "ev-export-03"]),
    ("2025 전남 벤처 스타트업 페스티벌", "부스를 운영하며 Clad AL Header Pipe와 수처리 설비를 전시했습니다.", ["ev-venture-01", "ev-venture-02", "ev-venture-03", "ev-venture-04"]),
    ("2025 전남형 청년창업사관학교 입교식", "1기 입교식에서 사업 아이템을 전시했습니다.", ["ev-ysa-01", "ev-ysa-02", "ev-ysa-03", "ev-ysa-04"]),
]


def build_news():
    news = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}<small>{urllib.parse.urlparse(u).netloc}</small></a></li>' for n, u in NEWS)
    ev = ""
    for t, d, imgs in EVENTS:
        ev += (f'<h3 style="margin-top:48px">{t}</h3><p class="amp-prose">{d}</p>' +
               f'<div class="amp-gallery">' + "".join(f'<figure class="rv">{img(k, t)}</figure>' for k in imgs) + '</div>')
    company_page("/default/company/news.html", "언론보도·활동 | 에이엠피",
        "에이엠피 언론보도와 활동 – 중국 샤먼 국제무역투자상담회, 배터리 코리아 2026, 전남·광주 해외수출페스티벌, 전남 벤처 스타트업 페스티벌.",
        "언론보도·활동",
        f'<h2 style="margin-top:0">언론보도</h2><ul class="amp-news">{news}</ul>'
        f'<p class="amp-prose" style="margin-top:12px">{todo("기사 제목·날짜 기입 (원문 확인 필요)")}</p>'
        f'<h2 style="margin-top:64px">활동</h2>{ev}')


# ───────────────────────── 공조부품 ─────────────────────────
def build_air():
    def air_page(path, h1, title, desc, inner):
        body = (subhead(h1, ["공조부품", h1], "Clad Aluminum Header Pipe", kind="air") + localnav("air", path) +
                f'<section class="amp-sec"><div class="amp-wrap">{inner}</div></section>')
        write(path, title, desc, body, "air")

    gal = "".join(f'<figure class="rv">{img(n, a)}<figcaption>{a}</figcaption></figure>' for n, a in [
        ("product-header-pipe", "원형 알루미늄 파이프"), ("product-pipe-assembly", "이형 단면 알루미늄 파이프"),
        ("product-heat-exchanger", "열교환기(Condenser) – 헤더 파이프 적용 위치"), ("product-atf-warmer", "ATF Warmer"),
        ("product-ev-cooler", "전기차 배터리 Cooler"), ("product-tube-stack", "실내기(증발기)")])
    air_page("/default/air/products.html", "제품 소개", "Clad Aluminum Header Pipe 제조 | 에이엠피",
        "Clad AL Header Pipe, Clad AL Pipe & Assembly, ATF Warmer, 전기차 배터리 Cooler, 실내기(증발기) 등 공조부품을 제조합니다.",
        f'''
{csp(["자동차 및 에어컨 공조부품", "전기차 배터리 Cooler 부품", "공조부품 제조사"],
     ["당사 노하우에 따른 외주 업체 품질 요인 및 생산 조건 관리", "금형 설계"],
     ["기존 외주 업체의 품질 관리 미숙", "Q-Cost 과다 발생", "공조기 규격에 따른 사이징 필요", "품질 향상을 위한 형상 변경 필요"],
     "신규 개발품을 통한 매출 증대 · Q-Cost 절감을 통한 수익률 증대", air=True)}
<div class="amp-split top" style="margin-top:56px">
  <div class="amp-prose">
    <h2>Clad Aluminum Header Pipe란?</h2>
    <p>공조시스템에 적용되는 브레이징 제품에 사용되는 부품입니다. 주로 자동차 열교환기(콘덴서, 에바, 히터, 라디에이터 등)와
    가정용 에어컨 열교환기(콘덴서, 에바)에 적용됩니다.</p>
    <p>용융점이 다른 알루미늄 합금(3000계, 4000계 등)을 클래딩한 판재를 <b>고주파 유도용접</b>으로 조관해 제작합니다.</p>
    <table class="amp-table"><tr><th>심재(Core)</th><td>알루미늄 합금(3000계 등), 용융점 630~660℃</td></tr>
    <tr><th>클래드층</th><td>Al-Si 합금(4000계 등), 용융점 577~610℃</td></tr>
    <tr><th>제작 방식</th><td>클래드 판재 → 고주파 유도용접 조관</td></tr></table>
  </div>
  <div style="display:grid;gap:16px">
    <figure class="amp-figure wide">{img("clad-line", "알루미늄 클래딩 라인 도식")}<figcaption>알루미늄 클래딩 라인</figcaption></figure>
    <figure class="amp-figure wide">{img("clad-sheet", "용융점이 서로 다른 알루미늄 클래드 판재 단면")}<figcaption>용융점이 서로 다른 알루미늄 클래드 판재</figcaption></figure>
  </div>
</div>
<h2 style="margin-top:56px">주력 제품</h2>
<div class="amp-gallery" style="margin-top:20px">{gal}</div>
<h2 style="margin-top:56px">생산 설비</h2>
<div class="amp-split top">
  <figure class="amp-figure rv">{img("air-drawbench", "3구 인발기")}<figcaption>3구 인발기</figcaption></figure>
  <figure class="amp-figure rv d2">{img("air-dies", "다이스·플러그와 소구경 알루미늄 파이프")}<figcaption>다이스 및 플러그(좌), 소구경 Al Pipe(우)</figcaption></figure>
</div>
<p class="amp-prose" style="margin-top:14px">Target Item: ATF Warmer, 전기차 배터리 Cooler, 실내기(증발기)</p>
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
<h2 style="margin-top:56px">주요 생산 현황</h2>
<p class="amp-prose">차량용 Clad AL Header Pipe 제작 및 출고</p>
{gallery([("prod-02", "생산 공장 전경"), ("prod-06", "절단 가공품 적재"), ("prod-07", "규격별 가공품"), ("air-case-02", "포장 대기 제품"),
          ("prod-08", "설비 점검"), ("air-case-03", "가공품 검사"), ("air-case-01", "출고 적재"), ("prod-01", "트럭 출고"), ("prod-05", "절단 라인")])}
<h3>창업 준비 과정</h3>
{gallery([("prep-01", "작업대 제작"), ("prep-02", "세척 설비 설치"), ("prep-03", "절단 라인 구성"), ("prep-04", "가공품 적재")], "c2")}
<h3>설비 제작 과정</h3>
{gallery([("build-01", "가공 설비 제작"), ("build-02", "설비 조립"), ("build-03", "설비 시운전"), ("build-04", "완성 설비")], "c2")}
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


def csp(customer, solution, problem, goal, air=False):
    """회사 소개자료(2026.11)의 Customer · Solution · Problem 구조."""
    col = lambda cls, en, ko, items: (f'<div class="{cls}"><h4>{en}</h4><h3>{ko}</h3><ul>' +
                                      "".join(f"<li>{i}</li>" for i in items) + "</ul></div>")
    return (f'<div class="amp-csp rv{" air" if air else ""}">' + col("", "CUSTOMER", "고객", customer) +
            col("sol", "SOLUTION", "에이엠피의 해결", solution) + col("", "PROBLEM", "현장의 문제", problem) +
            f'</div><div class="amp-goal rv{" air" if air else ""}">{goal}</div>')


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
        "이차전지 전구체·양극재 공정의 망초폐수(고농도 염폐수)를 Filter·EDR(전기투석 반전법) 4단·증발농축으로 처리해 공정수로 재사용하는 시스템과 전구체 공침반응기를 제작합니다.",
        "전구체·양극재 공정 폐수를 처리해 공정수로 다시 씁니다", "pilot-01",
        "<p>양극재 생산 과정에서 고농도 염폐수(망초폐수, Na₂SO₄)가 전주기적으로 발생합니다.</p>"
        "<p>캐즘 이후 시장이 다시 살아나면서 폐수량은 늘지만, 기존 종말처리장으로는 처리에 한계가 있습니다.</p>",
        csp(["전구체 제조 시 과량의 폐수가 발생하는 기업", "공침 반응 및 세척 공정", "재순환으로 신규 용수 사용량 절감", "재사용량 증가에 따른 비용 절감"],
            ["전기투석(EDR) 기반 처리 공정 도입", "폐수 및 공정수의 재이용수화", "재순환·역세 공정으로 생산성 향상 및 부적합률 절감"],
            ["캐즘 이후 재활성화 시장", "전주기적 폐수 발생", "양극재 생성 시 고농도 염폐수 발생", "기존 종말처리장 처리 문제"],
            "전구체·양극재 공정 폐수 재사용량 증가 · 생산 비용 절감 · 고농도 염폐수 처리로 환경 오염 부하 절감") +
        '<h3>망초폐수 처리 공정</h3>' +
        flowline([("drop", "원수", "망초폐수"), ("filter", "Filter", "전처리"), ("bolt", "EDR #1~#4", "전기투석 반전법 4단"), ("recycle", "재사용 공정수 투입", "처리수 재이용")]) +
        checks(["EDR 농축수는 증발 농축을 거쳐 응집수(재이용)와 슬러지로 분리합니다.",
                "연계 장비: 전구체 공침반응기(Lab 5L ~ 50L급), pH·투입량 이상 감지 및 제어 프로그램"]) +
        f'''<figure class="amp-figure wide rv" style="margin-top:26px">{img("edr-flow", "이차전지 망초폐수 처리시스템 공정도")}<figcaption>이차전지 망초폐수 처리시스템 공정도</figcaption></figure>
<div class="amp-split top" style="margin-top:30px">
  <figure class="amp-figure wide rv">{img("edr-ion", "EDR 전기투석 반전법 원리")}<figcaption>EDR(전기투석 반전법) 원리</figcaption></figure>
  <figure class="amp-figure wide rv d2">{img("edr-cell", "EDR 셀 구조도")}<figcaption>EDR 셀 구조도 – 전극·스페이서·멤브레인</figcaption></figure></div>
<h3 style="margin-top:40px">공침 공정 장비</h3>
<div class="amp-split top">
  <figure class="amp-figure rv">{img("coprecip-process", "공침 공정 장비")}<figcaption>공침 공정</figcaption></figure>
  <figure class="amp-figure rv d2">{img("precursor-material", "전구체와 양극재 시료")}<figcaption>전구체·양극재 시료</figcaption></figure></div>
<div class="amp-split top" style="margin-top:20px">
  <figure class="amp-figure wide rv">{img("reactor-diagram-50l", "50L 공침 반응기 구성 개념도")}<figcaption>50L 공침 반응기 구성 개념도</figcaption></figure>
  <div></div></div>''',
        '<p class="amp-prose">이차전지 폐수처리 Pilot, 전구체 공침 반응기, 전구체 입자선별·필터 장치를 제작했습니다.</p>' +
        gallery([("pilot-01", "이차전지 폐수 처리 시스템 Pilot"), ("pilot-02", "Pilot 시스템(다른 각도)"),
                 ("reactor-lab-01", "전구체 공침 반응기"), ("reactor-lab-02", "공침 반응기 제어부"),
                 ("module-b1", "전구체 입자선별 및 필터 장치"), ("module-b2", "입자선별 필터 장치(다른 각도)")]) +
        '<h3>공침반응기 제작 과정</h3>' +
        gallery([("reactor-01", "판재 절단·가공"), ("reactor-02", "스테인리스 용접"), ("reactor-03", "조립·치수 확인"),
                 ("reactor-04", "교반부(임펠러)"), ("reactor-05", "상부 포트·클램프 조립"), ("reactor-site-01", "설치·점검")]) +
        '<h3>광양시 이차전지 협의체</h3><p class="amp-prose">광양시 이차전지 산업 상호협력과 공동발전을 위한 업무협약(2025.09.24)에 참여하고 있습니다.</p>' +
        gallery([("gy-battery-01", "광양시 이차전지 업무협약"), ("gy-battery-02", "광양시 이차전지 기업협의체 간담회"), ("gy-battery-03", "광양시 이차전지 기업 행사")]) +
        f'<p class="amp-prose" style="margin-top:12px">{todo("고객사명은 익명(S社) 표기 유지 – 공개 범위 AMP 확인")}</p>')

    field_page("/default/water/recycle.html", "recycle", "공정수 재순환", "공정수 재순환",
        "공정수 재순환 시스템 | 에이엠피",
        "공정수 사용량과 폐수 배출을 줄이는 현장 맞춤형 공정수 재순환·재이용 시스템과 입자선별·필터 장치, 수질 모니터링 연동.",
        "공정수 사용량·폐수 배출량을 줄이는 현장 맞춤형 재이용 시스템", "module-a1",
        "<p>공정수 사용량과 폐수 배출량이 늘면서 원가와 ESG 부담이 커지고 있습니다.</p>",
        flowline([("search", "현장·수질 진단", "원수 확인"), ("tank", "재순환 모듈", "현장 맞춤 설계"), ("filter", "입자선별·필터", "고형물 분리"), ("activity", "모니터링 연동", "수질 확인")]) +
        checks(["현장 맞춤형 재순환 모듈", "입자선별·필터 장치", "수질 모니터링 연동"]),
        '<p class="amp-prose">공정수 재순환 현장 맞춤형 시스템을 제작했습니다.</p>' +
        gallery([("module-a1", "공정수 재순환 현장 맞춤형 시스템"), ("module-a2", "재순환 모듈 설치 구성")], "c2"))

    field_page("/default/water/aquaculture.html", "aqua", "육상양식 물관리", "육상양식 물관리",
        "육상양식 수처리·수질 모니터링 | 에이엠피",
        "순환여과 방식 육상양식장의 폐해수를 여과·가압부상·폭기·UV·바이오볼 여과로 처리해 재이용하고, 실시간 모니터링·대시보드로 수질을 관리합니다.",
        "순환여과 방식으로 양식장 물을 다시 쓰고, 데이터로 관리합니다", "aqua-05",
        "<p>육상양식은 아질산, DO, 탁도·SS 변동에 민감해 수질이 흔들리면 대량 폐사로 이어질 수 있습니다.</p>"
        "<p>지금은 물교환에 의존하고 있어 교체수 확보와 배출수 처리 비용이 부담입니다.</p>",
        csp(["폐해수 처리 후 재이용수 재순환", "농축수·슬러지 분리 관리", "실시간 모니터링·대시보드", "권장 조치 가이드 제공"],
            ["물관리 시스템화", "폐해수의 재이용수화", "분리 관리로 환경 리스크 최소화", "슬러지 자원화(액비·비료 등) 확장"],
            ["아질산, DO, 탁도·SS 변동에 민감", "수질 변동 시 대량 폐사 위험", "현재 물교환에 의존", "교체수 확보 및 처리 비용 문제"],
            "신규 유입수 절감 및 배출수 오염 부하 절감 · 군락형 모델 패키지 설계") +
        '<h3>육상양식 물관리 시스템 공정</h3>' +
        '<ol class="amp-steps rv">' + "".join(f"<li>{x}</li>" for x in ["원수(폐해수)", "1차 여과(활성탄)", "가압부상조(SS·침전)", "폭기조(DO 관리)", "Reaction(UV 살균)", "2차 여과(바이오볼)", "배양 수조(미생물)", "재이용수 투입(온도·pH·미생물 보정)", "양식수조(새우 양식)"]) + '</ol>' +
        checks(["가압부상조에서 분리한 슬러지는 액비·비료 등으로 자원화합니다.", "수질 센서(pH, EC, 온도, 탁도, TDS, DO)와 원격 대시보드·알림으로 상태를 확인합니다."]) +
        f'''<figure class="amp-figure wide rv" style="margin-top:26px">{img("aqua-flow", "육상양식 물관리 시스템 공정도")}<figcaption>육상양식 물관리 시스템 공정도</figcaption></figure>
<div class="amp-split top" style="margin-top:30px">
  <figure class="amp-figure wide rv">{img("aqua-concept", "육상양식장 재순환 물관리 시스템 기술 개요도")}<figcaption>육상양식 물관리 시스템 기술 개요도</figcaption></figure>
  <figure class="amp-figure wide rv d2">{img("aqua-package", "물관리 센터 1개와 양식장 10개소 군락형 패키지 모델 개요도")}<figcaption>물관리 센터형 군락 패키지 모델 개요도(물관리 센터 1 + 양식장 10)</figcaption></figure></div>''' +
        f'<p class="amp-prose" style="margin-top:14px">연계 과제: 미생물 자동 배양수조 개발 (블루스타트업) {todo("과제 완료 후 사진 추가, 대외 표기 가능 여부 확인")}</p>',
        checks(["물관리 시스템 시작품 제작 – 필터, 수조 및 폭기조", "양식어가 수질 센서 및 물관리 시스템 검증 (2025)", "무안 소재 양식장 유지보수"]) +
        '<h3>시작품 제작</h3>' +
        gallery([("aqua-proto-01", "필터·수조 시작품"), ("aqua-proto-02", "수조 용접 제작"), ("aqua-proto-03", "수조 시작품"), ("aqua-proto-04", "폭기조 시작품")], "c2") +
        '<h3>양식장 현장</h3>' +
        gallery([("aqua-01", "육상양식 수조 현장"), ("aqua-02", "원형 수조"), ("aqua-05", "양식장 수조 전경"),
                 ("aqua-06", "수조 수질 상태"), ("aqua-07", "수조 점검"), ("aqua-04", "수조 표면 상태")]) +
        f'<p class="amp-prose" style="margin-top:12px">{todo("고객은 C社(양식어가) 익명 – 양식장 위치 노출 가능 여부 확인")}</p>')

    field_page("/default/water/pharma.html", "pharma", "제약·화학 폐수처리", "제약·화학 폐수처리",
        "제약·화학 폐수처리 시스템 | 에이엠피",
        "원수 성상이 현장마다 다른 제약·화학 폐수를 원수 분석 기반으로 공정을 구성하고 소규모·Pilot 규모로 맞춤 제작합니다.",
        "원수 분석에서 출발하는 맞춤형 수처리 시스템", "pharma-01",
        "<p>제약·화학 공정은 원수 성상이 현장마다 달라, 표준 설비만으로는 처리 목표를 달성하기 어렵습니다.</p>",
        flowline([("flask", "원수 분석", "성상 파악"), ("target", "공정 구성", "처리목표 기반"), ("tank", "맞춤 제작", "소규모·Pilot"), ("play", "설치·시운전", "처리 확인")]) +
        checks(["원수 분석 결과를 기준으로 공정을 구성합니다.", "소규모·Pilot 규모부터 맞춤 제작합니다."]),
        '<p class="amp-prose">제약 공정 수처리 시설 설치 공사를 수행했습니다. 수조 구조물 제작부터 배관·펌프 설치까지 진행했습니다.</p>' +
        gallery([("pharma-01", "수처리 설비 배관·밸브 설치"), ("pharma-02", "수조 반입·설치"), ("pharma-03", "설치 전 현장"),
                 ("pharma-04", "철골 수조 구조물 제작"), ("pharma-05", "배관·펌프 라인"), ("pharma-06", "수조 구조물 조립"),
                 ("pharma-07", "수조 구조물 제작"), ("pharma-08", "수조 설치 공사")]))


# ───────────────────────── 시공사례 ─────────────────────────
def build_portfolio():
    def card(n, alt, cat, tag, title, text, meta, tagcls=""):
        im = f'<div class="imgwrap">{img(n, alt)}</div>'
        return (f'<div class="amp-card rv" data-cat="{cat}">{im}<div class="body"><span class="tag {tagcls}">{tag}</span>'
                f'<h3>{title}</h3><p>{text}</p><div class="meta">{meta}</div></div></div>')

    water = [
        card("reactor-lab-01", "전구체 공침 반응기", "battery", "이차전지", "전구체 공침 반응기 제작", "전구체 공침 공정용 실험실 규모 반응기를 맞춤 제작.", "고객: 대학·연구소 / 양극재사"),
        card("pilot-01", "이차전지 폐수처리 Pilot", "battery", "이차전지", "이차전지 폐수처리 Pilot", "고염 폐수 처리 공정을 시험하는 Pilot 설비 제작.", ""),
        card("module-a1", "공정수 재순환 시스템", "recycle", "공정수", "공정수 재순환 현장 맞춤형 시스템", "현장 조건에 맞춘 재순환 모듈 제작.", ""),
        card("module-b1", "전구체 입자선별 및 필터 장치", "battery", "이차전지", "전구체 입자선별 및 필터 장치", "전구체 입자 선별용 필터 장치 제작.", "고객: S社(양극재)"),
        card("pharma-01", "제약 공정 수처리 시설", "pharma", "제약·화학", "수처리 시설 설치 공사 – 제약 공정", "수조 구조물 제작, 배관·펌프 설치까지 수행.", ""),
        card("aqua-proto-01", "육상양식 물관리 시스템 시작품", "aqua", "육상양식", "육상양식 물관리 시스템 시작품", "필터, 수조 및 폭기조 시작품 제작.", ""),
        card("coprecip-process", "공침 공정 장비", "battery", "이차전지", "전구체 공침 공정 장비", "공침 반응 공정과 전구체·양극재 시료 제작 지원.", ""),
        card("monitor-screen", "수질 실시간 모니터링 프로그램 화면", "common", "공통", "수질 실시간 모니터링 프로그램·센서", "pH, EC, 온도, 탁도, TDS, DO 측정 및 데이터 관리.", ""),
        card("aqua-01", "육상양식 수조", "aqua", "육상양식", "양식어가 수질센서·물관리 시스템 검증", "양식 수조 수질 센서와 물관리 시스템을 검증.", "고객: C社(양식어가) · 2025"),
        card("supply-01", "원료 가공·소모품 납품", "battery", "이차전지", "원료 가공·소모품 납품", "이차전지 양극재 공정용 원료 가공 및 소모품 납품.", "고객: S社(양극재) · 2025"),
    ]
    flt = '<div class="amp-filter">' + "".join(
        f'<button data-filter="{k}"{" class=on" if k == "all" else ""}>{v}</button>'.replace("class=on", 'class="on"') for k, v in
        [("all", "전체"), ("battery", "이차전지"), ("recycle", "공정수"), ("aqua", "육상양식"), ("pharma", "제약·화학"), ("common", "공통")]) + "</div>"
    body = (subhead("수처리·공정장비 실적", ["시공사례·납품실적", "수처리·공정장비 실적"], "분야별로 제작·설치한 설비와 납품 실적입니다.", bg="pilot-02") +
            localnav("portfolio", "/default/portfolio/water.html") +
            f'<section class="amp-sec"><div class="amp-wrap">{flt}<div class="amp-grid c3">{"".join(water)}</div></div></section>' + banner())
    write("/default/portfolio/water.html", "시공사례·납품실적 | 에이엠피",
          "에이엠피의 수처리·공정장비 시공사례와 납품실적 – 공침반응기, 폐수처리 Pilot, 공정수 재순환, 수질 모니터링, 육상양식.", body, "portfolio")

    air = [card("air-case-01", "차량용 Clad AL Header Pipe 출고", "air", "공조부품", "차량용 Clad AL Header Pipe 제작·출고", "자동차 공조부품용 헤더 파이프를 제작해 출고.", "", "air"),
           card("air-case-02", "Clad AL Header Pipe 포장", "air", "공조부품", "Clad AL Header Pipe 포장·납품", "규격별 절단·디버링·세척 후 포장해 납품.", "", "air"),
           card("air-case-03", "Clad AL Header Pipe 가공품", "air", "공조부품", "Clad AL Header Pipe 가공품", "사이징·절단 가공품 검사.", "", "air"),
           card("prod-01", "제품 출고", "air", "공조부품", "제품 출고", "트럭 적재·출고.", "", "air"),
           card("build-04", "자체 제작 생산 설비", "air", "공조부품", "생산 설비 자체 제작", "절단·가공 설비를 자체 제작해 라인 구성.", "", "air"),
           card("prod-05", "생산 라인", "air", "공조부품", "생산 라인 운영", "절단·디버링 라인에서 공정별 작업표준서 운영.", "", "air")]
    body = (subhead("공조부품 실적", ["시공사례·납품실적", "공조부품 실적"], "Clad AL Header Pipe 등 공조부품 가공·납품 실적입니다.", kind="air") +
            localnav("portfolio", "/default/portfolio/air.html") +
            f'<section class="amp-sec"><div class="amp-wrap"><div class="amp-grid c3">{"".join(air)}</div>'
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
<table class="amp-table"><tr><th>전화</th><td>{PHONE}</td></tr><tr><th>이메일</th><td>{todo("대표 이메일")}</td></tr>
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


# 정보 공백/확인 항목 → (구분, 해소 방법)
TODO_INFO = {
    "대표 이메일": ("연락처", "홈페이지에 표시할 대표 이메일"),
    "여수 지점 호수 106호 vs 202-01 확인": ("연락처", "여수 주삼동 지점의 정확한 호수 (106호 / 202-01 중 확인)"),
    "현 홈페이지 company 연혁 원문 붙여넣기": ("회사 내용", "현 홈페이지 연혁 원문 (소스를 받으면 직접 추출 가능)"),
    "생산팀·품질·설계 조직 구성 AMP 확인 후 수정": ("회사 내용", "생산팀·품질·설계의 실제 조직 구성(연구개발부서는 인정서 기준으로 반영함)"),
    "기존 협력기관 4곳(현 홈페이지 파트너) 추가": ("회사 내용", "현 홈페이지 '파트너' 4곳 (소스를 받으면 직접 추출 가능)"),
    "중국 협력사 1곳(2026.09.08 협약) 표기명 확인 및 해외 협력사 명칭 공개 동의 확인": ("공개 범위 확인", "해외 협력사 4곳 중 판독이 안 된 1곳의 정확한 명칭, 그리고 4곳 모두 홈페이지에 명칭 공개해도 되는지"),
    "공개 가능 범위 AMP 확인": ("공개 범위 확인", "2026년 스마트제조 전환지원·AI솔루션 구축지원 수행 사실을 연혁에 공개해도 되는지"),
    "고객사명은 익명(S社) 표기 유지 – 공개 범위 AMP 확인": ("공개 범위 확인", "양극재사(S社) 실명 공개 여부 (기본은 익명 유지)"),
    "고객은 C社(양식어가) 익명 – 양식장 위치 노출 가능 여부 확인": ("공개 범위 확인", "양식어가(C社) 실명·양식장 위치 노출 가능 여부"),
    "작업표준서에 고객사명·품번·담당자 실명이 보임 – 게시 범위 AMP 최종 확인(필요 시 해당 부분 가림 처리)": ("공개 범위 확인", "작업표준서 3장에 보이는 고객사명·품번·담당자 실명의 게시 여부 (안 되면 가림 처리본 필요)"),
    "과제 완료 후 사진 추가, 대외 표기 가능 여부 확인": ("공개 범위 확인", "블루스타트업 '미생물 자동 배양수조' 과제를 대외 표기해도 되는지, 완료 후 사진"),
    "기사 제목·날짜 기입 (원문 확인 필요)": ("회사 내용", "언론보도 12건의 기사 제목·날짜 (이 환경에서는 기사 사이트 접속이 막혀 링크와 매체명만 넣음. 매체명이 도메인으로 표시된 4건은 매체명 확인)"),
    "보유기간 AMP 확인": ("공개 범위 확인", "문의 개인정보 보유기간 (현재 임의로 '1년' 기재)"),
    "기존 게시판(DB 연동) 페이지와 연결하거나, 공지가 생기면 이 화면에 목록 추가": ("서버·운영", "기존 공지사항 게시판(DB) 연결 여부 / 등록할 공지"),
}
CAT_ORDER = ["연락처", "회사 내용", "공개 범위 확인", "서버·운영"]


def build_photo_list():
    import datetime
    page_title = {"/default/index.html": "메인"}
    for _, label, _, subs in NAV:
        for t, h in subs:
            page_title[h] = f"{label} > {t}"
    order = list(page_title)

    def pages_of(ps, all_pages=23):
        ps = sorted(ps, key=lambda x: order.index(x) if x in order else 99)
        return "전 페이지 푸터" if len(ps) >= 15 else ", ".join(page_title.get(p, p) for p in ps)

    photos = [(k, PHOTO_SPEC.get(k, (k, "", "4/3", False)), PH_USED[k]) for k in PHOTO_SPEC if k in PH_USED]
    req = [k for k, v, _ in photos if not v[3]]
    todos = {c: [] for c in CAT_ORDER}
    for t, ps in TODO_USED.items():
        cat, how = TODO_INFO.get(t, ("회사 내용", t))
        todos.setdefault(cat, []).append((t, how, ps))
    n_todo = sum(len(v) for v in todos.values())

    L = ["# 공백으로 남은 곳 · 필요한 자료 목록", "",
         f"- 기준일: {datetime.date.today().isoformat()} (자동 생성 문서 – 직접 고치지 말고 `tools/build_draft.py` 수정 후 `python3 tools/build_draft.py` 재실행)",
         "- 대상: `site_draft/` 초안 사이트 19페이지",
         f"- 요약: **사진 자리 {len(photos)}곳**(필수 {len(req)}·선택 {len(photos) - len(req)}), **정보·확인 공백 {n_todo}종**, 공통 자산 7종",
         "- 화면 표시: 사진 자리는 점선 박스(\"사진 필요\"), 정보 공백은 노란색 `[ ]` 표식으로 보입니다.", "",
         "---", "", "## 1. AMP에 요청할 것 (체크리스트)", "",
         "### A. 사진", "",
         f"아래 파일명 그대로 `site_draft/default/img/`에 JPG로 넣고 재빌드하면 해당 자리가 자동으로 사진으로 바뀝니다. 필수 {len(req)}장, 선택 {len(photos) - len(req)}장.", "",
         "| ☐ | No | 파일명 | 필요한 사진 | 규격·비고 | 구분 | 사용 위치 | 임시 자료 |", "|---|---|---|---|---|---|---|---|"]
    for n, (k, (title, spec, ratio, opt), ps) in enumerate(photos, 1):
        tmp = ROOT.parent / "자료" / "임시_저해상도" / f"{k}.jpg"
        tmp_s = f"`자료/임시_저해상도/{k}.jpg` (저해상도·참고용)" if tmp.exists() else "없음"
        L.append(f"| ☐ | P{n:02d} | `{k}.jpg` | {title} | {spec or DEFAULT_SPEC} | {'선택' if opt else '필수'} | {pages_of(ps)} | {tmp_s} |")
    L += ["", "**우선순위(첫 화면에 보이는 순서)**: ① `monitor-screen`(메인 히어로 패널) ② `pilot-01`·`module-a1`·`pharma-01`(메인 적용 분야 카드) ③ `reactor-lab-01`·`pilot-02`(메인 실적 카드) ④ 공조부품 제품 6장 ⑤ 나머지", ""]
    names = {"연락처": "B. 연락처·주소", "회사 내용": "C. 회사 내용", "공개 범위 확인": "D. 공개 범위·가부 확인 (AMP 결정 사항)", "서버·운영": "E. 서버·운영"}
    for cat in CAT_ORDER:
        if not todos.get(cat):
            continue
        L += [f"### {names[cat]}", "", "| ☐ | 필요한 것 | 화면 표식 | 나오는 위치 |", "|---|---|---|---|"]
        for t, how, ps in todos[cat]:
            L.append(f"| ☐ | {how} | `[{t if len(t) < 30 else t[:28] + '…'}]` | {pages_of(ps)} |")
        L.append("")
    assets = [
        "| ☐ | 로고 원본(AI/SVG) | 헤더·푸터·파비콘 | 회사 소개자료의 로고(370×101 투명 PNG)로 교체함. 고해상도 화면·인쇄용으로 벡터 원본이 있으면 좋음 |",
        "| ☐ | 작업표준서 공개본(고객사명·품번·담당자 실명 가림) | 공조부품 > 생산·품질 | D의 작업표준서 건이 '게시 불가'일 때만 필요. 지금은 원본 그대로 사용 중 |",
        "| ☐ | 인물이 나온 사진 사용 확인 | 이차전지 폐수처리, 공조부품 생산 현황, 언론보도·활동 | 회사 소개자료(AMP 제공)의 행사·작업 사진에 직원·외부 관계자 얼굴이 보임. 외부인(협약 상대·바이어 등) 게시가 괜찮은지 확인 |",
        "| ☐ | 인증서 이미지 노출 범위 확인 | 인증 및 제증명, 메인 신뢰 지표 | 벤처·뿌리기업 확인서에 사업자등록번호·법인번호·QR, ISO 인증서에 인증번호·QR이 보임. 전라남도 청년기업 인증서의 대표자 생년월일은 가림 처리함 |",
        "| ☐ | 협약서 원본 비공개 확인 | 협력기관 | 협약서 이미지는 서명·내부 조항이 있어 게시하지 않고 기관명·체결일만 텍스트로 게시 중 |",
        "| ☐ | 미생물 자동 배양수조 사진 | 육상양식 물관리 | 블루스타트업 과제 완료 후. 현재 페이지에는 자리 없음(문구만) |",
        "| ☐ | 카페24 FTP 계정 또는 사이트 소스 일체, 관리자 계정 | 실서버 반영, 기존 연혁·파트너·갤러리 이관 | `CLAUDE.md` 미결 사항 1·2번 |",
    ]
    L += ["### F. 사진 외 공통 자산", "",
          "| ☐ | 항목 | 용도 | 비고 |", "|---|---|---|---|"] + assets + [
          "", "---", "", "## 2. 지금 화면에 임의로 채운 것 (승인·검증 필요)", "",
          "공백은 아니지만 근거가 약해 AMP 승인이나 출처 확인이 필요한 항목입니다.", "",
          "| 항목 | 위치 | 내용 | 확인할 것 |", "|---|---|---|---|",
          "| 메인 슬로건·히어로 문구 | 메인 | \"현장에 맞춘 설비, 데이터로 관리하는 물\" 등 | AMP 최종 승인 (기획안에서 컬리버 초안) |",
          "| 인사말 | 회사소개 > 인사말 | 수처리 중심으로 새로 작성 | AMP 최종 승인, \"가장 저렴한 가격\" 문구는 삭제함 |",
          "| FAQ 답변 8건 | 고객센터 > FAQ | 기획안의 질문 8개에 컬리버가 답변 작성 | 답변 내용이 실제 응대 방식과 맞는지 |",
          "| 대표번호 0507-1486-0997 | 전 페이지 푸터, 오시는 길, 견적·기술상담 | 공장등록증명(신청)서에 신청인 전화번호로 적힌 번호를 사용 | 홈페이지에 공개할 대표번호가 맞는지 |",
          "| 연혁 구성 | 회사소개 > 연혁 | 회사 소개자료 연혁 16건 + 인증서·협약서 날짜를 합침 | 청년창업사관학교: 소개자료는 \"2024.04 수행 완료\", 졸업장 날짜는 2025.02.13 – 어느 쪽으로 표기할지 |",
          "| 연혁·협력기관의 협약 체결일 | 연혁, 협력기관 | 협약서·인증서에 적힌 날짜 그대로 | 날짜 오기 없는지, 협약 사실을 대외 공개해도 되는지 |",
          "| 연구개발부서 위치 | 오시는 길 | 인정서·소개자료 기준으로 태인동 지점·공장에 표기 | 기획안의 \"연구: 여수 지점\"과 다름 |",
          "| 대표 약력 | 인사말 > 회사 개요 | 소개자료의 \"화공 석사, 제조업 부설연구소 및 품질 업무 10년 이상\"을 반영. 출생연도는 개인정보라 뺌 | 공개 문구 |",
          "| ISO 9001 인증범위 | 인증 및 제증명, 메인 신뢰 지표 | 인증서 범위가 \"알루미늄 합금 파이프 가공에 대한 제조\"라 수처리 설비에는 해당하지 않음 | 수처리 품질로 오해되지 않는 표기 문구 |",
          "| 50L 공침 반응기 구성도 | 이차전지 폐수처리 | 1차 자료의 도식(출처 불명). ZLD 도식은 회사 소개자료의 EDR 공정도로 교체해 삭제함 | 50L 반응기 도식 출처 |",
          "| 육상양식 개요도 2종 | 육상양식 물관리 | 회사 소개자료의 기술 개요도·패키지 모델 개요도(일러스트) | 실제 설비가 아닌 개념도로 읽히는지 (캡션에 \"개요도\"로 표기) |",
          "| 이차전지 해결 방식 문구 | 이차전지 폐수처리 | 소개자료의 \"처리 공정 도입(전기분해)\"를 공정도에 맞춰 \"전기투석(EDR) 기반\"으로 표기 | 표현이 맞는지 |",
          "| 수치 카드 | 메인 | 7단계·4개 분야·6종·7개 인증 | 7개 = ISO 9001, 벤처, 뿌리기업, 연구개발전담부서, 전남 청년기업, G-SCNU 강소지역기업, 순천대 가족회사 |",
          "", "---", "", "## 2-1. 받은 자료 중 사이트에 쓰지 않은 것", "",
          "| 자료 | 이유 |", "|---|---|",
          "| 공장등록증명(신청)서 | 법인등록번호·종업원 수 등이 있어 게시 부적합. 공장 주소와 대표 전화번호만 확인용으로 사용 |",
          "| 민주평화통일자문회의 위촉장(대통령 명의) | 대표 개인의 위촉이고 정치적 성격이 있어 제외. 필요하면 AMP 확인 후 추가 |",
          "| 청년창업사관학교 졸업장 | 이미지는 제외하고 연혁에 텍스트로만 반영 |",
          "| 한영대학교 위촉장 | 이미지는 제외하고 연혁·협력기관에 텍스트로만 반영 |",
          "| 업무협약서 15종(국내 대학·광양시·중국 기업) | 서명·내부 조항이 있어 원본은 게시하지 않고 기관명·체결일만 텍스트로 반영 |",
          "| 전남한국줄넘기협회 등 업무협약서(2026.10.31) | 수처리·공조부품과 무관한 굿즈·소상공인 협력 건이라 제외 |",
          "", "---", "", "## 3. 사이트에서 공백이 보이는 위치 (페이지별)", ""]
    by_page = {}
    for k, (title, spec, ratio, opt), ps in photos:
        for p in ps:
            by_page.setdefault(p, {"photo": [], "todo": []})["photo"].append(f"`{k}.jpg`{'(선택)' if opt else ''}")
    for t, ps in TODO_USED.items():
        if len(ps) >= 15:
            continue
        for p in ps:
            by_page.setdefault(p, {"photo": [], "todo": []})["todo"].append(t if len(t) < 40 else t[:38] + "…")
    L += ["| 페이지 | 사진 자리 | 정보 공백 |", "|---|---|---|"]
    for p in sorted(by_page, key=lambda x: order.index(x) if x in order else 99):
        L.append(f"| {page_title.get(p, p)} | {', '.join(by_page[p]['photo']) or '-'} | {'; '.join(by_page[p]['todo']) or '-'} |")
    L += ["", "※ 모든 페이지 푸터와 견적·기술상담 영역에는 `[대표 이메일]` 표식이 들어갑니다.", "",
          "---", "", "## 4. 사진 규격 (AMP 전달용)", "",
          "- 형식: JPG, 가로 1600px 이상, 가로 방향(4:3 또는 16:9). 스크린샷은 PNG로 받아도 되며 사이트에 넣을 때 JPG로 변환",
          "- 휴대폰 원본 그대로 괜찮습니다(리사이즈·압축하지 말 것). 메신저로 보내면 화질이 줄어드니 메일·드라이브 권장",
          "- 설비는 전체가 보이는 컷 1장 + 다른 각도 1장이 가장 좋습니다",
          "- 사람 얼굴이 크게 나오는 컷은 피하거나 사용 동의를 함께 받을 것",
          "- 고객사 로고·간판·서류가 찍힌 경우 알려 주세요(가림 처리가 필요할 수 있음)", ""]
    out = ROOT.parent / "자료" / "공백_및_필요자료_목록.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"photo placeholders: {len(photos)}, todo kinds: {n_todo}")


def main():
    build_index()
    build_company()
    build_news()
    build_air()
    build_water()
    build_portfolio()
    build_cscenter()
    build_seo_files()
    build_photo_list()
    print("pages:", len(PAGES))


if __name__ == "__main__":
    main()
