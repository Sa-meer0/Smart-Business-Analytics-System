const categorySelect = document.getElementById("category");
const productSelect = document.getElementById("product");

if (categorySelect && productSelect) {

    const productMapping = window.productMapping || {};

    function updateProducts() {

        const category = categorySelect.value;

        productSelect.innerHTML = "";

        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.text = "Select Product";
        productSelect.appendChild(defaultOption);

        if (productMapping[category]) {

            productMapping[category].forEach(function (product) {

                const option = document.createElement("option");
                option.value = product;
                option.text = product;

                if (product === window.selectedProduct) {
                    option.selected = true;
                }

                productSelect.appendChild(option);
            });

        }

    }

    categorySelect.addEventListener("change", updateProducts);

    updateProducts();
}