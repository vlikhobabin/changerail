## Why
Реальный self-host successor из чистого committed checkout остановился на проверках: обычный resume требует dirty payload. Смена закреплённого engine для исправления такого runner требует отдельного проверяемого перехода; bound identity предка должна сохранять проектные входы.

## What Changes
- Явный atomic engine rebind с before/after receipt, проверкой snapshots, lock и отсутствия живого владельца.
- Точное продолжение empty payload после self-host перехода; без ослабления fingerprint и execution gates.
- Recovery bound predecessor с сохранением identity проектных входов.
- Исправление fixtures для проверки под реальным binding и Python 3.14.

## Capabilities
### Modified Capabilities
- `native-delivery`: продолжение проверенной self-host финализации.

## Impact
Изменения ограничены engine bootstrap, recovery admission и общими тестами; старые run и snapshots сохраняются.
