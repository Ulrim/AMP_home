#!/usr/bin/env python3
"""에이엠피 홈페이지 리뉴얼 초안 생성기.

사용법:  python3 tools/build_draft.py
출력:    site_draft/  (UTF-8 정적 HTML, robots.txt, sitemap.xml)

공통 헤더·푸터·메타 태그를 한 곳에서 관리하기 위한 스크립트이며, 결과물(HTML)만 배포해도 된다.
이미지(site_draft/default/img)와 CSS/JS는 이 스크립트가 만들지 않는다.
"""
import json
import os
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent / "site_draft"
SITE = "https://www.amp0404.co.kr"
MAP_URL = "https://map.naver.com/p/search/" + urllib.parse.quote("전남 광양시 광양읍 익신산단3길 40")
V = "20261006"  # 캐시 무효화용 버전


def todo(text):
    """AMP 확인이 필요한 자리. 배포 전 `class="todo"`로 검색해 모두 해소한다."""
    return '<span class="todo">[%s]</span>' % text


def img(name, alt, ext="jpg", cls=""):
    c = ' class="%s"' % cls if cls else ""
    return '<img src="/default/img/%s.%s" alt="%s" loading="lazy"%s>' % (name, ext, alt, c)


NAV = [
    ("company", "회사소개", "/default/company/greeting.html", [
        ("인사말", "/default/company/greeting.html"),
        ("연혁", "/default/company/history.html"),
        ("조직도", "/default/company/organization.html"),
        ("인증 및 제증명", "/default/company/certification.html"),
        ("협력기관", "/default/company/partners.html"),
        ("오시는 길", "/default/company/location.html"),
    ]),
    ("air", "공조부품", "/default/air/products.html", [
        ("제품 소개", "/default/air/products.html"),
        ("생산·품질", "/default/air/quality.html"),
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
    ("cscenter", "고객센터", "/default/cscenter/contact.html", [
        ("견적·기술상담", "/default/cscenter/contact.html"),
        ("공지사항", "/default/cscenter/notice.html"),
        ("FAQ", "/default/cscenter/faq.html"),
    ]),
]

SECTION_LABEL = {k: label for k, label, _, _ in NAV}
PAGES = []  # (url, lastmod 용도 없음) – sitemap 생성용


def header(section):
    items = []
    for key, label, href, subs in NAV:
        cls = []
        if key == "water":
            cls.append("water")
        if key == section:
            cls.append("on")
        sub = "".join('<li><a href="%s">%s</a></li>' % (h, t) for t, h in subs)
        items.append('<li class="%s"><a href="%s">%s</a><ul class="sub">%s</ul></li>'
                     % (" ".join(cls), href, label, sub))
    return (
        '<a class="amp-skip" href="#main">본문 바로가기</a>'
        '<header class="amp-header"><div class="amp-wrap">'
        '<a class="amp-logo" href="/default/index.html"><img src="/default/img/logo.png" alt="AMP 에이엠피"></a>'
        '<button class="amp-burger" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>'
        '<nav class="amp-nav" aria-label="주요 메뉴"><ul>%s</ul></nav>'
        '</div></header>' % "".join(items)
    )


def footer():
    return (
        '<footer class="amp-footer"><div class="amp-wrap">'
        '<address><b>유한회사 에이엠피</b> · 대표이사 안명원<br>'
        '사업자등록번호 171-81-03763<br>'
        '본점 전남 광양시 광양읍 익신산단3길 40, 409호<br>'
        'TEL %s · E-mail %s</address>'
        '<ul><li><a href="/default/company/greeting.html">회사소개</a></li>'
        '<li><a href="/default/air/products.html">공조부품</a></li>'
        '<li><a href="/default/water/overview.html">수처리·물 매니지먼트</a></li>'
        '<li><a href="/default/portfolio/water.html">시공사례</a></li>'
        '<li><a href="/default/cscenter/contact.html">CS CENTER</a></li></ul>'
        '<div class="amp-copy">© AMP Co., Ltd. All rights reserved.</div>'
        '</div></footer>' % (todo("대표번호"), todo("대표 이메일"))
    )


def subhead(h1, crumbs, lead="", water=False):
    crumb = " &gt; ".join(['<a href="%s">%s</a>' % c if isinstance(c, tuple) else c for c in crumbs])
    p = "<p>%s</p>" % lead if lead else ""
    return ('<div class="amp-subhead%s"><div class="amp-wrap"><div class="amp-crumb"><a href="/default/index.html">HOME</a> &gt; %s</div>'
            '<h1>%s</h1>%s</div></div>' % (" water" if water else "", crumb, h1, p))


def localnav(section, current):
    for key, label, href, subs in NAV:
        if key == section:
            lis = "".join('<li><a href="%s"%s>%s</a></li>' % (h, ' class="on"' if h == current else "", t) for t, h in subs)
            return '<div class="amp-localnav"><ul>%s</ul></div>' % lis
    return ""


def write(path, title, desc, body, section="", extra_head="", og_type="website"):
    url = SITE + path
    PAGES.append(path)
    html = (
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>%(title)s</title>\n'
        '<meta name="description" content="%(desc)s">\n'
        '<link rel="canonical" href="%(url)s">\n'
        '<meta property="og:type" content="%(og_type)s">\n'
        '<meta property="og:site_name" content="에이엠피 AMP">\n'
        '<meta property="og:title" content="%(title)s">\n'
        '<meta property="og:description" content="%(desc)s">\n'
        '<meta property="og:url" content="%(url)s">\n'
        '<meta property="og:image" content="%(site)s/default/img/og-default.jpg">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<link rel="icon" href="/default/img/logo.png">\n'
        '<link rel="stylesheet" href="/default/css/amp-draft.css?v=%(v)s">\n%(extra)s'
        '</head>\n<body class="amp%(wsec)s">\n%(header)s\n<main id="main">\n%(body)s\n</main>\n%(footer)s\n'
        '<script src="/default/js/amp-draft.js?v=%(v)s" defer></script>\n</body>\n</html>\n'
    ) % dict(title=title, desc=desc, url=url, og_type=og_type, site=SITE, v=V, extra=extra_head,
             wsec=" water-sec" if section == "water" else "", header=header(section), body=body, footer=footer())
    out = ROOT / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def banner(h="설비·수처리 견적 문의", p="현장 상황을 알려 주시면 담당자가 확인 후 연락드립니다."):
    return ('<section class="amp-banner"><div class="amp-wrap"><div><h2>%s</h2><p>%s &nbsp; 대표번호 %s</p></div>'
            '<a class="amp-btn" href="/default/cscenter/contact.html">견적·기술상담 신청</a></div></section>'
            % (h, p, todo("대표번호")))


def cta(field, label, water=True):
    return ('<div class="amp-cta%s"><div><h3>이 분야 견적·기술상담 받기</h3><p>%s 관련 현장 조건을 알려 주시면 확인 후 연락드립니다.</p></div>'
            '<a class="amp-btn light" href="/default/cscenter/contact.html?field=%s">견적·기술상담 신청</a></div>'
            % ("" if water else " air", label, field))


# ───────────────────────── 메인 ─────────────────────────
def build_index():
    org = json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": "유한회사 에이엠피", "alternateName": "AMP", "url": SITE,
        "logo": SITE + "/default/img/logo.png",
        "address": {"@type": "PostalAddress", "addressRegion": "전남", "addressLocality": "광양시",
                    "streetAddress": "광양읍 익신산단3길 40, 409호", "addressCountry": "KR"},
    }, ensure_ascii=False)
    body = """
<section class="amp-hero"><div class="amp-wrap">
  <div>
    <!-- 슬로건 문구는 AMP 최종 승인 필요 -->
    <h1>현장에 맞춘 설비,<br>데이터로 관리하는 물</h1>
    <p>공조부품 제조에서 수처리·이차전지 공정 설비까지</p>
    <div class="btns">
      <a class="amp-btn light" href="/default/water/overview.html">수처리 설비 보기</a>
      <a class="amp-btn ghost" style="color:#fff !important;border-color:#fff" href="/default/cscenter/contact.html">견적·기술상담</a>
    </div>
  </div>
  <figure>%(hero)s</figure>
</div></section>

<section class="amp-sec"><div class="amp-wrap">
  <span class="amp-eyebrow">BUSINESS</span>
  <h2>에이엠피의 두 가지 사업</h2>
  <p class="lead">공조부품 제조로 쌓은 가공·품질관리 역량을 수처리·물 매니지먼트로 넓혔습니다.</p>
  <div class="amp-grid c2">
    <a class="amp-card axis air" href="/default/air/products.html">%(air)s<div class="body">
      <span class="tag air">공조부품</span><h3>Clad AL Header Pipe 제조·가공</h3>
      <p>자동차·가정용 에어컨 열교환기에 쓰이는 클래드 알루미늄 헤더 파이프를 주문 사양에 맞춰 생산합니다.</p></div></a>
    <a class="amp-card axis water" href="/default/water/overview.html">%(water)s<div class="body">
      <span class="tag">수처리·물 매니지먼트</span><h3>설계·제작·설치·시운전·모니터링</h3>
      <p>현장마다 다른 물에 맞춰 수처리 설비를 설계·제작하고, 수질 데이터를 실시간으로 관리합니다.</p></div></a>
  </div>
</div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <span class="amp-eyebrow water">APPLICATION</span>
  <h2>적용 분야</h2>
  <p class="lead">고객 문제에서 출발해 해결 방식과 실적까지 분야별로 정리했습니다.</p>
  <div class="amp-grid c4">
    <a class="amp-tile" href="/default/water/battery.html"><b>이차전지 폐수</b><span>망초폐수·고염폐수 처리, 전구체 공침 공정 장비</span></a>
    <a class="amp-tile" href="/default/water/recycle.html"><b>공정수 재순환</b><span>재이용 시스템, 입자선별·필터 장치</span></a>
    <a class="amp-tile" href="/default/water/aquaculture.html"><b>육상양식</b><span>RAS·BFT 수질 모니터링, 미생물 배양수조</span></a>
    <a class="amp-tile" href="/default/water/pharma.html"><b>제약·화학</b><span>원수 분석 기반 맞춤형 수처리 시스템</span></a>
  </div>
</div></section>

<section class="amp-sec"><div class="amp-wrap">
  <span class="amp-eyebrow">REFERENCES</span>
  <h2>실적 하이라이트</h2>
  <p class="lead">제작·설치한 설비와 수행한 과제의 일부입니다.</p>
  <div class="amp-grid c3">
    <a class="amp-card" href="/default/portfolio/water.html">%(r1)s<div class="body"><span class="tag">이차전지</span><h3>전구체 공침반응기</h3><p>실험실 규모(Lab 5L~50L급) 맞춤 제작, pH·투입량 제어.</p></div></a>
    <a class="amp-card" href="/default/portfolio/water.html">%(r2)s<div class="body"><span class="tag">이차전지</span><h3>폐수처리 Pilot 시스템</h3><p>고염 폐수 처리 공정을 현장 조건에 맞춰 시험하는 Pilot 설비.</p></div></a>
    <a class="amp-card" href="/default/portfolio/water.html">%(r3)s<div class="body"><span class="tag">육상양식</span><h3>양식장 수질관리</h3><p>수질 센서와 모니터링 프로그램으로 물 상태를 확인·관리.</p></div></a>
  </div>
  <p style="margin-top:24px"><a class="amp-btn ghost" href="/default/portfolio/water.html">시공사례 전체 보기</a></p>
</div></section>

<section class="amp-sec soft"><div class="amp-wrap">
  <span class="amp-eyebrow">TRUST</span>
  <h2>신뢰 지표</h2>
  <ul class="amp-trust">
    <li>ISO 9001</li><li>벤처기업 확인</li><li>뿌리기업 확인</li><li>연구전담부서</li><li>전라남도지사 표창</li>
  </ul>
  <p style="margin-top:14px"><a href="/default/company/certification.html" style="text-decoration:underline">인증 및 제증명 보기</a></p>
</div></section>
%(banner)s
""" % dict(
        hero=img("monitoring-field", "수질 센서와 실시간 모니터링 프로그램을 점검하는 현장"),
        air=img("product-header-pipe", "Clad Aluminum Header Pipe 제품"),
        water=img("pilot-01", "이차전지 폐수처리 Pilot 시스템"),
        r1=img("reactor-lab-01", "전구체 공침반응기"),
        r2=img("pilot-02", "이차전지 폐수처리 Pilot 시스템 측면"),
        r3=img("aqua-01", "육상양식 수조 현장"),
        banner=banner(),
    )
    write("/default/index.html",
          "에이엠피 AMP – 수처리 시스템 설비·Clad AL Header Pipe 제조",
          "에이엠피는 Clad AL Header Pipe 등 공조부품 제조와 이차전지 폐수처리·공정수 재순환·육상양식·제약화학 수처리 설비를 설계·제작·설치합니다.",
          body, extra_head='<script type="application/ld+json">%s</script>\n' % org)


