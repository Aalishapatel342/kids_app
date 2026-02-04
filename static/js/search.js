document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="search"]');
    const cards = document.querySelectorAll('.card');

    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();

        cards.forEach(card => {
            const name = card.getAttribute('data-name').toLowerCase();
            const desc = card.getAttribute('data-desc').toLowerCase();

            if (name.includes(query) || desc.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});
