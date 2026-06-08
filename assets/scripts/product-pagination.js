(() => {
  const PAGE_SIZE = 6;

  function createPageButton(label, pageIndex, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "product-pagination-btn";
    button.textContent = label;
    button.dataset.page = String(pageIndex);
    button.addEventListener("click", onClick);
    return button;
  }

  function setupPagination(grid, gridIndex) {
    const cards = Array.from(grid.querySelectorAll(":scope > .product"));
    if (cards.length <= PAGE_SIZE) {
      return;
    }

    const pageCount = Math.ceil(cards.length / PAGE_SIZE);
    let activePage = 0;

    const nav = document.createElement("nav");
    nav.className = "product-pagination";
    nav.setAttribute("aria-label", `Produktseiten ${gridIndex + 1}`);

    const controls = document.createElement("div");
    controls.className = "product-pagination-controls";
    nav.appendChild(controls);

    const buttons = Array.from({ length: pageCount }, (_, pageIndex) =>
      createPageButton(String(pageIndex + 1), pageIndex, () => {
        setPage(pageIndex, true);
      })
    );

    buttons.forEach((button) => controls.appendChild(button));
    grid.insertAdjacentElement("afterend", nav);

    function setPage(pageIndex, shouldScroll) {
      activePage = pageIndex;

      cards.forEach((card, cardIndex) => {
        const isVisible =
          cardIndex >= pageIndex * PAGE_SIZE &&
          cardIndex < (pageIndex + 1) * PAGE_SIZE;

        card.hidden = !isVisible;
        card.classList.toggle("is-paged-hidden", !isVisible);
      });

      buttons.forEach((button, buttonIndex) => {
        const isActive = buttonIndex === activePage;
        button.classList.toggle("is-active", isActive);
        button.setAttribute("aria-current", isActive ? "page" : "false");
      });

      if (shouldScroll) {
        grid.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    setPage(0, false);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".products").forEach((grid, gridIndex) => {
      setupPagination(grid, gridIndex);
    });
  });
})();
