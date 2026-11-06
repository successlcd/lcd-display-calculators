"""Small, dependency-free calculators for TFT and LCD display planning.

Every function returns plain numbers so the results can be used in scripts,
spreadsheets or tests. Units are in the function names: _hz, _bps, _bytes,
_mm, _in.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Common total timings (active + blanking) at 60 Hz. These are typical values;
# always check the timing table in your panel's datasheet.
TYPICAL_TOTALS = {
    (480, 272): (525, 288),
    (800, 480): (1056, 525),
    (1024, 600): (1344, 635),
}


@dataclass(frozen=True)
class Timing:
    """Horizontal and vertical timing in pixels / lines."""

    width: int
    height: int
    hfp: int = 0
    hbp: int = 0
    hsync: int = 0
    vfp: int = 0
    vbp: int = 0
    vsync: int = 0

    @property
    def h_total(self) -> int:
        return self.width + self.hfp + self.hbp + self.hsync

    @property
    def v_total(self) -> int:
        return self.height + self.vfp + self.vbp + self.vsync


def pixel_clock_hz(h_total: int, v_total: int, refresh_hz: float = 60.0) -> float:
    """Pixel clock = total pixels per line x total lines x refresh rate."""
    _positive(h_total=h_total, v_total=v_total, refresh_hz=refresh_hz)
    return h_total * v_total * refresh_hz


def pixel_clock_from_timing(timing: Timing, refresh_hz: float = 60.0) -> float:
    return pixel_clock_hz(timing.h_total, timing.v_total, refresh_hz)


def lvds_bitrate_per_pair_bps(pixel_clock: float, dual_link: bool = False) -> float:
    """Serial bit rate on each LVDS data pair (7 bits per clock).

    In a dual-link (odd/even) interface each link runs at half the pixel clock.
    """
    clock = pixel_clock / 2 if dual_link else pixel_clock
    return clock * 7


def lvds_data_pairs(bits_per_pixel: int) -> int:
    """3 data pairs for 18-bit (6-bit per colour), 4 pairs for 24-bit."""
    if bits_per_pixel not in (18, 24):
        raise ValueError("LVDS panels are usually 18-bit or 24-bit")
    return 3 if bits_per_pixel == 18 else 4


def mipi_dsi_lane_rate_bps(
    pixel_clock: float, bits_per_pixel: int, lanes: int, margin: float = 0.2
) -> float:
    """Per-lane bit rate needed for MIPI DSI video mode.

    Raw rate = pixel clock x bits per pixel / lanes. ``margin`` adds headroom
    for blanking and protocol overhead (0.2 = 20 %); use the figure your
    host's DSI documentation recommends.
    """
    _positive(pixel_clock=pixel_clock, bits_per_pixel=bits_per_pixel, lanes=lanes)
    if margin < 0:
        raise ValueError("margin must be >= 0")
    return pixel_clock * bits_per_pixel / lanes * (1 + margin)


def spi_max_fps(spi_clock_hz: float, width: int, height: int, bits_per_pixel: int = 16) -> float:
    """Upper bound on full-screen frames per second over a single SPI data line.

    Ignores command overhead and gaps between transfers, so real numbers are lower.
    """
    _positive(spi_clock_hz=spi_clock_hz, width=width, height=height, bits_per_pixel=bits_per_pixel)
    return spi_clock_hz / (width * height * bits_per_pixel)


def frame_bytes(width: int, height: int, bits_per_pixel: int = 16) -> int:
    """Bytes for one full frame, rounded up to whole bytes."""
    _positive(width=width, height=height, bits_per_pixel=bits_per_pixel)
    return math.ceil(width * height * bits_per_pixel / 8)


def frame_buffer_bytes(width: int, height: int, bits_per_pixel: int = 16, buffers: int = 1) -> int:
    """RAM for ``buffers`` full frame buffers (2 = double buffering)."""
    if buffers < 0:
        raise ValueError("buffers must be >= 0")
    return frame_bytes(width, height, bits_per_pixel) * buffers


def draw_buffer_bytes(
    width: int, height: int, bits_per_pixel: int = 16, fraction: int = 10, count: int = 2
) -> int:
    """Partial draw buffers, as graphics libraries such as LVGL use.

    ``fraction`` = 10 means each buffer holds 1/10 of the screen.
    Useful for SPI or MCU-interface panels that keep their own display RAM.
    """
    _positive(fraction=fraction)
    if count < 0:
        raise ValueError("count must be >= 0")
    return math.ceil(frame_bytes(width, height, bits_per_pixel) / fraction) * count


def active_area_mm(diagonal_in: float, width_px: int, height_px: int) -> tuple[float, float]:
    """Active-area width and height from the diagonal, assuming square pixels."""
    _positive(diagonal_in=diagonal_in, width_px=width_px, height_px=height_px)
    diag_px = math.hypot(width_px, height_px)
    diag_mm = diagonal_in * 25.4
    return diag_mm * width_px / diag_px, diag_mm * height_px / diag_px


def ppi(diagonal_in: float, width_px: int, height_px: int) -> float:
    """Pixels per inch along the diagonal, assuming square pixels."""
    _positive(diagonal_in=diagonal_in, width_px=width_px, height_px=height_px)
    return math.hypot(width_px, height_px) / diagonal_in


def pixel_pitch_mm(
    active_width_mm: float, active_height_mm: float, width_px: int, height_px: int
) -> tuple[float, float]:
    """Horizontal and vertical pixel pitch from a drawing's active area.

    Many panels do not have square pixels; compare the two values before
    drawing circles or icons.
    """
    _positive(
        active_width_mm=active_width_mm,
        active_height_mm=active_height_mm,
        width_px=width_px,
        height_px=height_px,
    )
    return active_width_mm / width_px, active_height_mm / height_px


def aspect_correction(active_width_mm: float, active_height_mm: float, width_px: int, height_px: int) -> float:
    """Factor to multiply vertical pixel sizes by so shapes look round.

    > 1 means pixels are wider than tall (draw shapes taller in pixels).
    """
    h_pitch, v_pitch = pixel_pitch_mm(active_width_mm, active_height_mm, width_px, height_px)
    return h_pitch / v_pitch


def _positive(**values: float) -> None:
    for name, value in values.items():
        if not value or value <= 0:
            raise ValueError(f"{name} must be > 0")
