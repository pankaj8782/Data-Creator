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

document.getElementById('column-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission

    const generateBtn = document.getElementById('generate-btn');
    const buttonLabel = document.getElementById('button-label');
    const spinner = document.getElementById('spinner');

    // Show spinner, hide label, and disable the button
    generateBtn.disabled = true;
    buttonLabel.style.display = 'none';
    spinner.style.display = 'block';

    // Create a FormData object to send the form data via AJAX
    const formData = new FormData(this);

    // Send data to the server via POST
    fetch('/generate_data', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else if (data.file_path) {
                // Show download link
                const downloadLink = document.getElementById('download-link');
                downloadLink.href = '/' + data.file_path;
                downloadLink.style.display = 'inline-block';
                downloadLink.innerText = 'Download';
            }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => {
            // Hide spinner, show label, and re-enable the button
            spinner.style.display = 'none';
            buttonLabel.style.display = 'inline';
            generateBtn.disabled = false;
        });
});
