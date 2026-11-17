/* Octagon Defense: mobile menu + polish layer (entrance motion). No dependencies. */
(function () {
  var root = document.documentElement;
  root.classList.add('js');

  // Mobile menu
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? 'Close' : 'Menu';
    });
  }

  // Site forms: post to Formspree when an endpoint is configured; otherwise open a pre-filled email.
  document.querySelectorAll('form.rq').forEach(function (form) {
    var status = form.querySelector('.rq__status');
    var say = function (msg, ok) { status.textContent = msg; status.classList.toggle('is-ok', !!ok); };
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var bad = [];
      form.querySelectorAll('[required]').forEach(function (el) {
        var empty = !String(el.value || '').trim();
        el.setAttribute('aria-invalid', empty ? 'true' : 'false');
        if (empty) bad.push(el);
      });
      if (bad.length) { say('Please fill in the highlighted fields.'); bad[0].focus(); return; }
      var data = new FormData(form);
      if (data.get('_gotcha')) return;
      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint) {
        var lines = [];
        data.forEach(function (v, k) { if (k.charAt(0) !== '_' && String(v).trim()) lines.push(k.replace(/_/g, ' ') + ': ' + v); });
        var subject = form.getAttribute('data-mail-subject') + ' from ' + data.get('name');
        window.location.href = 'mailto:' + form.getAttribute('data-email') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
        say('Your email app should open with the details filled in. Send it to reach Brennan.', true);
        return;
      }
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true; say('Sending…');
      fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); say(form.getAttribute('data-ok'), true); })
        .catch(function () { say('That didn\u2019t send. Please call ' + form.querySelector('.rq__alt a').textContent + ' instead.'); })
        .then(function () { btn.disabled = false; });
    });
  });

  // Entrance motion: skipped entirely for reduced motion or old browsers, so nothing starts hidden.
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  root.classList.add('js-polish');
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-visible');
      io.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('[data-animate], [data-animate-stagger]').forEach(function (el) { io.observe(el); });
})();