# ───────────────────────── 회사소개 ─────────────────────────
def company_page(path, current, title, desc, h1, body_inner, lead=""):
    body = (subhead(h1, ["회사소개", h1], lead) + localnav("company", path) +
            '<section class="amp-sec"><div class="amp-wrap">%s</div></section>' % body_inner)
    write(path, title, desc, body, "company")


def build_company():
    values = "".join('<div class="amp-tile"><b>%s</b><span>%s</span></div>' % v for v in [
        ("도전 정신 Challenge", "새로운 분야에 도전합니다."),
        ("윤리 경영 Ethics", "투명하고 책임 있게 경영합니다."),
        ("창조성 Creativity", "창조적 혁신으로 가치를 만듭니다."),
        ("전문성 Professionalism", "현장 경험과 기술로 전문성을 쌓습니다."),
    ])
    company_page("/default/company/greeting.html", "", "인사말 | 에이엠피",
        "공조부품 제조로 쌓은 가공·품질관리 역량을 바탕으로 수처리·물 매니지먼트로 사업을 넓힌 에이엠피의 인사말.",
        "인사말", """
<!-- 인사말은 컬리버 초안. AMP 최종 승인 필요 -->
<div class="amp-prose" style="max-width:820px">
  <h2>홈페이지를 방문해 주신 여러분께 감사드립니다.</h2>
  <p>에이엠피는 대형·소형·원형·사각 알루미늄 파이프를 가공해 공조기 제품 제작에 쓰이는 Clad Aluminum Header Pipe를 공급해 왔습니다.
  고객의 요구에 맞춰 주문 생산하고, 공정별 작업표준서와 품질관리로 안정적인 품질을 유지해 온 것이 저희의 기반입니다.</p>
  <p>이 가공·품질관리 역량을 바탕으로 이제 <b>수처리·물 매니지먼트</b> 분야로 사업을 넓혔습니다.
  이차전지 공정 폐수, 공정수 재순환, 육상양식, 제약·화학 폐수까지 현장마다 물의 성상이 다르다는 점에서 출발해,
  현장·수질 진단부터 공정 설계, 설비 제작·설치, 시운전, 모니터링까지 한 흐름으로 수행합니다.</p>
  <p>현장에 맞춘 설계·제작과 사후관리로 신뢰받는 파트너가 되겠습니다.
  필요하신 제품과 설비는 전화 또는 <a href="/default/cscenter/contact.html" style="text-decoration:underline">견적·기술상담</a>으로 문의해 주십시오.</p>
  <p style="margin-top:28px"><b>대표이사 안명원</b></p>
</div>
<h3 style="margin-top:56px">윤리·책임경영</h3>
<p class="amp-prose">창조적 혁신을 통해 사회적 가치를 실현하는 책임 있는 경영을 추구합니다.</p>
<div class="amp-grid c4">%s</div>""" % values)

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
    company_page("/default/company/history.html", "", "연혁 | 에이엠피",
        "에이엠피의 주요 연혁 – 뿌리기업·벤처기업 확인, 전라남도지사 표창, 여수 지점 등록 등.", "연혁",
        '<ol class="amp-timeline" style="max-width:760px">%s</ol>' %
        "".join("<li><time>%s</time>%s</li>" % t for t in tl))

    company_page("/default/company/organization.html", "", "조직도 | 에이엠피",
        "에이엠피 조직도 – 대표이사, 생산팀, 품질·설계, 연구전담부서.", "조직도",
        """<p class="amp-prose">%s</p>
<div class="amp-org"><div class="top">대표이사</div><div class="bar"></div>
<div class="row"><div>생산팀</div><div>품질·설계</div><div>연구전담부서</div></div></div>""" %
        todo("실제 조직 구성 AMP 확인 후 수정"))

    cert = lambda n, cap, sub: ('<figure class="amp-cert amp-figure">%s<figcaption>%s<small>%s</small></figcaption></figure>' %
                                (img(n, cap), cap, sub))
    company_page("/default/company/certification.html", "", "인증 및 제증명 | 에이엠피",
        "에이엠피의 벤처기업확인서, 뿌리기업확인서, ISO 9001, 전라남도지사 표창, 중소벤처기업청장 상장.", "인증 및 제증명",
        """<div class="amp-grid c4">%s%s%s%s</div>
<div class="amp-box" style="margin-top:28px"><h3>ISO 9001:2015</h3><p>품질경영시스템 인증을 보유하고 있습니다. %s</p></div>""" % (
            cert("cert-venture", "벤처기업확인서", "혁신성장유형 · 2026.03.17 ~ 2029.03.16"),
            cert("cert-root", "뿌리기업확인서", "2025.10.21 ~ 2028.10.20"),
            cert("award-jeonnam", "전라남도지사 표창장", "2025.11.19"),
            cert("award-smba", "중소벤처기업청장 상장", "2024.11.14"),
            todo("ISO 9001 인증서 이미지 수령 후 추가")))

    partners = [("전남테크노파크", "지역 기업 지원기관"), ("전남대학교", "산학 협력(MOU)"),
                ("순천대학교", "산학 협력(MOU)"), ("광양시", "이차전지 산업 협약")]
    company_page("/default/company/partners.html", "", "협력기관 | 에이엠피",
        "에이엠피의 협력기관 – 전남테크노파크, 전남대학교, 순천대학교, 광양시 등.", "협력기관",
        '<div class="amp-grid c4">%s</div><p class="amp-prose" style="margin-top:24px">%s</p>' % (
            "".join('<div class="amp-tile"><b>%s</b><span>%s</span></div>' % p for p in partners),
            todo("기존 협력기관 4곳(현 홈페이지 '파트너') 추가")))

    company_page("/default/company/location.html", "", "오시는 길 | 에이엠피",
        "에이엠피 본점(광양 익신산단), 공장(광양 태인동 국가산단), 지점·연구(여수 주삼동) 위치 안내.", "오시는 길",
        """<table class="amp-table">
<tr><th>본점</th><td>전남 광양시 광양읍 익신산단3길 40, 409호 (광양만권 소재부품 지식산업센터)<br>
<a href="%s" target="_blank" rel="noopener" style="text-decoration:underline">지도 보기</a></td></tr>
<tr><th>공장</th><td>전남 광양시 태인동 국가산업단지 %s</td></tr>
<tr><th>지점·연구</th><td>전남 여수시 주삼동 (여수 융합지구) %s</td></tr>
<tr><th>전화</th><td>%s</td></tr>
</table>""" % (MAP_URL, todo("공장 상세 주소"), todo("여수 지점 호수 106호 vs 202-01 확인"), todo("대표번호")))


