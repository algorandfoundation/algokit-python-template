# ESM Migration Summary

## What broke
After upgrading to newer `algokit-utils` alpha dependencies, generated TypeScript projects started pulling ESM-first packages. Our template was still CJS-oriented, which caused:
- Jest ESM import failures
- TS/Jest transform mismatches
- Runtime `__dirname` errors in deploy scripts

## What we changed
### 1) TypeScript package template
File: `template_content/{% if deployment_language == 'typescript' or use_typescript_jest %}package.json{% endif %}.jinja`
- Added `"type": "module"`
- Switched deploy scripts from `ts-node-dev`/`ts-node` to `tsx`
- Updated test script to run Jest with ESM runtime
- Updated dev deps: removed `ts-node-dev`, added `tsx`, added `ts-node`, bumped `typescript` to `^5.7.3`

### 2) TypeScript compiler settings
File: `template_content/{% if deployment_language == 'typescript' or use_typescript_jest %}tsconfig.json{% endif %}`
- Set:
  - `"module": "NodeNext"`
  - `"moduleResolution": "NodeNext"`

### 3) Jest config
File: `template_content/{% if use_typescript_jest %}jest.config.ts{% endif %}`
- Switched to ESM preset: `ts-jest/presets/default-esm`
- Enabled ESM transform (`useESM: true`)
- Added ESM-related config (`extensionsToTreatAsEsm`, `moduleNameMapper`)

### 4) Deploy entrypoint runtime fix
File: `template_content/smart_contracts/{% if deployment_language == 'typescript' %}index.ts{% endif %}.jinja`
- Replaced `__dirname` usage with `import.meta.url` + `fileURLToPath`
- Updated dynamic imports to use file URLs

## Why this approach
It is the smallest coherent long-term fix:
- aligns runtime + compiler + tests around ESM
- avoids fragile CJS shims
- keeps existing Jest-based testing model for now

## Alternatives considered
- Jest-only patch: smaller now, more breakage risk later
- CJS shims/transforms: brittle with modern ESM deps
- Migrate to Vitest: cleaner ESM long-term, but larger change scope

## Validation commands
```bash
poetry run pytest -q -s 'tests/test_generators.py::test_smart_contract_generator_default_production_preset[typescript]'
poetry run pytest -q -s 'tests/test_generators.py::test_smart_contract_generator_default_starter_preset[typescript]'
poetry run pytest -q tests/test_generators.py
poetry run pytest -q tests/test_templates.py
poetry run pytest -q
```
