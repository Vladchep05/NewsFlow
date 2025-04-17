const imageInput = document.getElementById('images');
const imagePreview = document.getElementById('imagePreview');
const form = document.querySelector('form');
let selectedImages = [];

const customUploadBtn = document.getElementById('customUploadBtn');
customUploadBtn.addEventListener('click', () => {
    imageInput.click(); // "прокликиваем" скрытый input
});

// Add error container
const errorDiv = document.createElement('div');
errorDiv.id = 'imageError';
errorDiv.classList.add('text-danger', 'mt-2');
imagePreview.parentNode.appendChild(errorDiv);

function showImageError(message) {
    errorDiv.textContent = message;
}

function clearImageError() {
    errorDiv.textContent = '';
}

// Image selection handling
imageInput.addEventListener('change', (event) => {
    const files = Array.from(event.target.files);
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 2 MB

    if (selectedImages.length + files.length > 2) {
        showImageError("Можно загрузить максимум 2 изображения");
        imageInput.value = '';
        return;
    }

    clearImageError();

    files.forEach(file => {
        if (file.size > MAX_FILE_SIZE) {
            showImageError(`Файл "${file.name}" слишком большой. Максимум 5 МБ.`);
            return;
        }

        if (!selectedImages.find(f => f.name === file.name)) {
            selectedImages.push(file);

            const reader = new FileReader();
            reader.onload = function (e) {
                const container = document.createElement('div');
                container.classList.add('image-container');

                            const img = document.createElement('img');
                img.src = e.target.result;

                            const caption = document.createElement('div');
                caption.classList.add('image-caption');
                caption.textContent = file.name;

                            const removeBtn = document.createElement('span');
                removeBtn.classList.add('remove-image');
                removeBtn.textContent = '✖';
                removeBtn.title = 'Удалить изображение';

                            removeBtn.onclick = function () {
                    selectedImages = selectedImages.filter(f => f.name !== file.name);
                    container.remove();
                    if (selectedImages.length < 2) {
                        clearImageError();
                    }
                };

                            container.appendChild(img);
                container.appendChild(caption);
                container.appendChild(removeBtn);
                imagePreview.appendChild(container);
            };
            reader.readAsDataURL(file);
        }
    });
    imageInput.value = '';
});

// Отображение ошибок под полями
function showFieldErrors(errors) {
    ['title', 'content', 'font'].forEach(field => {
        const errorElem = document.getElementById(`${field}-error`);
        if (errorElem) {
            errorElem.textContent = errors[field] || '';
        }
    });
}

// Очистка ошибок перед отправкой
function clearFieldErrors() {
    ['title', 'content', 'font'].forEach(field => {
        const errorElem = document.getElementById(`${field}-error`);
        if (errorElem) {
            errorElem.textContent = '';
        }
    });
}

// Отправка формы через fetch
form.addEventListener('submit', function (e) {
    e.preventDefault();

    clearFieldErrors();

    const formData = new FormData(form);
    selectedImages.forEach(image => {
        formData.append('images', image, image.name);
    });

    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(async res => {
        if (res.redirected) {
            window.location.href = res.url;
        } else if (!res.ok) {
            const data = await res.json();
            if (data.errors) {
                showFieldErrors(data.errors);
            }
        } else {
            return res.text();
        }
    })
    .catch(err => console.error('Ошибка при отправке:', err));
});

// Динамическая смена шрифта
const fontSelect = document.getElementById('font');
const titleInput = document.getElementById('title');
const contentTextarea = document.getElementById('content');

function applyFont(font) {
    titleInput.style.fontFamily = font;
    contentTextarea.style.fontFamily = font;
}

fontSelect.addEventListener('change', function () {
    applyFont(this.value);
});

window.addEventListener('DOMContentLoaded', () => {
    applyFont(fontSelect.value);
});