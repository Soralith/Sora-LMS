/* =============================================
   SORA LMS — Landing Page Script
   Theme: Blue (#3b82f6)
============================================== */

/* =============================================
   SORA LMS — Landing Page Script
   Theme: Blue (#3b82f6)
============================================== */

const SORA_API_BASE = window.location.origin;

// ---- DYNAMIC LINKS ----
function updateDynamicLinks() {
  const links = document.querySelectorAll('a[data-dynamic-href]');
  links.forEach(link => {
    link.setAttribute('href', SORA_API_BASE + link.dataset.dynamicHref);
  });
}

// ---- AUTH CHECK ----
async function checkAuthStatus() {
  try {
    const res = await fetch(`${SORA_API_BASE}/accounts/auth-status/`, {
      credentials: 'include',
    });
    const data = await res.json();

    if (data.is_authenticated) {
      // Update nav CTA
      const navCta = document.getElementById('nav-cta');
      const avatarSrc = data.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.username}`;
      if (navCta) {
        navCta.innerHTML = `
          <a href="${SORA_API_BASE}/dashboard/" class="btn btn--ghost">Dashboard</a>
          <a href="${SORA_API_BASE}/accounts/profile/" class="btn btn--primary btn--user">
            <img src="${avatarSrc}" alt="" onerror="this.src='https://api.dicebear.com/7.x/avataaars/svg?seed=${data.username}'" />
            ${data.name}
          </a>
        `;
      }

      // Update hero CTA button
      const btnCtaPrimary = document.getElementById('btn-cta-primary');
      if (btnCtaPrimary) {
        btnCtaPrimary.setAttribute('href', `${SORA_API_BASE}/dashboard/`);
        btnCtaPrimary.innerHTML = `
          Pergi ke Dashboard
          <i class="bi bi-arrow-right"></i>
        `;
      }

      // Update CTA final section
      const ctaFinalTitle = document.getElementById('cta-final-title');
      const ctaFinalText = document.getElementById('cta-final-text');
      const btnCtaFinal = document.getElementById('btn-cta-final');
      if (ctaFinalTitle && ctaFinalText && btnCtaFinal) {
        ctaFinalTitle.innerHTML = `Selamat Datang<br />Kembali, ${data.name.split(' ')[0]}!`;
        ctaFinalText.textContent = 'Lanjutkan perjalanan belajarmu sekarang! Dengan kelas-kelas menarik dan tutor AI yang siap membantu 24/7.';
        btnCtaFinal.setAttribute('href', `${SORA_API_BASE}/dashboard/`);
        btnCtaFinal.textContent = 'Pergi ke Dashboard';
      }

      // Update hero welcome
      const dashboardUsername = document.getElementById('dashboard-username');
      if (dashboardUsername) {
        dashboardUsername.textContent = data.name;
      }
    }
  } catch (e) {
    console.error('Auth check error:', e);
  }
}

checkAuthStatus();
updateDynamicLinks();

// ---- NAVBAR SCROLL EFFECT ----
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
}, { passive: true });


// ---- HAMBURGER MENU ----
const hamburger = document.getElementById('hamburger');
hamburger.addEventListener('click', () => {
  const navLinks = document.querySelector('.nav__links');
  const navCta   = document.querySelector('.nav__cta');
  const isOpen   = navLinks.style.display === 'flex';

  if (isOpen) {
    navLinks.style.display = '';
    navCta.style.display   = '';
    hamburger.classList.remove('open');
  } else {
    navLinks.style.cssText = `
      display: flex; flex-direction: column; align-items: flex-start; gap: 4px;
      position: fixed; top: 70px; left: 0; right: 0;
      background: rgba(15,23,42,.97); backdrop-filter: blur(20px);
      padding: 24px; border-bottom: 1px solid rgba(59,130,246,.18);
      z-index: 99;
    `;
    navCta.style.cssText = `
      display: flex; flex-direction: column; align-items: stretch;
      position: fixed; top: calc(70px + ${navLinks.offsetHeight}px); left: 0; right: 0;
      padding: 0 24px 24px;
      background: rgba(15,23,42,.97); backdrop-filter: blur(20px);
      z-index: 99;
    `;
    hamburger.classList.add('open');
  }
});


// ---- REVEAL ON SCROLL ----
const revealEls = document.querySelectorAll('.reveal');

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

revealEls.forEach(el => revealObserver.observe(el));


// ---- COUNTER ANIMATION ----
function formatNumber(num) {
  if (num >= 1000) return (num / 1000).toFixed(num % 1000 === 0 ? 0 : 0) + 'K';
  return num.toString();
}

function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const duration = 1800;
  const start = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(eased * target);
    el.textContent = formatNumber(current);
    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

const statNums = document.querySelectorAll('.stat-num');
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      counterObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

statNums.forEach(el => counterObserver.observe(el));


// ---- SMOOTH ANCHOR SCROLL ----
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const offset = 80;
    const top = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});


// ---- TILT EFFECT ON DASHBOARD CARD ----
const dashCard = document.querySelector('.dashboard-card');
const heroVisual = document.querySelector('.hero__visual');

if (heroVisual && dashCard) {
  heroVisual.addEventListener('mousemove', (e) => {
    const rect = heroVisual.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top)  / rect.height - 0.5;
    dashCard.style.transform = `perspective(800px) rotateY(${x * 8}deg) rotateX(${-y * 6}deg) scale(1.02)`;
  });
  heroVisual.addEventListener('mouseleave', () => {
    dashCard.style.transform = '';
    dashCard.style.transition = 'transform .5s ease';
    setTimeout(() => { dashCard.style.transition = ''; }, 500);
  });
}


// ---- CURSOR RING (Desktop) ----
document.addEventListener('DOMContentLoaded', () => {
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  if (!isTouchDevice) {
    const cursorRing = document.createElement('div');
    cursorRing.style.cssText = `
      position: fixed; pointer-events: none; z-index: 9999;
      width: 32px; height: 32px;
      border-radius: 50%;
      border: 2px solid #3b82f6;
      background: rgba(59,130,246,0.1);
      transform: translate(-50%, -50%);
      will-change: transform;
    `;
    document.body.appendChild(cursorRing);

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', e => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });
    function animateCursor() {
      cursorRing.style.left = mouseX + 'px';
      cursorRing.style.top = mouseY + 'px';
      requestAnimationFrame(animateCursor);
    }
    animateCursor();
  }

  // Hero entrance
  const heroReveals = document.querySelectorAll('.hero .reveal');
  heroReveals.forEach((el, i) => {
    setTimeout(() => el.classList.add('visible'), 150 + i * 80);
  });
});