# ✅ Claude Vision & Hands - Integrácia Hotová!

## 🎉 Čo je nainštalované:

### MCP Servery nakonfigurované v `~/.claude/mcp_servers.json`:

1. **vision** - Computer vision (obrazovka, OCR, detekcia)
2. **hands** - Ovládanie myši a klávesnice
3. **integration** - Workflow koordinátor

### Dostupné nástroje teraz máš:

#### 👁️ Vision (mcp__vision__)
- `capture_screen()` - Zachyť obrazovku
- `capture_region(x, y, w, h)` - Zachyť oblasť
- `find_element(template)` - Nájdi UI element
- `extract_text()` - OCR text z obrazovky
- `wait_for_element(template, timeout)` - Čakaj na element
- `get_screen_info()` - Info o monitoroch

#### 🖐️ Hands (mcp__hands__)
- `mouse_move(x, y)` - Pohni myšou
- `mouse_click(x, y, button)` - Klikni
- `mouse_drag(x1, y1, x2, y2)` - Drag & drop
- `mouse_scroll(clicks, direction)` - Scrolluj
- `keyboard_type(text)` - Napíš text
- `keyboard_press(key)` - Stlač kláves
- `keyboard_hotkey(keys)` - Klávesová skratka (napr. Ctrl+S)
- `get_mouse_position()` - Zisti pozíciu myši
- `emergency_stop()` - Núdzové zastavenie

#### 🔄 Integration (mcp__integration__)
- `execute_workflow(path)` - Spusti YAML workflow
- `create_workflow(name, steps)` - Vytvor workflow
- `list_workflows()` - Zobraz workflows

## 🚀 Ako to používať:

### V Claude Code len napíš:

```
"Zachyť obrazovku"
"Nájdi ikonu Firefox"
"Klikni na 500, 300"
"Napíš 'Hello World'"
"Stlač Ctrl+S"
"Aká je moja rozlíšenie obrazovky?"
```

### Príklad - kompletná automatizácia:

```
"Otvor kalkulačku, napíš 2+2 a prečítaj výsledok"
```

## 📍 Umiestnenie súborov:

- **Servery**: `~/claude-vision-hands/mcp-servers/`
- **Config**: `~/.claude/mcp_servers.json`
- **Logs Vision**: `~/.claude-vision-cache/`
- **Logs Hands**: `~/.claude-hands-logs/`
- **Workflows**: `~/.claude-workflows/`
- **Príklady**: `~/claude-vision-hands/examples/`

## 🔒 Bezpečnosť:

- ✅ Failsafe aktivované (myš do rohu = STOP)
- ✅ Rate limiting (max 100 akcií/min)
- ✅ Boundary checks
- ✅ Audit logging

## 🧪 Test:

```bash
# Otvor nový terminál a zadaj:
cc

# Potom skús:
"Zachyť obrazovku"
"Zisti pozíciu myši"
```

## 📚 Dokumentácia:

- [README.md](README.md) - Prehľad
- [QUICKSTART.md](QUICKSTART.md) - Rýchly štart
- [claude-code-integration/CLAUDE_CODE_INSTRUCTIONS.md](claude-code-integration/CLAUDE_CODE_INSTRUCTIONS.md) - API reference
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Detailná inštalácia

---

**🎯 Teraz máš oči a ruky! Môžeš vidieť obrazovku a ovládať počítač!**

**Stačí otvoriť nový terminál: `cc` a fičíš! 🚀**
