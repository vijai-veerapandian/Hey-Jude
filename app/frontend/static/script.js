document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    const messageElement = document.getElementById('message');
    const MAX_SIZE_MB = 100;

    if (!file) {
        messageElement.textContent = "Please select a file.";
        return;
    }

    // Validate file size and type
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        messageElement.textContent = `File size must not exceed ${MAX_SIZE_MB}MB.`;
        return;
    }

    if (file.type !== 'application/pdf') {
        messageElement.textContent = "Only PDF files are allowed.";
        return;
    }

    messageElement.textContent = "Uploading and processing document...";

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            messageElement.textContent = `${result.message} You can now chat at http://localhost:8080`;
        } else {
            messageElement.textContent = `Error: ${result.detail || 'An unknown error occurred.'}`;
        }
    } catch (error) {
        messageElement.textContent = `Error: ${error.message}`;
    }
});
