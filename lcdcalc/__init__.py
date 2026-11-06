"""lcdcalc: pixel clock, bandwidth, frame buffer and pixel pitch math for TFT/LCD displays."""

from .core import (
    TYPICAL_TOTALS,
    Timing,
    active_area_mm,
    aspect_correction,
    draw_buffer_bytes,
    frame_buffer_bytes,
    frame_bytes,
    lvds_bitrate_per_pair_bps,
    lvds_data_pairs,
    mipi_dsi_lane_rate_bps,
    pixel_clock_from_timing,
    pixel_clock_hz,
    pixel_pitch_mm,
    ppi,
    spi_max_fps,
)

__version__ = "0.1.0"

__all__ = [
    "TYPICAL_TOTALS",
    "Timing",
    "active_area_mm",
    "aspect_correction",
    "draw_buffer_bytes",
    "frame_buffer_bytes",
    "frame_bytes",
    "lvds_bitrate_per_pair_bps",
    "lvds_data_pairs",
    "mipi_dsi_lane_rate_bps",
    "pixel_clock_from_timing",
    "pixel_clock_hz",
    "pixel_pitch_mm",
    "ppi",
    "spi_max_fps",
]
