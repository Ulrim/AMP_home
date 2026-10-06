/* AMP 홈페이지 리뉴얼 초안 – 공통 스크립트 (의존성 없음) */
(function () {
  'use strict';

  // 모바일 메뉴
  var burger = document.querySelector('.amp-burger');
  var nav = document.querySelector('.amp-nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // 실적 필터
  var filter = document.querySelector('.amp-filter');
  if (filter) {
    var cards = document.querySelectorAll('[data-cat]');
    filter.addEventListener('click', function (e) {
      var btn = e.target.closest('button');
      if (!btn) return;
      filter.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
      btn.classList.add('on');
      var cat = btn.getAttribute('data-filter');
      cards.forEach(function (c) {
        c.style.display = (cat === 'all' || c.getAttribute('data-cat').split(' ').indexOf(cat) > -1) ? '' : 'none';
      });
    });
  }

  // 문의폼: ?field=battery 로 들어오면 문의 분야 자동 선택
  var sel = document.getElementById('field');
  if (sel) {
    var m = /[?&]field=([^&]+)/.exec(location.search);
    if (m) {
      var want = decodeURIComponent(m[1]);
      for (var i = 0; i < sel.options.length; i++) {
        if (sel.options[i].value === want) { sel.selectedIndex = i; break; }
      }
    }
    var form = sel.form;
    form.addEventListener('submit', function (e) {
      var agree = document.getElementById('agree');
      if (agree && !agree.checked) {
        e.preventDefault();
        alert('개인정보 수집·이용에 동의해 주세요.');
        agree.focus();
      }
    });
  }
})();

// 문의 접수 완료 안내 (contact_ok.php 가 ?sent=1 로 되돌려 보냄)
(function () {
  var box = document.getElementById('sentMsg');
  if (box && /[?&]sent=1/.test(location.search)) box.style.display = 'block';
})();
