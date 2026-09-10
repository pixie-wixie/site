// Optional enhancements: all content and links work without JavaScript.
const cards = [...document.querySelectorAll('.article-card')];
const filters = [...document.querySelectorAll('[data-filter]')];
const search = document.querySelector('.search');
const empty = document.querySelector('.empty');
let selected = 'Усі матеріали';
function applyFilters() {
  const query = (search?.value || '').trim().toLocaleLowerCase('uk');
  let visible = 0;
  cards.forEach(card => {
    const matches = (selected === 'Усі матеріали' || card.dataset.category === selected)
      && card.textContent.toLocaleLowerCase('uk').includes(query);
    card.hidden = !matches;
    if (matches) visible++;
  });
  if (empty) empty.hidden = visible > 0;
}
document.querySelectorAll('.filters, .search-controls').forEach(el => el.hidden = false);
filters.forEach(button => button.addEventListener('click', () => {
  selected = button.dataset.filter;
  filters.forEach(filter => {
    const active = filter === button;
    filter.classList.toggle('active', active);
    filter.setAttribute('aria-pressed', String(active));
  });
  applyFilters();
}));
search?.addEventListener('input', applyFilters);