# ───────────────────────── 공조부품 ─────────────────────────
def build_air():
    def air_page(path, h1, title, desc, inner):
        body = (subhead(h1, ["공조부품", h1], "Clad Aluminum Header Pipe") + localnav("air", path) +
                '<section class="amp-sec"><div class="amp-wrap">%s</div></section>' % inner)
        write(path, title, desc, body, "air")

    gallery = "".join('<figure>%s</figure>' % img(n, a) for n, a in [
        ("product-header-pipe", "Clad Aluminum Header Pipe"),
        ("product-pipe-assembly", "Clad Aluminum Pipe 및 Assembly"),
        ("product-heat-exchanger", "알루미늄 열교환기"),
        ("product-atf-warmer", "ATF Warmer"),
        ("product-ev-cooler", "전기차 배터리 Cooler"),
        ("product-tube-stack", "알루미늄 튜브 적층 가공품")])
    air_page("/default/air/products.html", "제품 소개",
        "Clad Aluminum Header Pipe 제조 | 에이엠피",
        "Clad AL Header Pipe, Clad AL Pipe & Assembly, ATF Warmer, 전기차 배터리 Cooler, D-type 실내기(증발기) 등 공조부품을 제조합니다.",
        """
<div class="amp-split">
  <div class="amp-prose">
    <h2>Clad Aluminum Header Pipe란?</h2>
    <p>공조시스템에 적용되는 브레이징 제품에 사용되는 부품입니다. 주로 자동차 열교환기(콘덴서, 에바, 히터, 라디에이터 등)와
    가정용 에어컨 열교환기(콘덴서, 에바)에 적용됩니다.</p>
    <p>용융점이 다른 알루미늄 합금(3000계, 4000계 등)을 클래딩한 판재를 <b>고주파 유도용접</b>으로 조관해 제작합니다.</p>
    <table class="amp-table"><tr><th>심재(Core)</th><td>알루미늄 합금(3000계 등), 용융점 630~660℃</td></tr>
    <tr><th>클래드층</th><td>Al-Si 합금(4000계 등), 용융점 577~610℃</td></tr>
    <tr><th>제작 방식</th><td>클래드 판재 → 고주파 유도용접 조관</td></tr></table>
  </div>
  <figure class="amp-figure">%s<figcaption>용융점이 서로 다른 알루미늄 클래드 판재</figcaption></figure>
</div>
<h2 style="margin-top:56px">주력 제품</h2>
<ul class="amp-prose"><li>Clad Aluminum Header Pipe</li><li>Clad AL Pipe &amp; Assembly</li><li>ATF Warmer</li>
<li>전기차 배터리 Cooler</li><li>D-type 실내기(증발기)</li></ul>
<div class="amp-gallery" style="margin-top:20px">%s</div>
<p class="amp-prose" style="margin-top:14px">%s</p>
%s""" % (img("air-diagram-clad", "알루미늄 클래딩 라인과 클래드 판재 단면 도식"), gallery,
         todo("제품 사진 원본 수령 후 교체 (현재 현 홈페이지 캡처 크롭)"),
         cta("air", "공조부품(Clad AL Header Pipe)", water=False)))

    qs = "".join('<figure class="amp-figure">%s<figcaption>%s</figcaption></figure>' % (img(n, a), a) for n, a in [
        ("qs-cutting", "작업표준서 – 절단 공정"), ("qs-deburring", "작업표준서 – 디버링 공정"), ("qs-washing", "작업표준서 – 세척 공정")])
    flow = "".join("<li>%s</li>" % s for s in ["원소재 조관", "사이징/인발", "절단", "디버링", "표면처리(세척)", "검사", "포장·출고"])
    air_page("/default/air/quality.html", "생산·품질",
        "공조부품 생산공정·품질관리 | 에이엠피",
        "Clad AL Header Pipe 생산공정(조관·사이징·절단·디버링·세척·검사)과 공정별 작업표준서, ISO 9001:2015 품질관리를 소개합니다.",
        """
<h2>생산공정</h2>
<ol class="amp-steps">%s</ol>
<h2 style="margin-top:48px">품질관리</h2>
<div class="amp-prose" style="max-width:820px">
<p>절단·디버링·세척 등 공정별로 <b>작업표준서</b>를 운영합니다. 작업 순서와 방법, 작업 조건 관리 항목, 자주 검사 항목,
품질 문제·비상 상황 발생 시 조치 사항을 공정마다 명시하고, 개정 이력을 관리합니다.</p>
<ul><li>절단: 수입검사, 초물 검사, 길이·진직도·수직도 자주검사</li>
<li>디버링: 브러쉬 간격 설정, 버(Burr)·모서리 및 절단면 상태 확인</li>
<li>세척: 세척액 온도·상태 관리, 건조 및 내경 검사</li>
<li>품질경영시스템 ISO 9001:2015</li></ul></div>
<div class="amp-gallery" style="margin-top:28px">%s</div>
<p class="amp-prose" style="margin-top:12px">%s</p>
%s""" % (flow, qs,
         todo("작업표준서에 고객사명·품번·담당자 실명이 보임 – 게시 범위 AMP 최종 확인(필요 시 해당 부분 가림 처리)"),
         cta("air", "공조부품", water=False)))


