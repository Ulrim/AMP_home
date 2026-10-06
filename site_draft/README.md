# site_draft – 에이엠피 홈페이지 리뉴얼 페이지 초안

`01_사이트맵_콘텐츠기획안.md` 기준으로 만든 정적 HTML 초안 19페이지. 소스(FTP)를 받기 전에 만든 **독립 초안**이라 기존 사이트의 헤더·푸터·CSS를 쓰지 않고, 자체 CSS(`amp-draft.css`)로 동작한다.

## 미리보기

```bash
python3 -m http.server 8000 -d site_draft
# http://localhost:8000/default/index.html
```

## 구성

```
site_draft/
├─ robots.txt, sitemap.xml        루트에 배포
├─ redirects.htaccess.txt         기존 URL 301 규칙(초안)
└─ default/
   ├─ index.html
   ├─ company/    greeting history organization certification partners location
   ├─ air/        products quality                         (공조부품)
   ├─ water/      overview battery recycle aquaculture pharma  (수처리·물 매니지먼트)
   ├─ portfolio/  water air                                (시공사례·납품실적)
   ├─ cscenter/   contact notice faq, contact_ok.php       (고객센터)
   ├─ css/amp-draft.css, js/amp-draft.js
   └─ img/        PDF 자료에서 추출·크롭한 이미지 (JPEG 최대 1600px)
```

`tools/build_draft.py`가 공통 헤더·푸터·메타를 한 번에 만든다. 문구를 고친 뒤 `python3 tools/build_draft.py`로 다시 생성하면 된다(HTML만 직접 고쳐도 배포는 가능하지만 다음 생성 때 덮어쓴다).

## 배포 전 필수 작업

1. **노란색 `[…]` 표식을 모두 해소**한다. 찾기: `grep -rn 'class="todo"' site_draft --include=*.html` (현재 약 40곳, 푸터의 대표번호·이메일 포함). 해소하면 `build_draft.py`의 `todo()` 호출을 실제 값으로 바꾼다.
2. `cscenter/contact_ok.php`의 `$TO`(수신 메일)를 설정하고, 서버에서 `mb_send_mail`이 되는지 확인한다. 안 되면 기존 사이트의 문의 처리 방식으로 교체.
3. **인코딩**: 이 초안은 UTF-8이고 `<meta charset="utf-8">`을 넣었다. 기존 사이트는 EUC-KR이므로, (a) 서버가 charset 헤더를 강제하지 않는지 확인하거나 (b) 파일을 EUC-KR로 변환(`iconv -f UTF-8 -t CP949`)하고 meta를 바꾼다. `contact_ok.php`는 UTF-8 기준이다.
4. 서버 기존 파일을 **백업**한 뒤 업로드한다. 기존 `company/*.php`, `cscenter/*.php` 이름과 겹치는 파일은 `redirects.htaccess.txt`로 정리한다.
5. 공지사항(`notice.html`)은 빈 화면이다. 기존 게시판(DB)을 그대로 쓸 거면 그쪽으로 연결한다.
6. 배포 후: 네이버 서치어드바이저·구글 서치콘솔 등록, `sitemap.xml` 제출.

## 이미지 사용 현황

공급기업이 전 이미지 사용 가능을 확인했다고 하여 PDF의 이미지를 사용했다. 다만 아래는 **일부러 쓰지 않았다**(기획안에서도 쓰지 않는 용도).
- 언론기사 캡처 3장, 리서치 차트 2장(제3자 저작물 – 공급기업 확인으로 권리가 해소되지 않을 수 있음)
- 서명 이미지, 현 홈페이지 화면 캡처 원본
- AI 생성으로 보이는 이미지 2장(PDF 15·27쪽) – 실제 설비·현장이 아니라 실적처럼 보일 수 있음
- 인물이 크게 나온 시연 사진 2장(PDF 35·36쪽). 34쪽 사진은 인물이 작게 나와 `reactor-site-01`로 썼다.

주의해서 쓴 것:
- **작업표준서 3장**(`air/quality.html`): 고객사명(에스트라오토모티브시스템), 품번, 담당자 실명이 그대로 보인다. 기획안은 고객사 익명 원칙이다. 게시 범위를 AMP가 최종 확인하거나 해당 부분을 가려야 한다.
- **인증서 이미지**에는 사업자등록번호·법인번호가 보인다. 가릴지 AMP 확인.
- 공조부품 제품 사진 6컷과 로고는 현 홈페이지 캡처를 잘라 썼다(저해상도). 원본을 받으면 `img/product-*.jpg`, `img/logo.png`만 교체하면 된다.
- 콜라주(PDF 9쪽)에서 잘라 쓴 컷 중 `module-a1/a2`(공정수 재순환), `module-b1/b2`(전구체 입자선별·필터)는 **배치를 추정**했다. 맞는지 AMP 확인 필요.
- 제약·화학 폐수처리 페이지, 공조부품 실적 일부는 사진이 없어 비어 있다.

## 문구 출처

모든 문구는 기획안·PDF 자료에 있는 내용만 사용했다. 숫자(유량, 기간, 매출 등)는 넣지 않았다. 슬로건·인사말·FAQ 답변은 컬리버 초안이라 AMP 승인이 필요하다. 개인정보 보유기간(1년)은 임의 기재라 확인이 필요하다.
