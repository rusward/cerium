(() => {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

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
