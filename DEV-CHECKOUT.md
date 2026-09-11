# Рабочий checkout ChangeRail

Авторитетный checkout для разработки и подготовки релизов: `/opt/changerail-dev`.

- Карточки и OpenSpec changes создаются только здесь.
- `/opt/changerail` — рабочий runtime и историческая точка подключения consumer-проектов; его board защищён от записи.
- `.changerail/engine` указывает на `/opt/changerail` как на текущую стабильную копию engine. Эта ссылка не заменяет отдельный self-host recovery receipt.
- Consumer-проекты не переключаются вручную: для source-link используется поддержанный `distribution.py attach --development` с inventory/adoption.
- `.runtime`, профили, credentials и локальные Codex state остаются локальными и не переносятся в Git.
