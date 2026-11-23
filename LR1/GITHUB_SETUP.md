# Публікація Smart HelpDesk через сайт GitHub (без програм)

Ця папка призначена для завантаження **через браузер**. Вона містить усі проєктні файли ЛР1, але **не містить папки `.git` та локальної історії Git**. Коміт створюється під час завантаження через вебсайт. Тег `lab01-spec` створюється окремо після публікації.

1. У GitHub відкрийте свою сторінку **Repositories → New**.
2. Введіть назву `Smart-HelpDesk-LR1`. Оберіть Public або Private, як потрібно для перевірки. **Не додавайте** README, `.gitignore` чи License при створенні.
3. Натисніть **Create repository**.
4. На сторінці порожнього репозиторію оберіть **uploading an existing file** (або **Add file → Upload files**).
5. Відкрийте у Windows Провіднику розпаковану папку `Smart_HelpDesk_Browser_Upload`, виділіть вміст (README.md, GITHUB_SETUP.md, `.gitignore`, папки `docs`, `scripts`, `reports`, `.github`) і **перетягніть вміст** у область завантаження GitHub. Важливо: не перетягніть всю зовнішню папку, щоб не виникла зайва вкладеність.
6. Перевірте в переліку, що збережені шляхи `docs/requirements.md`, `docs/architecture.md`, `docs/api-contract.md`, `docs/traceability.csv`, `docs/ai-log.md`, `docs/lab-01.md`, `reports/...`, `.github/workflows/lr1-spec.yml`.
7. У полі повідомлення коміту введіть `docs: add Smart HelpDesk lab 01 specification`. Натисніть **Commit changes** (або **Propose changes**, якщо GitHub пропонує PR).
8. Відкрийте **Actions**, перевірте результат workflow. При необхідності GitHub попросить дозволити запуск Actions.
9. Щоб створити тег без терміналу, відкрийте **Releases → Draft a new release → Choose a tag**, введіть `lab01-spec`, оберіть **Create new tag**, target `main`, укажіть назву `Lab 01 — specification` і натисніть **Publish release**. Це створить тег до поточного коміту гілки main.
10. Перед здачею додайте посилання на репозиторій до звіту й виконайте фактичне перехресне рев’ю та відеозахист, якщо їх вимагає викладач.

**Примітка:** цей браузерний спосіб не переносить стару локальну Git-історію, лише вміст файлів. Якщо потрібна саме оригінальна історія комітів, її треба передати з локального Git через командний рядок або інший Git-клієнт.
