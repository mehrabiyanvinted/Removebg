document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.result === 'success') {
            // Display the processed image
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `<img src="data:image/jpeg;base64,${data.processed_image}" alt="Processed Image">`;
        } else {
            alert('Error processing the image. Please try again.');
        }
    });
});
