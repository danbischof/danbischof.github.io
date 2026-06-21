/* Theme toggle — runs immediately to avoid flash of wrong theme */
(function () {
  var saved = localStorage.getItem('theme');
  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  var theme = saved || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
})();

function toggleTheme() {
  var html = document.documentElement;
  var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

function toggleNav() {
  var nav = document.getElementById('site-nav');
  if (nav) nav.classList.toggle('open');
}

document.addEventListener('click', function(e) {
  var nav = document.getElementById('site-nav');
  if (nav && nav.classList.contains('open') && !nav.contains(e.target)) {
    nav.classList.remove('open');
  }
});