# ───────────────────────── 수처리 ─────────────────────────
def water_page(path, h1, title, desc, lead, inner):
    body = (subhead(h1, ["수처리·물 매니지먼트", h1], lead, water=True) + localnav("water", path) + inner)
    write(path, title, desc, body, "water")


def field_page(path, field, label, h1, title, desc, lead, problem, solution, results, extra_after=""):
    flow = '<ol class="amp-flow"><li>고객 문제</li><li>해결 방식</li><li>실적·성과</li><li>문의</li></ol>'
    inner = """
<section class="amp-sec"><div class="amp-wrap">%(flow)s
  <h2 style="margin-top:36px">고객 문제</h2><div class="amp-box hl amp-prose">%(problem)s</div>
  <h2 style="margin-top:48px">해결 방식</h2>%(solution)s
  <h2 style="margin-top:48px">실적·성과</h2>%(results)s%(extra)s
  %(cta)s
</div></section>""" % dict(flow=flow, problem=problem, solution=solution, results=results, extra=extra_after, cta=cta(field, label))
    water_page(path, h1, title, desc, lead, inner)


def steps(items):
    return '<ol class="amp-steps">%s</ol>' % "".join("<li>%s</li>" % i for i in items)


def gallery(items, cls=""):
    return '<div class="amp-gallery %s">%s</div>' % (cls, "".join(
        '<figure>%s<figcaption>%s</figcaption></figure>' % (img(n, a), a) for n, a in items))


