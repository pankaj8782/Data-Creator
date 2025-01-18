// Function to handle showing/hiding helper fields based on column type selection
function toggleFields(colId) {
    var colType = document.getElementById("col_type_" + colId).value;

    // Hide all dynamic fields initially
    document.querySelectorAll('.dynamic-fields').forEach(function(el) {
        el.style.display = 'none';
    });

    // Show relevant fields based on column type
    if (colType === 'number') {
        document.getElementById("min_max_" + colId).style.display = 'flex';
    } else if (colType === 'date') {
        document.getElementById("date_fields_" + colId).style.display = 'flex';
    } else if (colType === 'datetime') {
        document.getElementById("datetime_fields_" + colId).style.display = 'flex';
    } else if (colType === 'custom') {
        document.getElementById("custom_fields_" + colId).style.display = 'flex';
    }
}

// On page load, hide all dynamic fields initially
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.dynamic-fields').forEach(function(el) {
        el.style.display = 'none';
    });
});

document.getElementById("column-form").onsubmit = function(event) {
    event.preventDefault(); // Prevent form submission

    var formData = new FormData(this);
    fetch("/generate_data", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display download button and set file link
        document.getElementById("download-section").style.display = 'block';
        document.getElementById("download-link").href = data.file_path;
    })
    .catch(error => {
        console.error("Error generating data:", error);
    });
};
