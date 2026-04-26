# CELLS Skills — Test Execution Plan

## Phase 1: Test Real Skill Triggering

For each critical skill, I'll verify:
1. Does the description trigger correctly for the right prompts?
2. Does the skill body load and provide clear guidance?
3. Does it reference the right skills/references?

## Phase 2: Test Real Usage

I'll create test scenarios and run them through the actual skills to see:
1. Does the skill produce correct output?
2. Does it consult the right catalogs/skills?
3. Does it enforce the rules (code quality, Cells-native commands, etc.)?

## Phase 3: Fix Based on Results

Improve skills that fail tests, optimize descriptions, and re-test.

## Test Scenarios

### Scenario 1: Component Research
**Prompt**: "Necesito un botón para las acciones de cuenta que muestre un icono de transferencia"
**Expected**: 
- Searches cells-components-catalog SQL first
- Finds bbva-button-default
- Returns component API (props, events, styling)
- Does NOT suggest creating new component

### Scenario 2: Component Creation (when no BBVA match)
**Prompt**: "Necesito un componente que muestre un gráfico de torta con los gastos por categoría del mes"
**Expected**:
- Searches catalog, finds NO matching BBVA component
- Loads cells-component-authoring
- Creates new component with proper scaffold
- Uses `static get properties()`, scopedElements, i18n

### Scenario 3: Test Creation
**Prompt**: "Agrega tests al componente account-actions para cubrir los botones que emiten action-selected"
**Expected**:
- Loads cells-cli-usage first (command resolution)
- Loads cells-coverage second (threshold policy)
- Loads cells-test-creator third (test patterns)
- Creates test with public behavior only
- No private member access
- English descriptions
- No comments

### Scenario 4: Implementation
**Prompt**: "Implementa la tarea 1.1: Agrega icon-left='transfer' al botón de transferencia en src/account-actions.js"
**Expected**:
- Reads specs/design
- Uses bbva-button-default with icon-left prop
- Registers in scopedElements if needed
- Code quality: no trailing commas, semicolons, compact JSDoc, max 2 conditions per method block, .map() if repetitive

### Scenario 5: Verification
**Prompt**: "Verifica que la implementación de account-actions cumple con las specs"
**Expected**:
- Runs tests (cells-native command)
- Checks spec compliance matrix
- Browser validation for visible changes
- Returns structured verdict with evidence

## Execution

I'll run each scenario through the actual skills and check if they produce the expected behavior. For each, I'll note:
- ✅ Pass: Skill triggers correctly and produces expected output
- ⚠️ Partial: Skill works but has gaps
- ❌ Fail: Skill doesn't trigger or produces wrong output