def build_water():
    proc = [("01", "현장·수질 진단"), ("02", "처리목표 설정"), ("03", "공정설계"), ("04", "Pilot/시제품 제작"),
            ("05", "설비 제작·설치"), ("06", "시운전"), ("07", "모니터링·유지관리")]
    proc_html = '<ol class="amp-process">%s</ol>' % "".join("<li><b>STEP %s</b>%s</li>" % p for p in proc)
    inner = """
<section class="amp-sec"><div class="amp-wrap">
  <span class="amp-eyebrow water">OVERVIEW</span>
  <h2>현장마다 다른 물, 현장에 맞춘 수처리 설비를 설계·제작·설치합니다</h2>
  <p class="lead">원수 성상이 현장마다 달라 표준 설비만으로는 처리 목표를 맞추기 어렵습니다. 에이엠피는 진단에서 유지관리까지 한 흐름으로 수행합니다.</p>
  <h3>수행 프로세스</h3>%(proc)s
  <h3>에이엠피의 강점</h3>
  <div class="amp-grid c3">
    <div class="amp-tile"><b>화학공학·품질관리 기반 공정조건 설정</b><span>원수 특성과 처리 목표에 맞춰 공정 조건을 정합니다.</span></div>
    <div class="amp-tile"><b>자체 공장에서 구조물·장치 직접 제작</b><span>용접·절단·가공 설비를 갖춰 설계 변경에 빠르게 대응합니다.</span></div>
    <div class="amp-tile"><b>수질 센서 기반 실시간 모니터링</b><span>pH, EC, 온도, 탁도, TDS, DO를 측정하고 데이터를 관리합니다.</span></div>
  </div>
  <div class="amp-split" style="margin-top:36px">
    <figure class="amp-figure">%(m1)s<figcaption>수질 실시간 모니터링 프로그램과 센서</figcaption></figure>
    <figure class="amp-figure">%(m2)s<figcaption>실시간 모니터링 프로그램 화면</figcaption></figure>
  </div>
</div></section>
<section class="amp-sec soft"><div class="amp-wrap">
  <h2>적용 분야</h2>
  <div class="amp-grid c4">
    <a class="amp-tile" href="/default/water/battery.html"><b>이차전지 폐수처리</b><span>망초폐수·고염폐수, 공침 공정 장비</span></a>
    <a class="amp-tile" href="/default/water/recycle.html"><b>공정수 재순환</b><span>재이용 시스템, 입자선별·필터</span></a>
    <a class="amp-tile" href="/default/water/aquaculture.html"><b>육상양식 물관리</b><span>RAS·BFT, 수질 모니터링</span></a>
    <a class="amp-tile" href="/default/water/pharma.html"><b>제약·화학 폐수처리</b><span>맞춤형 수처리 시스템</span></a>
  </div>
  %(cta)s
</div></section>""" % dict(proc=proc_html, m1=img("monitoring-field", "수질 센서와 모니터링 프로그램 현장"),
                           m2=img("monitor-screen", "실시간 모니터링 프로그램(AMP) 화면"), cta=cta("etc", "수처리 시스템 설비"))
    water_page("/default/water/overview.html", "수처리 시스템 설비",
        "수처리 시스템 설비 설계·제작·설치 | 에이엠피",
        "광양 소재 에이엠피는 현장·수질 진단, 공정설계, 설비 제작·설치, 시운전, 모니터링까지 수처리 시스템 설비를 한 흐름으로 수행합니다.",
        "현장마다 다른 물, 현장에 맞춘 수처리 설비를 설계·제작·설치합니다", inner)

    field_page("/default/water/battery.html", "battery", "이차전지 폐수처리", "이차전지 폐수처리",
        "이차전지 폐수처리·망초폐수 재이용 | 에이엠피",
        "이차전지 전구체·양극재 공정의 망초폐수·고염폐수 처리, 전구체 공침반응기(Lab 5L~50L급) 제작, 무방류(ZLD) 지향 공정 설계.",
        "고염·고농도 폐수 처리와 공정수 재이용, 전구체 공침 공정 장비",
        "<p>전구체·양극재 공정에서는 고염·고농도 폐수(망초폐수, Na₂SO₄)가 발생합니다.</p><p>폐수 처리비가 늘어나고, 공정수를 확보하는 부담도 함께 커집니다.</p>",
        steps(["전처리(Micro Filter)", "농축탱크", "EDR(전기투석역전)", "처리수 재이용"]) + """
<div class="amp-prose"><ul><li>중앙 모니터링으로 공정 상태를 확인합니다.</li>
<li>무방류(ZLD)를 지향하는 공정으로 설계합니다. 실제 공정 구성은 현장 수질에 따라 달라집니다.</li>
<li><b>연계 장비</b>: 전구체 공침반응기(Lab 5L ~ 50L급), pH·투입량 이상 감지 및 제어 프로그램</li></ul></div>
<div class="amp-split" style="margin-top:20px">
  <figure class="amp-figure">%s<figcaption>50L 공침 반응기 구성 개념도</figcaption></figure>
  <figure class="amp-figure">%s<figcaption>무방류(ZLD) 공정 개념도 – 현장 수질에 따라 공정 구성이 달라집니다</figcaption></figure>
</div>""" % (img("reactor-diagram-50l", "50L 공침 반응기 구성 개념도"), img("zld-diagram", "무방류 ZLD 공정 개념도")),
        "<p class=\"amp-prose\">이차전지 폐수처리 Pilot, 실험실 맞춤형 공침반응기, 전구체 입자선별·필터 장치를 제작했습니다.</p>" +
        gallery([("pilot-01", "폐수처리 Pilot 시스템"), ("pilot-02", "폐수처리 Pilot 시스템(측면)"),
                 ("reactor-lab-01", "전구체 공침반응기"), ("reactor-lab-02", "공침반응기 제어부"),
                 ("module-b1", "전구체 입자선별 및 필터 장치"), ("module-b2", "입자선별 필터 장치(S社 양극재)")]) +
        '<h3>공침반응기 제작 과정</h3>' +
        gallery([("reactor-01", "판재 절단·가공"), ("reactor-02", "스테인리스 용접"), ("reactor-03", "조립·치수 확인"),
                 ("reactor-04", "교반부(임펠러)"), ("reactor-05", "상부 포트·클램프 조립"), ("reactor-site-01", "설치·점검")], "c3") +
        '<p class="amp-prose" style="margin-top:12px">%s</p>' % todo("고객사명은 익명(S社) 표기 유지 – 공개 범위 AMP 확인"))

    field_page("/default/water/recycle.html", "recycle", "공정수 재순환", "공정수 재순환",
        "공정수 재순환 시스템 | 에이엠피",
        "공정수 사용량과 폐수 배출을 줄이는 현장 맞춤형 공정수 재순환·재이용 시스템과 입자선별·필터 장치, 수질 모니터링 연동.",
        "공정수 사용량·폐수 배출량을 줄이는 현장 맞춤형 재이용 시스템",
        "<p>공정수 사용량과 폐수 배출량이 늘면서 원가와 ESG 부담이 커지고 있습니다.</p>",
        steps(["현장·수질 진단", "재순환 모듈 설계", "입자선별·필터 적용", "수질 모니터링 연동"]) +
        '<div class="amp-prose"><ul><li>현장 맞춤형 재순환 모듈</li><li>입자선별·필터 장치</li><li>수질 모니터링 연동</li></ul></div>',
        "<p class=\"amp-prose\">공정수 재순환 현장 맞춤형 시스템을 제작했습니다. %s</p>" % todo("모듈 사진 매핑 확인(콜라주 하단 좌측 2컷 가정)") +
        gallery([("module-a1", "공정수 재순환 현장 맞춤형 시스템"), ("module-a2", "재순환 모듈 설치 구성")], "c2"))

    field_page("/default/water/aquaculture.html", "aqua", "육상양식 물관리", "육상양식 물관리",
        "육상양식 수처리·수질 모니터링 | 에이엠피",
        "RAS·바이오플락(BFT) 육상양식장의 수질 센서·컨트롤러, 순환여과 수처리, 미생물 자동 배양수조, 원격 모니터링을 제공합니다.",
        "RAS·BFT 양식장의 수질을 데이터로 관리합니다",
        "<p>RAS·바이오플락(BFT) 양식장은 수질 관리가 경험에 의존하는 경우가 많습니다.</p><p>수온·pH·DO가 급변하면 대량 폐사로 이어질 위험이 있습니다.</p>",
        '<div class="amp-prose"><ul><li>순환여과 수처리 설비</li><li>수질 센서·컨트롤러 (pH, EC, 온도, 탁도, TDS, DO)</li>'
        '<li>미생물 자동 배양수조 – DO·pH·염도·온도 자동 보정</li><li>원격 대시보드·알림</li></ul></div>' +
        '<p class="amp-prose">%s</p>' % ("연계 과제: 미생물 자동 배양수조 개발 (블루스타트업) " + todo("과제 완료 후 사진 추가, 대외 표기 가능 여부 확인")),
        '<div class="amp-prose"><ul><li>양식어가 수질 센서 및 물관리 시스템 검증 (2025)</li><li>무안 소재 양식장 유지보수</li></ul></div>' +
        gallery([("aqua-01", "육상양식 수조 현장"), ("aqua-02", "원형 수조"), ("aqua-05", "양식장 수조 전경"),
                 ("aqua-06", "수조 수질 상태"), ("aqua-07", "수조 점검"), ("aqua-04", "수조 표면 상태")]) +
        '<p class="amp-prose" style="margin-top:12px">%s</p>' % todo("고객은 C社(양식어가) 익명 – 양식장 위치 노출 가능 여부 확인"))

    field_page("/default/water/pharma.html", "pharma", "제약·화학 폐수처리", "제약·화학 폐수처리",
        "제약·화학 폐수처리 시스템 | 에이엠피",
        "원수 성상이 현장마다 다른 제약·화학 폐수를 원수 분석 기반으로 공정을 구성하고 소규모·Pilot 규모로 맞춤 제작합니다.",
        "원수 분석에서 출발하는 맞춤형 수처리 시스템",
        "<p>제약·화학 공정은 원수 성상이 현장마다 달라, 표준 설비만으로는 처리 목표를 달성하기 어렵습니다.</p>",
        steps(["원수 분석", "공정 구성", "소규모·Pilot 맞춤 제작", "설치·시운전"]) +
        '<div class="amp-prose"><ul><li>원수 분석 결과를 기준으로 공정을 구성합니다.</li><li>소규모·Pilot 규모부터 맞춤 제작합니다.</li></ul></div>',
        '<p class="amp-prose">제약공정 수처리 시스템을 제작·설치했습니다.</p><p class="amp-prose">%s</p>' %
        todo("제약공정 수처리 시스템 사진 수령 후 추가 (현재 이 분야 사진 없음)"))


