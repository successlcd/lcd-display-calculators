"""Command line: python -m lcdcalc <command> ...

Examples:
  python -m lcdcalc pclk 800 480                    # typical 1056 x 525 total, 60 Hz
  python -m lcdcalc pclk 1024 600 --htotal 1344 --vtotal 635 --bpp 24 --lanes 2
  python -m lcdcalc ram 800 480 --bpp 16 --buffers 2
  python -m lcdcalc size 7 1024 600
  python -m lcdcalc pitch 154.21 85.92 1024 600
"""

from __future__ import annotations

import argparse
import sys

from . import core


def _mhz(hz: float) -> str:
    return f"{hz / 1e6:.2f} MHz"


def _mbps(bps: float) -> str:
    return f"{bps / 1e6:.0f} Mbps" if bps < 1e9 else f"{bps / 1e9:.2f} Gbps"


def _size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1048576:.2f} MB ({n:,} bytes)"
    if n >= 1024:
        return f"{n / 1024:.1f} KB ({n:,} bytes)"
    return f"{n} bytes"


def cmd_pclk(a: argparse.Namespace) -> None:
    if a.htotal and a.vtotal:
        ht, vt = a.htotal, a.vtotal
    elif (a.width, a.height) in core.TYPICAL_TOTALS:
        ht, vt = core.TYPICAL_TOTALS[(a.width, a.height)]
        print(f"Using typical totals {ht} x {vt}; pass --htotal/--vtotal from your datasheet.")
    else:
        sys.exit("No typical timing for this resolution; pass --htotal and --vtotal.")
    pclk = core.pixel_clock_hz(ht, vt, a.refresh)
    print(f"Total timing:      {ht} x {vt} at {a.refresh:g} Hz")
    print(f"Pixel clock:       {_mhz(pclk)}")
    print(f"Parallel RGB:      {a.bpp} data lines at {_mhz(pclk)}")
    if a.bpp in (18, 24):
        pairs = core.lvds_data_pairs(a.bpp)
        print(f"LVDS single link:  {pairs} pairs + clock, {_mbps(core.lvds_bitrate_per_pair_bps(pclk))} per pair")
        print(f"LVDS dual link:    2 x {pairs} pairs, {_mbps(core.lvds_bitrate_per_pair_bps(pclk, True))} per pair")
    rate = core.mipi_dsi_lane_rate_bps(pclk, a.bpp, a.lanes, a.margin)
    print(f"MIPI DSI:          {_mbps(rate)} per lane on {a.lanes} lane(s), {a.margin:.0%} margin")
    print(f"SPI at {a.spi:g} MHz:   {core.spi_max_fps(a.spi * 1e6, a.width, a.height, a.bpp):.1f} fps max")


def cmd_ram(a: argparse.Namespace) -> None:
    frame = core.frame_bytes(a.width, a.height, a.bpp)
    print(f"One frame:         {_size(frame)}")
    print(f"{a.buffers} frame buffer(s): {_size(core.frame_buffer_bytes(a.width, a.height, a.bpp, a.buffers))}")
    draw = core.draw_buffer_bytes(a.width, a.height, a.bpp, a.fraction, 2)
    print(f"2 draw buffers of 1/{a.fraction} screen: {_size(draw)}")


def cmd_size(a: argparse.Namespace) -> None:
    w, h = core.active_area_mm(a.diagonal, a.width, a.height)
    print(f"Active area:       {w:.2f} x {h:.2f} mm (square pixels assumed)")
    print(f"Pixel pitch:       {w / a.width:.4f} mm")
    print(f"Pixel density:     {core.ppi(a.diagonal, a.width, a.height):.1f} PPI")


def cmd_pitch(a: argparse.Namespace) -> None:
    hp, vp = core.pixel_pitch_mm(a.active_width, a.active_height, a.width, a.height)
    k = core.aspect_correction(a.active_width, a.active_height, a.width, a.height)
    print(f"Pixel pitch:       {hp:.4f} x {vp:.4f} mm (H x V)")
    if abs(k - 1) < 0.01:
        print("Pixels are square to within 1 %.")
    else:
        print(f"Pixels are not square: scale vertical sizes by {k:.3f} to keep circles round.")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="lcdcalc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("pclk", help="pixel clock and interface bandwidth")
    s.add_argument("width", type=int)
    s.add_argument("height", type=int)
    s.add_argument("--refresh", type=float, default=60.0)
    s.add_argument("--htotal", type=int)
    s.add_argument("--vtotal", type=int)
    s.add_argument("--bpp", type=int, default=24)
    s.add_argument("--lanes", type=int, default=2)
    s.add_argument("--margin", type=float, default=0.2)
    s.add_argument("--spi", type=float, default=40.0, help="SPI clock in MHz")
    s.set_defaults(func=cmd_pclk)

    s = sub.add_parser("ram", help="frame buffer and draw buffer RAM")
    s.add_argument("width", type=int)
    s.add_argument("height", type=int)
    s.add_argument("--bpp", type=int, default=16)
    s.add_argument("--buffers", type=int, default=1)
    s.add_argument("--fraction", type=int, default=10)
    s.set_defaults(func=cmd_ram)

    s = sub.add_parser("size", help="active area and PPI from diagonal and resolution")
    s.add_argument("diagonal", type=float, help="inches")
    s.add_argument("width", type=int)
    s.add_argument("height", type=int)
    s.set_defaults(func=cmd_size)

    s = sub.add_parser("pitch", help="pixel pitch from a drawing's active area")
    s.add_argument("active_width", type=float, help="mm")
    s.add_argument("active_height", type=float, help="mm")
    s.add_argument("width", type=int)
    s.add_argument("height", type=int)
    s.set_defaults(func=cmd_pitch)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
