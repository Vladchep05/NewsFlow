// Получаем все кнопки и контент
const profileSettingsBtn = document.getElementById('profile-settings-btn');
const generalSettingsBtn = document.getElementById('general-settings-btn');
const themeSettingsBtn = document.getElementById('theme-settings-btn');
const fontSettingsBtn = document.getElementById('font-settings-btn');
const logoutBtn = document.getElementById('logout-btn');

const profileSettingsContent = document.getElementById('profile-settings-content');
const generalSettingsContent = document.getElementById('general-settings-content');
const themeSettingsContent = document.getElementById('theme-settings-content');
const fontSettingsContent = document.getElementById('font-settings-content');
const logoutContent = document.getElementById('logout-content');

// Функция для скрытия всех контентов
function hideAllContent() {
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
}

// Функция для сбора данных формы
function getFormData(formId) {
    const form = document.getElementById(formId);
    const data = new FormData(form);
    const formDataObject = {};
    data.forEach((value, key) => {
        formDataObject[key] = value;
    });
    return formDataObject;
}

// Обработчики для кнопок
profileSettingsBtn.addEventListener('click', function() {
    hideAllContent();
    profileSettingsContent.classList.add('active');
    setActiveButton(profileSettingsBtn);
});

generalSettingsBtn.addEventListener('click', function() {
    hideAllContent();
    generalSettingsContent.classList.add('active');
    setActiveButton(generalSettingsBtn);
});

themeSettingsBtn.addEventListener('click', function() {
    hideAllContent();
    themeSettingsContent.classList.add('active');
    setActiveButton(themeSettingsBtn);
});

fontSettingsBtn.addEventListener('click', function() {
    hideAllContent();
    fontSettingsContent.classList.add('active');
    setActiveButton(fontSettingsBtn);
});

logoutBtn.addEventListener('click', function() {
    hideAllContent();
    logoutContent.classList.add('active');
    setActiveButton(logoutBtn);
});

// Функция для выделения активной кнопки
function setActiveButton(button) {
    const buttons = document.querySelectorAll('.settings-btn');
    buttons.forEach(btn => btn.classList.remove('active-btn'));
    button.classList.add('active-btn');
}

// Пример сбора данных формы
document.getElementById('profile-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const data = getFormData('profile-form');
    console.log(data);  // Можете отправить эти данные на сервер через AJAX или использовать в Python
});
