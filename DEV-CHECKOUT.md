# Разработка ChangeRail и закреплённый engine

Разработка ведётся в основном checkout инструмента. Исполняемый engine должен
находиться в отдельном snapshot с проверяемым inventory и явным локальным binding.
Чистый Git checkout или символическая ссылка сами по себе этого не обеспечивают.

- Карточки и OpenSpec changes принадлежат checkout разработки.
- Исторические runs, профили и evidence сохраняются у исходного владельца.
- `.changerail/engine-binding.json` задаёт проверенную привязку к snapshot;
  receipt self-host recovery отдельно фиксирует переход конкретного run.
- Consumer-проекты подключаются через `distribution.py attach --development`
  с inventory/adoption и сохранением локальных данных.
- Локальные абсолютные ссылки, `.runtime`, credentials и настройки агентов
  не публикуются в Git.

Например, checkout разработки может находиться в `/srv/tools/changerail-dev`,
а snapshot — в `/srv/engines/changerail/<identity>`. Эти каталоги произвольны.
