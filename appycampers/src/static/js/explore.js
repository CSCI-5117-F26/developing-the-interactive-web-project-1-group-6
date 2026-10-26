const filterButton = document.getElementById("filter-button");
const filterPanel = document.getElementById("filter-panel");

filterButton.addEventListener("click", function () {
    filterPanel.hidden = !filterPanel.hidden;
});