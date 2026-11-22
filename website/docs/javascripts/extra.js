(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  for (const heading of document.querySelectorAll(".md-typeset h1")) {
    if (!heading.dataset.text) {
      const clone = heading.cloneNode(true);
      for (const permalink of clone.querySelectorAll(".headerlink")) {
        permalink.remove();
      }
      heading.dataset.text = clone.textContent.trim();
    }
    heading.classList.add("cerium-glitch");
  }

  if (reduceMotion || !("IntersectionObserver" in window)) return;

  const cards = document.querySelectorAll(".cerium-card");
  if (!cards.length) return;

  cards.forEach((card) => card.classList.add("cerium-reveal"));

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.12 }
  );

  cards.forEach((card) => observer.observe(card));
})();
