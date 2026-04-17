const tabs = document.querySelectorAll(".tab");
const cardGroups = document.querySelectorAll(".cards");

tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        // remove active class
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");

        // hide all card groups
        cardGroups.forEach(group => group.classList.add("hidden"));

        // show selected tab content
        const selected = document.getElementById(tab.dataset.tab);
        selected.classList.remove("hidden");
    });
});
