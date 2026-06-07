/**
 * Подключаем EasyMDE к textarea и синхронизируем текст перед отправкой формы.
 * Без этого браузер видит пустое скрытое поле и блокирует submit (атрибут required).
 */
function initEasyMDE(textareaId) {
  const textarea = document.getElementById(textareaId);
  if (!textarea) {
    return null;
  }

  // Проверку делаем на сервере, иначе required мешает отправке
  textarea.removeAttribute("required");

  const editor = new EasyMDE({
    element: textarea,
    spellChecker: false,
    status: false,
  });

  const form = textarea.closest("form");
  if (form) {
    form.addEventListener("submit", function () {
      editor.codemirror.save();
    });
  }

  return editor;
}
