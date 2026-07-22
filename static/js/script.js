// ==========================================================
// Category -> Product Dropdown
// ==========================================================
document.addEventListener("DOMContentLoaded", function () {

    const categorySelect = document.getElementById("category");
    const productSelect = document.getElementById("product");

    // Only run on prediction page
    if (!categorySelect || !productSelect) {
        return;
    }

    const productMapping = window.productMapping || {};
    const selectedProduct = window.selectedProduct || "";

    function updateProducts() {

        const category = categorySelect.value;

        productSelect.innerHTML = "";

        // Default option
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Select Product";
        productSelect.appendChild(defaultOption);

        // Populate products
        if (productMapping[category]) {

            productMapping[category].forEach(function (product) {

                const option = document.createElement("option");
                option.value = product;
                option.textContent = product;

                if (product === selectedProduct) {
                    option.selected = true;
                }

                productSelect.appendChild(option);

            });

        }

    }

    categorySelect.addEventListener("change", updateProducts);

    // Load products for the initially selected category
    updateProducts();

});