# ───────────────────────── 시공사례 ─────────────────────────
def build_portfolio():
    def card(n, alt, cat, tag, title, text, meta, tagcls=""):
        im = img(n, alt) if n else '<div class="noimg">사진 준비 중</div>'
        return ('<div class="amp-card" data-cat="%s">%s<div class="body"><span class="tag %s">%s</span><h3>%s</h3><p>%s</p><div class="meta">%s</div></div></div>'
                % (cat, im, tagcls, tag, title, text, meta))

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
    flt = ('<div class="amp-filter">%s</div>' % "".join('<button data-filter="%s"%s>%s</button>' % (k, ' class="on"' if k == "all" else "", v) for k, v in
           [("all", "전체"), ("battery", "이차전지"), ("recycle", "공정수"), ("aqua", "육상양식"), ("pharma", "제약·화학"), ("common", "공통")]))
    body = (subhead("수처리·공정장비 실적", ["시공사례·납품실적", "수처리·공정장비 실적"], "분야별로 제작·설치한 설비와 납품 실적입니다.") +
            localnav("portfolio", "/default/portfolio/water.html") +
            '<section class="amp-sec"><div class="amp-wrap">%s<div class="amp-grid c3">%s</div>%s</div></section>' % (
                flt, "".join(water), banner()))
    write("/default/portfolio/water.html", "시공사례·납품실적 | 에이엠피",
          "에이엠피의 수처리·공정장비 시공사례와 납품실적 – 공침반응기, 폐수처리 Pilot, 공정수 재순환, 수질 모니터링, 육상양식.", body, "portfolio")

    air = [card("product-header-pipe", "Clad AL Header Pipe", "air", "공조부품", "Clad AL Header Pipe 가공", "알루미늄 클래드 파이프 가공품.", "", "air"),
           card("product-pipe-assembly", "Clad AL Pipe 및 Assembly", "air", "공조부품", "Clad AL Pipe 및 Assembly", "파이프 및 조립품.", "", "air"),
           card("product-heat-exchanger", "열교환기", "air", "공조부품", "열교환기용 부품", "자동차·가정용 에어컨 열교환기 적용.", "", "air")]
    body = (subhead("공조부품 실적", ["시공사례·납품실적", "공조부품 실적"], "Clad AL Header Pipe 등 공조부품 가공·납품 실적입니다.") +
            localnav("portfolio", "/default/portfolio/air.html") +
            '<section class="amp-sec"><div class="amp-wrap"><div class="amp-grid c3">%s</div><p class="amp-prose" style="margin-top:14px">%s</p>%s</div></section>' % (
                "".join(air), todo("기존 갤러리 3건 이관 – 현 사이트 gallery01.php 원본 이미지·설명으로 교체"), cta("air", "공조부품", water=False)))
    write("/default/portfolio/air.html", "공조부품 납품실적 | 에이엠피",
          "에이엠피의 Clad AL Header Pipe 등 공조부품 가공·납품실적.", body, "portfolio")


