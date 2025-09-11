from __future__ import annotations

from typing import Any, Literal, Optional, Sequence, cast

import pygame

from .errors import PreExperimentSurveyError

FieldType = Literal["text", "dropdown", "checkbox"]


# ----------------------------- Utility / Constants -----------------------------


class Colors:
    BG = (28, 28, 35)
    PANEL = (40, 40, 52)
    TEXT = (230, 230, 235)
    TEXT_DIM = (170, 170, 180)
    ACCENT = (100, 149, 237)
    ACCENT_HOVER = (130, 180, 255)
    ERROR = (220, 80, 80)
    OUTLINE = (90, 90, 105)
    DISABLED_BG = (70, 70, 80)
    CHECKMARK = (60, 200, 120)


PADDING_HORIZONTAL = 30
WINDOW_WIDTH = 720
BASE_HEIGHT = 180  # will expand based on fields dynamically
LINE_HEIGHT = 30
FONT_SIZE = 20
SMALL_FONT_SIZE = 16
DROPDOWN_OPTION_HEIGHT = 28
FPS = 60


# ----------------------------- Widget Base Class ------------------------------


class Widget:
    def __init__(self):
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.focused: bool = False
        self.visible: bool = True
        self.enabled: bool = True

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False  # return True if event was consumed

    def set_position(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)

    def wants_tab_focus(self) -> bool:
        return False

    def get_value(self) -> Any:
        return None


# ----------------------------- Text Input Widget ------------------------------


