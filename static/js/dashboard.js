function toggleSubcategories(element) {
    const subcategories = element.nextElementSibling;
    if (subcategories) {
        if (subcategories.classList.contains('hidden')) {
            subcategories.classList.remove('hidden');
            element.textContent = '-'; // Change to collapse icon
        } else {
            subcategories.classList.add('hidden');
            element.textContent = '+'; // Change to expand icon
        }
    }
}

function selectSubcategories(checkbox) {
    const level = parseInt(checkbox.getAttribute('data-level'));
    const isChecked = checkbox.checked;

    if (level === 0) {
        // If a level 0 category is selected, select all level 1 and level 2 subcategories
        const subcategories = checkbox.closest('li').querySelectorAll('input[data-level="1"], input[data-level="2"]');
        subcategories.forEach(function (subCheckbox) {
            subCheckbox.checked = isChecked;
        });
    } else if (level === 1) {
        // If a level 1 category is selected, select all level 2 subcategories
        const subSubcategories = checkbox.closest('li').querySelectorAll('input[data-level="2"]');
        subSubcategories.forEach(function (subSubCheckbox) {
            subSubCheckbox.checked = isChecked;
        });

        // If a level 1 category is being selected, do not automatically select its level 0 parent
        if (!isChecked) {
            updateParentState(checkbox);
        }
    } else if (level === 2) {
        // If a level 2 category is selected, do not automatically select its parent categories
        if (!isChecked) {
            const parentCheckbox = document.querySelector('input[data-level="1"][value="' + checkbox.getAttribute('data-parent') + '"]');
            if (parentCheckbox) {
                updateParentState(parentCheckbox);
                const grandParent = parentCheckbox.getAttribute('data-parent');
                if (grandParent) {
                    const grandParentCheckbox = document.querySelector('input[data-level="0"][value="' + grandParent + '"]');
                    if (grandParentCheckbox) {
                        updateParentState(grandParentCheckbox);
                    }
                }
            }
        }
    }
}

// Function to update the state of the parent checkboxes
function updateParentState(parentCheckbox) {
    const childrenCheckboxes = parentCheckbox.closest('li').querySelectorAll('input[data-level="1"], input[data-level="2"]');
    const allChecked = [...childrenCheckboxes].every(child => child.checked);
    const noneChecked = [...childrenCheckboxes].every(child => !child.checked);

    if (allChecked) {
        parentCheckbox.checked = true;
        parentCheckbox.indeterminate = false;
    } else if (noneChecked) {
        parentCheckbox.checked = false;
        parentCheckbox.indeterminate = false;
    } else {
        parentCheckbox.indeterminate = true; // Indicate mixed selection state
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.filter-bar a'); // Select all tabs
    const tabContents = document.querySelectorAll('.tab-content'); // Select all tab content sections

    tabs.forEach(tab => {
        tab.addEventListener('click', function (event) {
            event.preventDefault();

            // Remove active class from all tabs and hide all tab content
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to the clicked tab and corresponding content
            const targetTab = this.getAttribute('data-tab');
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Level 0 category checkbox change event
    document.getElementById('id_level_0_category').addEventListener('change', function () {
        let categoryId = this.value;

        if (categoryId) {
            fetch(`/load-subcategories/?category_id=${categoryId}&level=0`)
                .then(response => response.json())
                .then(data => {
                    let subcategorySelect = document.getElementById('id_level_1_category');
                    subcategorySelect.innerHTML = '<option value="">Select Subcategory</option>';
                    data.forEach(function (subcategory) {
                        let option = document.createElement('option');
                        option.value = subcategory.id;
                        option.textContent = subcategory.name;
                        subcategorySelect.appendChild(option);
                    });

                    // Automatically check subcategories and clear lower-level sub-subcategories
                    document.getElementById('id_level_2_category').innerHTML = '<option value="">Select Sub-subcategory</option>';
                });
        }
    });

    // Level 1 category checkbox change event
    document.getElementById('id_level_1_category').addEventListener('change', function () {
        let subcategoryId = this.value;

        if (subcategoryId) {
            fetch(`/load-subcategories/?category_id=${subcategoryId}&level=1`)
                .then(response => response.json())
                .then(data => {
                    let subSubcategorySelect = document.getElementById('id_level_2_category');
                    subSubcategorySelect.innerHTML = '<option value="">Select Sub-subcategory</option>';
                    data.forEach(function (subSubcategory) {
                        let option = document.createElement('option');
                        option.value = subSubcategory.id;
                        option.textContent = subSubcategory.name;
                        subSubcategorySelect.appendChild(option);
                    });
                });
        }
    });
});