# ───────────────────────── 고객센터 ─────────────────────────
FAQ = [
    ("견적은 어떻게 진행되나요?",
     "문의 접수 후 현장·수질을 확인하고 개략 견적을 드립니다. 이후 상세 설계를 거쳐 상세 견적을 안내합니다."),
    ("현장 방문 상담이 가능한가요?",
     "가능합니다. 수처리 설비는 현장·수질 진단이 첫 단계이므로, 상담 시 방문 일정을 협의합니다."),
    ("소량·Pilot 규모도 제작하나요?",
     "네. Pilot/시제품 제작 단계를 수행 프로세스에 두고 있으며, 실험실 규모(5L급)부터 맞춤 제작한 실적이 있습니다."),
    ("제작 기간은 얼마나 걸리나요?",
     "설비 규모와 사양에 따라 달라집니다. 요구 사양을 알려 주시면 상담 시 예상 일정을 안내합니다."),
    ("설치 후 유지보수·소모품 공급이 되나요?",
     "설치·시운전 이후 모니터링과 유지관리까지 수행합니다. 소모품은 설비별로 상담해 안내합니다."),
    ("원격 모니터링을 지원하나요?",
     "수질 센서(pH, EC, 온도, 탁도, TDS, DO) 기반의 실시간 모니터링 프로그램과 원격 대시보드·알림을 지원합니다."),
    ("Clad AL Header Pipe 주문 사양은 어떻게 전달하나요?",
     "견적·기술상담에서 문의 분야를 '공조부품'으로 선택하고 사양(규격, 수량, 도면 등)을 남겨 주시면 확인 후 연락드립니다."),
    ("정부지원사업과 연계한 도입 상담이 가능한가요?",
     "스마트제조 전환지원 등 지원사업을 수행한 경험이 있어 상담이 가능합니다. 지원사업명과 일정을 함께 알려 주세요."),
]


