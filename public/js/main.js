(function () {

  // ---------------------------------------------------------------------------
  // Copy button on code blocks
  // ---------------------------------------------------------------------------
  document.querySelectorAll('pre').forEach(function (pre) {
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'copy';
    btn.setAttribute('aria-label', 'Copy code');
    pre.appendChild(btn);

    btn.addEventListener('click', function () {
      if (!navigator.clipboard) return;
      var code = pre.querySelector('code');
      var text = code ? code.innerText : pre.innerText.replace(btn.textContent, '').trim();
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'copied!';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'copy';
          btn.classList.remove('copied');
        }, 1800);
      }).catch(function () {
        btn.textContent = 'failed';
        setTimeout(function () { btn.textContent = 'copy'; }, 1800);
      });
    });
  });

  // ---------------------------------------------------------------------------
  // Project carousel
  // ---------------------------------------------------------------------------
  var carousel = document.querySelector('.project-carousel');
  if (carousel) {
    var dots = Array.from(document.querySelectorAll('.carousel-dot'));
    var autoTimer;
    var INTERVAL = 4000;

    function pageWidth() { return carousel.offsetWidth || 1; }

    function activeDotIndex() {
      var idx = Math.round(carousel.scrollLeft / pageWidth());
      return Math.max(0, Math.min(idx, dots.length - 1));
    }

    function setActiveDot(idx) {
      dots.forEach(function (d, i) { d.classList.toggle('active', i === idx); });
    }

    function scrollToPage(idx) {
      carousel.scrollTo({ left: idx * pageWidth(), behavior: 'smooth' });
    }

    function advance() {
      var next = activeDotIndex() + 1;
      if (next >= dots.length) next = 0;
      scrollToPage(next);
    }

    function startAuto() { autoTimer = setInterval(advance, INTERVAL); }
    function stopAuto()  { clearInterval(autoTimer); }

    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        stopAuto();
        scrollToPage(i);
        // Delay restart until after the smooth-scroll animation settles (~400 ms),
        // otherwise advance() may read a stale scrollLeft mid-animation.
        setTimeout(startAuto, 450);
      });
    });
    carousel.addEventListener('scroll', function () { setActiveDot(activeDotIndex()); }, { passive: true });
    carousel.addEventListener('mouseenter', stopAuto);
    carousel.addEventListener('mouseleave', startAuto);
    startAuto();
  }


  var DEFAULT_SPRITE = '/public/images/me-pixel-standing.png';
  var REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var websiteSpriteEl = document.getElementById('website-sprite');
  var websiteImg      = websiteSpriteEl && websiteSpriteEl.querySelector('img');
  if (!websiteImg) websiteSpriteEl = null; // guard: footer img missing, skip init

  // ---------------------------------------------------------------------------
  // Project card hover — swap the persistent website sprite to the card's sprite
  // ---------------------------------------------------------------------------
  document.querySelectorAll('.project-card[data-card-sprite]').forEach(function (card) {
    var src = card.dataset.cardSprite;
    if (!src) return;
    card.addEventListener('mouseenter', function () {
      if (websiteSpriteEl && websiteSpriteEl.dataset.state === 'idle') websiteImg.src = src;
    });
    card.addEventListener('mouseleave', function () {
      if (websiteSpriteEl && websiteSpriteEl.dataset.state === 'idle') websiteImg.src = DEFAULT_SPRITE;
    });
  });

  // ---------------------------------------------------------------------------
  // Persistent website sprite
  //
  // Sequence:
  //   idle     — fixed at resting position, me-pixel-standing.png
  //   grabbed  — follows cursor, me-pixel-grabbed.png
  //   falling  — released: grabbed figure falls off bottom of screen
  //   entering — me-pixel-landing.png rises from the bottom of the screen
  //              to the resting position with a spring overshoot
  //   (then back to idle via opacity crossfade)
  // ---------------------------------------------------------------------------
  if (websiteSpriteEl) {
    var spriteState = 'idle';
    var isDragging  = false;
    var grabOffX = 0, grabOffY = 0;
    // Resting position measured from the DOM at grab time — used as the
    // animation target so the landing sprite ends exactly where the idle
    // sprite was, regardless of how the browser resolves bottom/left CSS.
    var idleLeft = 0, idleTop = 0;
    // Animation timer IDs — cleared on grab to prevent stale callbacks
    // from a prior animation chain corrupting state.
    var animFallTimer = null, animRiseTimer = null;

    var WEBSITE_IMGS = {
      idle:    DEFAULT_SPRITE,
      grabbed: '/public/images/me-pixel-grabbed.png',
      landing: '/public/images/me-pixel-landing.png',
    };

    function setImg(key) {
      if (WEBSITE_IMGS[key]) websiteImg.src = WEBSITE_IMGS[key];
    }

    function setStateName(s) {
      spriteState = s;
      websiteSpriteEl.dataset.state = s;
    }

    // Inline-position the element (overrides the CSS bottom/left rules)
    function pinAt(left, top) {
      websiteSpriteEl.style.left       = left + 'px';
      websiteSpriteEl.style.top        = top  + 'px';
      websiteSpriteEl.style.bottom     = 'auto';
      websiteSpriteEl.style.transition = 'none';
    }

    // Remove inline position so CSS rules take over again
    function unpinToCSS() {
      websiteSpriteEl.style.left       = '';
      websiteSpriteEl.style.top        = '';
      websiteSpriteEl.style.bottom     = '';
      websiteSpriteEl.style.transition = '';
    }

    // ------------------------------------------------------------------
    // GRAB — mousedown on the sprite
    // ------------------------------------------------------------------
    function onGrab(e) {
      if (spriteState !== 'idle') return;
      e.preventDefault();

      // Cancel any in-flight animation chain from a previous release
      clearTimeout(animFallTimer);
      clearTimeout(animRiseTimer);

      var rect = websiteSpriteEl.getBoundingClientRect();
      // Capture exact idle position — reused as the rise animation target
      idleLeft = rect.left;
      idleTop  = rect.top;

      // Always anchor cursor to the left shoulder (~28% from left, ~20% from top)
      grabOffX = websiteImg.offsetWidth  * 0.28;
      grabOffY = websiteImg.offsetHeight * 0.20;

      pinAt(rect.left, rect.top);
      isDragging = true;
      setStateName('grabbed');
      setImg('grabbed');
    }

    // ------------------------------------------------------------------
    // DRAG — follow cursor
    // ------------------------------------------------------------------
    function onDrag(e) {
      if (!isDragging) return;
      e.preventDefault(); // prevent page scroll while dragging on touch
      var ptr = e.type === 'touchmove' ? e.touches[0] : e;
      websiteSpriteEl.style.left = (ptr.clientX - grabOffX) + 'px';
      websiteSpriteEl.style.top  = (ptr.clientY - grabOffY) + 'px';
    }

    // ------------------------------------------------------------------
    // RELEASE — four-phase animation
    // Phase 1: grabbed figure falls off the bottom (0.9s ease-in)
    // Phase 2: snap landing figure below the bottom edge of screen
    // Phase 3: rise to resting position (1.2s cubic-bezier with spring overshoot)
    // Phase 4: opacity crossfade landing → idle, hand control back to CSS
    // ------------------------------------------------------------------
    function onRelease() {
      if (!isDragging) return;
      isDragging = false;

      var spriteH = websiteImg.offsetHeight;

      // Phase 1 — fall off the bottom (0.9s = half of landing 1.8s)
      setStateName('falling');
      websiteSpriteEl.style.transition = 'top 0.9s ease-in';
      websiteSpriteEl.style.top = (window.innerHeight + spriteH + 40) + 'px';

      // Phase 2 — after fall: snap landing figure below the bottom edge
      animFallTimer = setTimeout(function () {
        pinAt(idleLeft, window.innerHeight + spriteH + 40);
        setImg('landing');
        setStateName('entering');

        // Phase 3 — rise from bottom to exact idle resting position
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            websiteSpriteEl.style.transition = 'top 1.2s cubic-bezier(0.34, 1.4, 0.64, 1)';
            websiteSpriteEl.style.top = idleTop + 'px';
          });
        });

        // Phase 4 — crossfade landing → idle
        // Fade out while still pinned, swap everything while invisible,
        // then fade back in so the image change is never seen.
        animRiseTimer = setTimeout(function () {
          var FADE = REDUCED_MOTION ? 1 : 140; // ms

          websiteImg.style.transition = 'opacity ' + FADE + 'ms ease';
          websiteImg.style.opacity = '0';

          setTimeout(function () {
            unpinToCSS();
            setStateName('idle');
            setImg('idle');
            // Force a reflow so the browser commits opacity:0 on the new state
            // before starting the fade-in, otherwise the transition is skipped.
            websiteImg.getBoundingClientRect();
            websiteImg.style.opacity = '1';

            setTimeout(function () {
              websiteImg.style.transition = '';
              websiteImg.style.opacity   = '';
            }, FADE);
          }, FADE);
        }, 1300);

      }, 970);
    }

    websiteSpriteEl.addEventListener('mousedown',  onGrab,     { passive: false });
    websiteSpriteEl.addEventListener('touchstart', onGrab,     { passive: false });
    document.addEventListener('mousemove',    onDrag,     { passive: true  });
    document.addEventListener('touchmove',    onDrag,     { passive: false });
    document.addEventListener('mouseup',      onRelease);
    document.addEventListener('touchend',     onRelease);
  }

  // ---------------------------------------------------------------------------
  // Pixel cursor trail
  //
  // On mousemove: spawn a small pixel square at the cursor with a random
  // offset and color from the website palette, then let CSS animate it out.
  // A lightweight active-count cap prevents DOM bloat during fast sweeps.
  // Touch events are skipped — no cursor on touch screens.
  // ---------------------------------------------------------------------------
  if (!REDUCED_MOTION && window.matchMedia('(pointer: fine)').matches) {
    // Dracula accent palette — https://draculatheme.com/spec
    var SPARKLE_COLORS  = ['#ff79c6', '#bd93f9', '#8be9fd', '#50fa7b', '#ffb86c', '#ff5555', '#f1fa8c'];
    var SPARKLE_SIZES   = [3, 4, 4, 5, 6]; // px — weighted toward 4px
    var SPARKLE_THROTTLE = 25; // ms minimum between spawns
    var SPARKLE_MAX      = 40; // max live sparkles at once
    var sparkleCount     = 0;
    var lastSparkle      = 0;

    document.addEventListener('mousemove', function (e) {
      var now = Date.now();
      if (now - lastSparkle < SPARKLE_THROTTLE) return;
      if (sparkleCount >= SPARKLE_MAX) return;
      lastSparkle = now;

      var size  = SPARKLE_SIZES[Math.floor(Math.random() * SPARKLE_SIZES.length)];
      var color = SPARKLE_COLORS[Math.floor(Math.random() * SPARKLE_COLORS.length)];
      // Snap offset to 2px grid to keep the pixel-art feel
      var ox = Math.round(((Math.random() - 0.5) * 14) / 2) * 2;
      var oy = Math.round(((Math.random() - 0.5) * 14) / 2) * 2;

      var el = document.createElement('div');
      el.className = 'cursor-sparkle';
      el.style.cssText =
        'width:'  + size  + 'px;' +
        'height:' + size  + 'px;' +
        'background:' + color + ';' +
        'left:' + (e.clientX + ox) + 'px;' +
        'top:'  + (e.clientY + oy) + 'px;';

      document.body.appendChild(el);
      sparkleCount++;

      el.addEventListener('animationend', function () {
        document.body.removeChild(el);
        sparkleCount--;
      }, { once: true });
    }, { passive: true });
  }

})();
