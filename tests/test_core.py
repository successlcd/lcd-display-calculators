import math

import pytest

import lcdcalc as lc


def test_pixel_clock_typical_totals():
    assert lc.pixel_clock_hz(525, 288, 60) == pytest.approx(9.072e6)
    assert lc.pixel_clock_hz(1056, 525, 60) == pytest.approx(33.264e6)
    assert lc.pixel_clock_hz(1344, 635, 60) == pytest.approx(51.2064e6)


def test_pixel_clock_from_timing_parts():
    t = lc.Timing(800, 480, hfp=210, hbp=26, hsync=20, vfp=22, vbp=13, vsync=10)
    assert (t.h_total, t.v_total) == (1056, 525)
    assert lc.pixel_clock_from_timing(t) == pytest.approx(33.264e6)


def test_lvds():
    pclk = 51.2064e6
    assert lc.lvds_bitrate_per_pair_bps(pclk) == pytest.approx(pclk * 7)
    assert lc.lvds_bitrate_per_pair_bps(pclk, dual_link=True) == pytest.approx(pclk * 3.5)
    assert lc.lvds_data_pairs(24) == 4
    assert lc.lvds_data_pairs(18) == 3
    with pytest.raises(ValueError):
        lc.lvds_data_pairs(16)


def test_mipi_dsi():
    pclk = 51.2064e6
    raw = pclk * 24 / 2
    assert lc.mipi_dsi_lane_rate_bps(pclk, 24, 2, margin=0) == pytest.approx(raw)
    assert lc.mipi_dsi_lane_rate_bps(pclk, 24, 2) == pytest.approx(raw * 1.2)


def test_spi_fps():
    # 240 x 320 x 16 bit = 1,228,800 bits per frame
    assert lc.spi_max_fps(40e6, 240, 320, 16) == pytest.approx(40e6 / 1_228_800)


def test_frame_buffers():
    assert lc.frame_bytes(480, 272, 16) == 261_120
    assert lc.frame_bytes(800, 480, 16) == 768_000
    assert lc.frame_bytes(1024, 600, 16) == 1_228_800
    assert lc.frame_buffer_bytes(800, 480, 16, 2) == 1_536_000
    assert lc.frame_bytes(128, 64, 1) == 1024
    assert lc.draw_buffer_bytes(320, 240, 16, fraction=10, count=2) == 30_720


def test_size_and_ppi():
    w, h = lc.active_area_mm(7, 800, 480)
    assert math.hypot(w, h) == pytest.approx(7 * 25.4)
    assert w / h == pytest.approx(800 / 480)
    assert lc.ppi(5, 800, 480) == pytest.approx(186.6, abs=0.1)
    assert lc.ppi(4.3, 480, 272) == pytest.approx(128.3, abs=0.1)


def test_non_square_pixels():
    # 7" 1024 x 600 panel, active area 154.21 x 85.92 mm from the module drawing
    hp, vp = lc.pixel_pitch_mm(154.21, 85.92, 1024, 600)
    assert hp == pytest.approx(0.1506, abs=1e-4)
    assert vp == pytest.approx(0.1432, abs=1e-4)
    assert lc.aspect_correction(154.21, 85.92, 1024, 600) == pytest.approx(1.052, abs=1e-3)


def test_bad_input():
    with pytest.raises(ValueError):
        lc.pixel_clock_hz(0, 525)
    with pytest.raises(ValueError):
        lc.ppi(-1, 800, 480)