class TextInput(Widget):
    def __init__(self, font: pygame.font.Font, initial: str = ""):
        super().__init__()
        self.font = font
        self.text = initial
        self.caret_pos = len(self.text)
        self._blink_timer = 0
        self._show_caret = True

    def wants_tab_focus(self) -> bool:
        return True

    def get_value(self) -> str:
        return self.text

    def draw(self, surface: pygame.Surface):
        # Background
        bg = Colors.PANEL if self.enabled else Colors.DISABLED_BG
        pygame.draw.rect(surface, bg, self.rect, border_radius=4)
        outline_color = Colors.ACCENT if self.focused else Colors.OUTLINE
        pygame.draw.rect(surface, outline_color, self.rect, width=2, border_radius=4)

        # Text
        display_text = self.text
        txt_surf = self.font.render(
            display_text, True, Colors.TEXT if self.enabled else Colors.TEXT_DIM
        )
        surface.blit(
            txt_surf,
            (
                self.rect.x + 8,
                self.rect.y + (self.rect.height - txt_surf.get_height()) // 2,
            ),
        )

        # Caret blinking
        if self.focused and self.enabled:
            self._blink_timer += 1
            if self._blink_timer >= FPS // 2:
                self._blink_timer = 0
                self._show_caret = not self._show_caret
            if self._show_caret:
                caret_x = self.font.size(display_text[: self.caret_pos])[0]
                caret_rect = pygame.Rect(
                    self.rect.x + 8 + caret_x,
                    self.rect.y + 6,
                    2,
                    self.rect.height - 12,
                )
                pygame.draw.rect(surface, Colors.ACCENT, caret_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.focused = True
                # Set caret approximate position
                rel_x = event.pos[0] - (self.rect.x + 8)
                # Determine caret index
                caret = 0
                for i in range(len(self.text) + 1):
                    width = self.font.size(self.text[:i])[0]
                    if width >= rel_x:
                        caret = i
                        break
                    caret = i
                self.caret_pos = caret
                return True
            else:
                self.focused = False
        if self.focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.caret_pos > 0:
                    self.text = (
                        self.text[: self.caret_pos - 1] + self.text[self.caret_pos :]
                    )
                    self.caret_pos -= 1
                return True
            elif event.key == pygame.K_DELETE:
                if self.caret_pos < len(self.text):
                    self.text = (
                        self.text[: self.caret_pos] + self.text[self.caret_pos + 1 :]
                    )
                return True
            elif event.key == pygame.K_LEFT:
                if self.caret_pos > 0:
                    self.caret_pos -= 1
                return True
            elif event.key == pygame.K_RIGHT:
                if self.caret_pos < len(self.text):
                    self.caret_pos += 1
                return True
            elif event.key == pygame.K_HOME:
                self.caret_pos = 0
                return True
            elif event.key == pygame.K_END:
                self.caret_pos = len(self.text)
                return True
            elif event.key == pygame.K_TAB:
                # Let container manage focus cycle
                self.focused = False
                return False
            elif event.key == pygame.K_RETURN:
                # Treat Enter as unfocus
                self.focused = False
                return True
            else:
                if event.unicode and event.unicode.isprintable():
                    self.text = (
                        self.text[: self.caret_pos]
                        + event.unicode
                        + self.text[self.caret_pos :]
                    )
                    self.caret_pos += 1
                    return True
        return False


# ----------------------------- Checkbox Widget --------------------------------


class Checkbox(Widget):
    BOX_SIZE = 22

    def __init__(self, font: pygame.font.Font, label: str):
        super().__init__()
        self.font = font
        self.label = label
        self.value = False

    def get_value(self) -> bool:
        return self.value

    def draw(self, surface: pygame.Surface):
        # Box
        box_rect = pygame.Rect(self.rect.x, self.rect.y, self.BOX_SIZE, self.BOX_SIZE)
        pygame.draw.rect(surface, Colors.PANEL, box_rect, border_radius=4)
        pygame.draw.rect(surface, Colors.OUTLINE, box_rect, width=2, border_radius=4)
        if self.value:
            inner = box_rect.inflate(-6, -6)
            pygame.draw.rect(surface, Colors.CHECKMARK, inner, border_radius=3)

        # Label
        txt_surf = self.font.render(self.label, True, Colors.TEXT)
        surface.blit(
            txt_surf,
            (
                box_rect.right + 10,
                box_rect.y + (box_rect.height - txt_surf.get_height()) // 2,
            ),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value
                return True
        return False


# ----------------------------- Dropdown Widget --------------------------------


class Dropdown(Widget):
    def __init__(self, font: pygame.font.Font, options: list[str]):
        super().__init__()
        self.font = font
        self.options = options
        self.selected_index = 0
        self.open = False
        self.hover_index: Optional[int] = None

    def wants_tab_focus(self) -> bool:
        return True

    def get_value(self) -> str:
        return self.options[self.selected_index]

    def draw(self, surface: pygame.Surface):
        # Main box
        pygame.draw.rect(surface, Colors.PANEL, self.rect, border_radius=4)
        outline_color = Colors.ACCENT if self.focused or self.open else Colors.OUTLINE
        pygame.draw.rect(surface, outline_color, self.rect, width=2, border_radius=4)

        txt_surf = self.font.render(
            self.options[self.selected_index], True, Colors.TEXT
        )
        surface.blit(
            txt_surf,
            (
                self.rect.x + 8,
                self.rect.y + (self.rect.height - txt_surf.get_height()) // 2,
            ),
        )

        # Dropdown arrow
        arrow = "▼" if not self.open else "▲"
        arrow_surf = self.font.render(arrow, True, Colors.TEXT_DIM)
        surface.blit(
            arrow_surf,
            (
                self.rect.right - arrow_surf.get_width() - 10,
                self.rect.y + (self.rect.height - arrow_surf.get_height()) // 2,
            ),
        )

        # Expanded options
        if self.open:
            option_rect = pygame.Rect(
                self.rect.x,
                self.rect.bottom,
                self.rect.width,
                DROPDOWN_OPTION_HEIGHT * len(self.options),
            )
            pygame.draw.rect(surface, Colors.PANEL, option_rect, border_radius=4)
            pygame.draw.rect(
                surface, Colors.OUTLINE, option_rect, width=2, border_radius=4
            )
            for i, opt in enumerate(self.options):
                row_rect = pygame.Rect(
                    option_rect.x,
                    option_rect.y + i * DROPDOWN_OPTION_HEIGHT,
                    option_rect.width,
                    DROPDOWN_OPTION_HEIGHT,
                )
                if i == self.hover_index:
                    pygame.draw.rect(surface, Colors.ACCENT_HOVER, row_rect)
                elif i == self.selected_index:
                    pygame.draw.rect(surface, Colors.ACCENT, row_rect, width=1)
                opt_surf = self.font.render(opt, True, Colors.TEXT)
                surface.blit(
                    opt_surf,
                    (
                        row_rect.x + 8,
                        row_rect.y + (row_rect.height - opt_surf.get_height()) // 2,
                    ),
                )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                self.focused = True
                return True
            if self.open:
                # Check options
                for i, _ in enumerate(self.options):
                    row_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * DROPDOWN_OPTION_HEIGHT,
                        self.rect.width,
                        DROPDOWN_OPTION_HEIGHT,
                    )
                    if row_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.open = False
                        return True
                # Click outside closes
                self.open = False
                self.focused = False
        elif event.type == pygame.MOUSEMOTION and self.open:
            self.hover_index = None
            for i, _ in enumerate(self.options):
                row_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * DROPDOWN_OPTION_HEIGHT,
                    self.rect.width,
                    DROPDOWN_OPTION_HEIGHT,
                )
                if row_rect.collidepoint(event.pos):
                    self.hover_index = i
                    break
        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.open = not self.open
                return True
            if event.key == pygame.K_ESCAPE:
                self.open = False
                self.focused = False
                return True
            if not self.open:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                    return True
                if event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                    return True
            else:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                    return True
                if event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                    return True
                if event.key == pygame.K_RETURN:
                    self.open = False
                    return True
        return False


