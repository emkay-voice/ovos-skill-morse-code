"""The code on a screen (issue #5): dots and dashes with the letters underneath."""
import base64
import re
from unittest.mock import MagicMock

import morse_skill


def _svg(uri):
    head, payload = uri.split(",", 1)
    assert head == "data:image/svg+xml;base64"
    return base64.b64decode(payload).decode("utf-8")


def _shapes(svg):
    """'.' per circle and '-' per bar, in drawing order."""
    return "".join("." if s == "circle" else "-" for s in re.findall(r"<(circle|rect)\b", svg))


def _viewbox_side(svg):
    w, h = re.search(r'viewBox="0 0 (\S+) (\S+)"', svg).groups()
    assert w == h
    return float(w)


def test_tile_draws_the_pattern():
    assert _shapes(_svg(morse_skill.morse_tile("-.-."))) == "-.-."


def test_tile_fits_five_dashes():
    svg = _svg(morse_skill.morse_tile("-----"))
    side = _viewbox_side(svg)
    xs = [float(x) for x in re.findall(r'<rect x="([\d.]+)"', svg)]
    assert xs[0] > 0 and xs[-1] + morse_skill._DASH_W < side


def test_intent_shows_a_tile_per_character(skill):
    skill.play_audio = MagicMock()
    message = MagicMock()
    message.data = {"text": "sos 1"}
    skill.handle_play_morse(message)

    data = dict(c.args for c in skill.gui.__setitem__.call_args_list)
    assert data["title"] == "sos 1"
    assert [i["title"] for i in data["items"]] == ["S", "O", "S", "1"]
    assert [_shapes(_svg(i["image"])) for i in data["items"]] == ["...", "---", "...", ".----"]
    skill.gui.show_page.assert_called_once_with("SYSTEM_grid", override_idle=morse_skill.SCREEN_SECONDS)


def test_nothing_encodable_shows_nothing(skill):
    skill.speak_dialog = MagicMock()
    skill.play_audio = MagicMock()
    message = MagicMock()
    message.data = {"text": "!!!"}
    skill.handle_play_morse(message)
    skill.gui.show_page.assert_not_called()


def test_sheet_has_every_letter_and_its_code():
    svg = _svg(morse_skill.morse_sheet("hi there"))
    assert re.findall(r">([A-Z0-9])</text>", svg) == list("HITHERE")
    assert _shapes(svg) == "".join(morse_skill.MORSE_CODE[c] for c in "hithere")


def test_sheet_stays_inside_the_round_cover():
    """Every shape lies within the circle a round cover is cut to."""
    svg = _svg(morse_skill.morse_sheet("hello world"))
    side = _viewbox_side(svg)
    r = side / 2
    points = [(float(x), float(y)) for x, y in re.findall(r'cx="([\d.]+)" cy="([\d.]+)"', svg)]
    points += [(float(x) + morse_skill._DASH_W, float(y))
               for x, y in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)"', svg)]
    points += [(float(x), float(y)) for x, y in re.findall(r'<text x="([\d.]+)" y="([\d.]+)"', svg)]
    assert all((x - r) ** 2 + (y - r) ** 2 < r ** 2 for x, y in points)


def test_ocp_result_carries_the_sheet(skill):
    skill.voc_list = MagicMock(return_value=["in morse"])
    [entry] = skill.search_morse("sos in morse")
    assert _shapes(_svg(entry.image)) == "...---..."