def build_cscenter():
    def cs(path, h1, title, desc, inner, extra_head=""):
        body = (subhead(h1, ["고객센터", h1]) + localnav("cscenter", path) +
                '<section class="amp-sec"><div class="amp-wrap">%s</div></section>' % inner)
        write(path, title, desc, body, "cscenter", extra_head)

    opts = [("air", "공조부품"), ("battery", "이차전지 폐수"), ("recycle", "공정수 재순환"),
            ("aqua", "육상양식"), ("pharma", "제약·화학"), ("etc", "기타")]
    options = "".join('<option value="%s">%s</option>' % o for o in opts)
    cs("/default/cscenter/contact.html", "견적·기술상담", "견적·기술상담 | 에이엠피",
       "에이엠피에 공조부품 주문, 수처리 설비 견적과 기술상담을 문의하세요. 분야를 선택해 현장 조건을 남기면 확인 후 연락드립니다.",
       """
<div class="amp-split">
<div>
<p id="sentMsg" class="amp-box hl" style="display:none"><b>문의가 접수되었습니다.</b> 확인 후 연락드리겠습니다.</p>
<form class="amp-form" method="post" action="/default/cscenter/contact_ok.php">
  <div class="amp-hp" aria-hidden="true"><label>비워 두세요 <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
  <div><label for="field">문의 분야 <span class="req">*</span></label>
    <select id="field" name="field" required>%s</select></div>
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
    <tr><th>보유 기간</th><td>문의 처리 완료 후 1년 보관 후 파기 %s</td></tr></table>
    <p style="margin:8px 0 0">동의를 거부할 수 있으며, 거부 시 상담 접수가 제한됩니다.</p></div>
  <label class="amp-check"><input type="checkbox" id="agree" name="agree" value="1" required> 개인정보 수집·이용에 동의합니다. <span class="req">(필수)</span></label>
  <div><button class="amp-btn" type="submit">문의 접수</button></div>
</form></div>
<aside class="amp-box"><h3>직접 문의</h3>
<table class="amp-table"><tr><th>전화</th><td>%s</td></tr><tr><th>이메일</th><td>%s</td></tr>
<tr><th>본점</th><td>전남 광양시 광양읍 익신산단3길 40, 409호</td></tr></table>
<p style="font-size:14px;color:var(--ink-soft);margin-top:14px">견적 진행: 문의 → 현장·수질 확인 → 개략 견적 → 상세 설계 견적</p></aside>
</div>""" % (options, todo("보유기간 AMP 확인"), todo("대표번호"), todo("대표 이메일")))

    cs("/default/cscenter/notice.html", "공지사항", "공지사항 | 에이엠피", "에이엠피 공지사항.",
       '<div class="amp-empty"><p>등록된 공지사항이 없습니다.</p><p>%s</p></div>' % todo("기존 게시판(DB 연동) 페이지와 연결하거나, 공지가 생기면 이 화면에 목록 추가"))

    faq_html = "".join('<details><summary>%s</summary><div class="a"><p>%s</p></div></details>' % qa for qa in FAQ)
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False)
    cs("/default/cscenter/faq.html", "FAQ", "자주 묻는 질문 | 에이엠피",
       "에이엠피 견적 절차, 현장 방문, Pilot 제작, 유지보수, 원격 모니터링, Clad AL Header Pipe 주문 방법 등 자주 묻는 질문.",
       '<div class="amp-faq" style="max-width:860px">%s</div><p style="margin-top:28px"><a class="amp-btn" href="/default/cscenter/contact.html">견적·기술상담 신청</a></p>' % faq_html,
       '<script type="application/ld+json">%s</script>\n' % ld)


def build_seo_files():
    urls = sorted(set(PAGES))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("  <url><loc>%s%s</loc></url>" % (SITE, u))
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /default/cscenter/contact_ok.php\n\nSitemap: %s/sitemap.xml\n" % SITE, encoding="utf-8")


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