# ----------------------------- Button Widget ----------------------------------


class Button(Widget):
    def __init__(self, font: pygame.font.Font, text: str):
        super().__init__()
        self.font = font
        self.text = text
        self.hover = False
        self.disabled = False
        self._clicked = False

    def draw(self, surface: pygame.Surface):
        bg = Colors.ACCENT if not self.disabled else Colors.DISABLED_BG
        if self.hover and not self.disabled:
            bg = Colors.ACCENT_HOVER
        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        label_color = (0, 0, 0) if not self.disabled else Colors.TEXT_DIM
        txt_surf = self.font.render(self.text, True, label_color)
        surface.blit(
            txt_surf,
            (
                self.rect.centerx - txt_surf.get_width() // 2,
                self.rect.centery - txt_surf.get_height() // 2,
            ),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._clicked = True
                return True
        return False

    def consume_click(self) -> bool:
        if self._clicked:
            self._clicked = False
            return True
        return False


# ----------------------------- Survey GUI (Pygame) ----------------------------


class SurveyGui:
    _WINDOW_TITLE = "Pre-Experiment Survey"
    _FILL_ALL_REQUIRED_FIELDS_TEXT = "Please fill all required fields to continue."
    _START_TEXT = "START"

    _FIELD_GROUP_PADDING = (0, 20)
    _START_END_PADDING_VERTICAL = 15
    _FILL_ALL_REQUIRED_FIELDS_TEXT_PADDING_HORIZONTAL = 25
    _FILL_ALL_REQUIRED_FIELDS_TEXT_PADDING_TOP = 5

    def __init__(self, *, field_config: Sequence[dict[str, Any]]) -> None:
        self._field_config = field_config
        # Map: field_key -> (widget, is_required)
        self._field_key_to_widget: dict[str, tuple[Widget, bool]] = {}
        self._allowed_field_types = {"text", "dropdown", "checkbox"}

        self._running = False
        self._completed = False
        self._closed = False

        # Pre-calculated after building
        self._widgets_in_focus_order: list[Widget] = []
        self._font: Optional[pygame.font.Font] = None
        self._font_small: Optional[pygame.font.Font] = None
        self._start_button: Optional[Button] = None

    # ------------------------- Public API -------------------------

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption(self._WINDOW_TITLE)

        self._font = pygame.font.SysFont("Arial", FONT_SIZE)
        self._font_small = pygame.font.SysFont("Arial", SMALL_FONT_SIZE)

        # Build UI (creates widgets & layout)
        total_height = self._build_layout_return_height()
        height = max(BASE_HEIGHT, total_height + 40)
        self._surface = pygame.display.set_mode((WINDOW_WIDTH, height))

        clock = pygame.time.Clock()
        self._running = True

        # Initial validation (may disable start)
        self._validate_required_fields()

        # Focus first focusable
        self._focus_first()

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    self._closed = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._running = False
                    self._closed = True
                else:
                    self._handle_event(event)

            self._draw()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

    def get_responses(self) -> dict[str, str | bool]:
        if not self._completed and not self._closed:
            # Equivalent to user never pressed START
            raise PreExperimentSurveyError("Survey not completed (START not pressed).")
        responses: dict[str, str | bool] = {}
        for key, (widget, is_required) in self._field_key_to_widget.items():
            if isinstance(widget, TextInput):
                value = widget.get_value().strip()
                if is_required and value == "":
                    raise PreExperimentSurveyError(
                        f"Required field '{key}' is not filled."
                    )
                responses[key] = value
            elif isinstance(widget, Dropdown):
                responses[key] = widget.get_value()
            elif isinstance(widget, Checkbox):
                responses[key] = widget.get_value()
            else:
                responses[key] = widget.get_value()
        return responses

    # ------------------------- Internal: Building UI -------------------------

    def _build_layout_return_height(self) -> int:
        assert self._font and self._font_small

        y = self._START_END_PADDING_VERTICAL
        x = PADDING_HORIZONTAL
        content_width = WINDOW_WIDTH - 2 * PADDING_HORIZONTAL
        line_spacing = self._FIELD_GROUP_PADDING[1]

        # Build each field
        for idx, cfg in enumerate(self._field_config):
            key, label, field_type = self._parse_field_config(cfg)
            is_first = idx == 0
            is_required = False
            label_display = label

            if field_type == "text":
                is_required = bool(cfg.get("required", False))
                if not isinstance(is_required, bool):
                    raise PreExperimentSurveyError(
                        "Field config 'required' must be a boolean."
                    )
                if is_required:
                    label_display = f"{label} *"
                label_surf = self._font_small.render(label_display, True, Colors.TEXT)
                self._surface = pygame.display.set_mode(
                    (WINDOW_WIDTH, BASE_HEIGHT)
                )  # temporary to render
                # Draw position placeholder
                self._field_key_to_widget[key] = (TextInput(self._font), is_required)
                widget = self._field_key_to_widget[key][0]
                # Label position
                y += 0 if is_first else 0
                widget_y = y + label_surf.get_height() + 4
                widget.set_position(x, widget_y, content_width, LINE_HEIGHT)
                y = widget.rect.bottom + line_spacing
            elif field_type == "dropdown":
                label_surf = self._font_small.render(label_display, True, Colors.TEXT)
                options_raw = cfg.get("options")
                if options_raw is None or not isinstance(options_raw, list):
                    raise PreExperimentSurveyError(
                        "Dropdown field must have a list of 'options'."
                    )
                options = cast(list[str], options_raw)
                if not options:
                    raise PreExperimentSurveyError(
                        "Dropdown field must have at least 1 option."
                    )
                dropdown = Dropdown(self._font, options)
                self._field_key_to_widget[key] = (dropdown, False)
                y += 0
                widget_y = y + label_surf.get_height() + 4
                dropdown.set_position(x, widget_y, content_width, LINE_HEIGHT)
                y = dropdown.rect.bottom + line_spacing
            elif field_type == "checkbox":
                checkbox = Checkbox(self._font_small, label_display)
                self._field_key_to_widget[key] = (checkbox, False)
                checkbox.set_position(x, y, content_width, LINE_HEIGHT)
                y = checkbox.rect.bottom + line_spacing
            else:
                raise PreExperimentSurveyError(f"Unsupported field type: {field_type}")

        # Start button
        start_btn_height = 46
        start_btn_width = 180
        self._start_button = Button(self._font, self._START_TEXT)
        start_x = x
        start_y = y
        self._start_button.set_position(
            start_x, start_y, start_btn_width, start_btn_height
        )
        y = self._start_button.rect.bottom

        # Validation message positioning (drawn dynamically)
        y += (
            self._FILL_ALL_REQUIRED_FIELDS_TEXT_PADDING_TOP
            + self._START_END_PADDING_VERTICAL
        )
        return y

    # ------------------------- Internal: Parsing -------------------------

    def _parse_field_config(
        self, field_config: dict[str, Any]
    ) -> tuple[str, str, FieldType]:
        key = field_config.get("key")
        if key is None:
            raise PreExperimentSurveyError("Field config must contain a 'key'.")
        key = str(key)
        if key in self._field_key_to_widget:
            raise PreExperimentSurveyError(f"Duplicate field key: {key}.")

        field_type = field_config.get("type")
        if field_type is None:
            raise PreExperimentSurveyError("Field config must contain a 'type'.")
        if field_type not in self._allowed_field_types:
            raise PreExperimentSurveyError(
                f"Unsupported field type: {field_type}. Supported types: {', '.join(self._allowed_field_types)}."
            )
        field_type = cast(FieldType, field_type)

        label = field_config.get("label")
        if label is None:
            raise PreExperimentSurveyError("Field config must contain a 'label'.")
        label = str(label)

        return key, label, field_type

    # ------------------------- Internal: Event Handling -------------------------

    def _handle_event(self, event: pygame.event.Event):
        assert self._start_button

        # Tab navigation
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self._cycle_focus(shift=pygame.key.get_mods() & pygame.KMOD_SHIFT)
            return

        # Dispatch to widgets
        consumed = False
        for widget, _ in self._field_key_to_widget.values():
            if widget.handle_event(event):
                consumed = True
                break

        if not consumed and self._start_button.handle_event(event):
            consumed = True

        # After any interaction, re-validate required fields
        if consumed:
            self._validate_required_fields()

        if self._start_button.consume_click():
            if not self._start_button.disabled:
                self._completed = True
                self._running = False

    def _cycle_focus(self, shift: bool = False):
        focusables = [
            w for (w, _) in self._field_key_to_widget.values() if w.wants_tab_focus()
        ]
        if not focusables:
            return
        # Determine current
        current_index = None
        for i, w in enumerate(focusables):
            if w.focused:
                current_index = i
                break
        if current_index is None:
            target = focusables[-1] if shift else focusables[0]
        else:
            if shift:
                target = focusables[(current_index - 1) % len(focusables)]
            else:
                target = focusables[(current_index + 1) % len(focusables)]
        for w in focusables:
            w.focused = False
        target.focused = True

    def _focus_first(self):
        for widget, _ in self._field_key_to_widget.values():
            if widget.wants_tab_focus():
                widget.focused = True
                return

    # ------------------------- Internal: Validation -------------------------

    def _validate_required_fields(self):
        assert self._start_button
        incomplete = False
        for widget, is_required in self._field_key_to_widget.values():
            if is_required and isinstance(widget, TextInput):
                if widget.get_value().strip() == "":
                    incomplete = True
                    break
        self._start_button.disabled = incomplete

    # ------------------------- Internal: Drawing -------------------------

    def _draw(self):
        assert self._font and self._font_small and self._start_button
        self._surface.fill(Colors.BG)

        # Draw labels & widgets
        for key, (widget, is_required) in self._field_key_to_widget.items():
            # Draw label for text / dropdown above widget
            if isinstance(widget, TextInput):
                label_text = ""
                for cfg in self._field_config:
                    if cfg["key"] == key:
                        label_text = cfg["label"]
                        if (
                            is_required
                            and cfg.get("type") == "text"
                            and cfg.get("required")
                        ):
                            label_text += " *"
                        break
                label_surf = self._font_small.render(label_text, True, Colors.TEXT)
                self._surface.blit(
                    label_surf,
                    (widget.rect.x, widget.rect.y - label_surf.get_height() - 4),
                )
            elif isinstance(widget, Dropdown):
                # Same approach
                label_text = ""
                for cfg in self._field_config:
                    if cfg["key"] == key:
                        label_text = cfg["label"]
                        break
                label_surf = self._font_small.render(label_text, True, Colors.TEXT)
                self._surface.blit(
                    label_surf,
                    (widget.rect.x, widget.rect.y - label_surf.get_height() - 4),
                )

            widget.draw(self._surface)

        # Start button
        self._start_button.draw(self._surface)

        # Validation message
        if self._start_button.disabled:
            msg_surf = self._font_small.render(
                self._FILL_ALL_REQUIRED_FIELDS_TEXT, True, Colors.ERROR
            )
            msg_x = self._start_button.rect.x
            msg_y = (
                self._start_button.rect.bottom
                + self._FILL_ALL_REQUIRED_FIELDS_TEXT_PADDING_TOP
            )
            self._surface.blit(msg_surf, (msg_x, msg_y))
