/* AMP 홈페이지 리뉴얼 초안 – 공통 스크립트 (의존성 없음) */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  // 헤더: 스크롤하면 흰 배경으로 전환 (히어로 위에서는 투명)
  var header = document.querySelector('.amp-header');
  function onScroll() {
    if (!header) return;
    var solid = header.hasAttribute('data-solid') || window.scrollY > 30;
    header.classList.toggle('solid', solid);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // 모바일 메뉴
  var burger = document.querySelector('.amp-burger');
  var nav = document.querySelector('.amp-nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open && header) header.classList.add('solid');
      else onScroll();
    });
  }

  // 스크롤 등장 효과
  var rv = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    rv.forEach(function (el) { io.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add('in'); });
  }

  // 숫자 카운트업
  var nums = document.querySelectorAll('[data-count]');
  function count(el) {
    var to = parseInt(el.getAttribute('data-count'), 10), n = 0, step = Math.max(1, Math.round(to / 20));
    var t = setInterval(function () { n += step; if (n >= to) { n = to; clearInterval(t); } el.textContent = n; }, 45);
  }
  if ('IntersectionObserver' in window && nums.length) {
    var io2 = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { count(e.target); io2.unobserve(e.target); } });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { io2.observe(el); });
  }

  // 히어로 물방울
  var bub = document.querySelector('.amp-bubbles');
  if (bub && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    for (var i = 0; i < 14; i++) {
      var b = document.createElement('i'), s = 8 + Math.random() * 38;
      b.style.cssText = 'left:' + (Math.random() * 100) + '%;width:' + s + 'px;height:' + s + 'px;animation-duration:' + (12 + Math.random() * 16) + 's;animation-delay:-' + (Math.random() * 20) + 's';
      bub.appendChild(b);
    }
  }

  // 이미지 확대 보기
  var lb = document.createElement('div');
  lb.className = 'amp-lb';
  lb.innerHTML = '<img alt="">';
  document.body.appendChild(lb);
  document.addEventListener('click', function (e) {
    var im = e.target.closest('.amp-gallery img, .amp-figure img, .amp-certrow img');
    if (im) { lb.firstChild.src = im.src; lb.firstChild.alt = im.alt; lb.classList.add('on'); }
    else if (lb.classList.contains('on')) lb.classList.remove('on');
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') lb.classList.remove('on'); });

  // 실적 필터
  var filter = document.querySelector('.amp-filter');
  if (filter) {
    var cards = document.querySelectorAll('[data-cat]');
    filter.addEventListener('click', function (e) {
      var btn = e.target.closest('button');
      if (!btn) return;
      filter.querySelectorAll('button').forEach(function (x) { x.classList.remove('on'); });
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
      for (var k = 0; k < sel.options.length; k++) {
        if (sel.options[k].value === want) { sel.selectedIndex = k; break; }
      }
    }
    sel.form.addEventListener('submit', function (e) {
      var agree = document.getElementById('agree');
      if (agree && !agree.checked) {
        e.preventDefault();
        alert('개인정보 수집·이용에 동의해 주세요.');
        agree.focus();
      }
    });
  }

  // 문의 접수 완료 안내 (contact_ok.php 가 ?sent=1 로 되돌려 보냄)
  var box = document.getElementById('sentMsg');
  if (box && /[?&]sent=1/.test(location.search)) box.style.display = 'block';
})();
