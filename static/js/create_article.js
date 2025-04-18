// Получаем элементы DOM
const imageInput = document.getElementById('images');
const imagePreview = document.getElementById('imagePreview');
const form = document.querySelector('form');
let selectedImages = []; // Хранилище выбранных изображений

// Кнопка для открытия диалога выбора файлов
const customUploadBtn = document.getElementById('customUploadBtn');
customUploadBtn.addEventListener('click', () => {
    imageInput.click(); // Имитация клика по скрытому input
});

// Создаём и добавляем контейнер для ошибок изображений
const errorDiv = document.createElement('div');
errorDiv.id = 'imageError';
errorDiv.classList.add('text-danger', 'mt-2');
imagePreview.parentNode.appendChild(errorDiv);

// Функция показа ошибки загрузки изображения
function showImageError(message) {
    errorDiv.textContent = message;
}

// Очистка сообщения об ошибке
function clearImageError() {
    errorDiv.textContent = '';
}

// Обработка выбора изображений
imageInput.addEventListener('change', (event) => {
    const files = Array.from(event.target.files); // Преобразуем FileList в массив
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // Максимальный размер файла: 5 МБ

    // Проверка лимита изображений (не больше 2)
    if (selectedImages.length + files.length > 2) {
        showImageError("Можно загрузить максимум 2 изображения");
        imageInput.value = ''; // Сброс выбранных файлов
        return;
    }

    clearImageError(); // Очищаем ошибку перед добавлением

    files.forEach(file => {
        // Проверка размера файла
        if (file.size > MAX_FILE_SIZE) {
            showImageError(`Файл "${file.name}" слишком большой. Максимум 5 МБ.`);
            return;
        }

        // Проверка на дубликаты по имени
        if (!selectedImages.find(f => f.name === file.name)) {
            selectedImages.push(file); // Добавляем файл в массив

            const reader = new FileReader();
            reader.onload = function (e) {
                // Создание контейнера изображения
                const container = document.createElement('div');
                container.classList.add('image-container');

                // Создание тега <img> с превью
                const img = document.createElement('img');
                img.src = e.target.result;

                // Название файла
                const caption = document.createElement('div');
                caption.classList.add('image-caption');
                caption.textContent = file.name;

                // Кнопка удаления изображения
                const removeBtn = document.createElement('span');
                removeBtn.classList.add('remove-image');
                removeBtn.textContent = '✖';
                removeBtn.title = 'Удалить изображение';

                // Обработчик удаления
                removeBtn.onclick = function () {
                    selectedImages = selectedImages.filter(f => f.name !== file.name);
                    container.remove();
                    if (selectedImages.length < 2) {
                        clearImageError(); // Убираем ошибку, если допустимо снова загружать
                    }
                };

                // Добавление всех элементов в DOM
                container.appendChild(img);
                container.appendChild(caption);
                container.appendChild(removeBtn);
                imagePreview.appendChild(container);
            };
            reader.readAsDataURL(file); // Чтение файла как base64 для превью
        }
    });

    imageInput.value = ''; // Сброс input, чтобы можно было выбрать те же файлы снова
});

// Отображение ошибок под полями (текстовые поля и шрифт)
function showFieldErrors(errors) {
    ['title', 'content', 'font'].forEach(field => {
        const errorElem = document.getElementById(`${field}-error`);
        if (errorElem) {
            errorElem.textContent = errors[field] || '';
        }
    });
}

// Очистка всех полей ошибок перед отправкой формы
function clearFieldErrors() {
    ['title', 'content', 'font'].forEach(field => {
        const errorElem = document.getElementById(`${field}-error`);
        if (errorElem) {
            errorElem.textContent = '';
        }
    });
}

// Обработка отправки формы
form.addEventListener('submit', function (e) {
    e.preventDefault(); // Отменяем стандартную отправку формы

    clearFieldErrors(); // Очищаем ошибки

    const formData = new FormData(form); // Собираем данные формы
    selectedImages.forEach(image => {
        formData.append('images', image, image.name); // Добавляем изображения вручную
    });

    // Отправляем данные на сервер
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(async res => {
        // Если сервер сделал редирект — переходим по новому URL
        if (res.redirected) {
            window.location.href = res.url;
        } else if (!res.ok) {
            // Если сервер вернул ошибки — отображаем их
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

// Работа со шрифтами — динамическое применение
const fontSelect = document.getElementById('font');
const titleInput = document.getElementById('title');
const contentTextarea = document.getElementById('content');

// Применение выбранного шрифта к полям
function applyFont(font) {
    titleInput.style.fontFamily = font;
    contentTextarea.style.fontFamily = font;
}

// Обработчик изменения шрифта
fontSelect.addEventListener('change', function () {
    applyFont(this.value);
});

// Применяем текущий шрифт при загрузке страницы
window.addEventListener('DOMContentLoaded', () => {
    applyFont(fontSelect.value);
});
