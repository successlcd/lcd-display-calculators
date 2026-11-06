# lcdcalc

Small Python helpers for the numbers you need when picking a TFT or LCD panel
and the host that drives it:

- pixel clock from resolution, blanking and refresh rate
- per-pair LVDS bit rate (single and dual link)
- per-lane MIPI DSI bit rate
- best-case SPI frame rate
- frame buffer and LVGL-style draw buffer RAM
- active area, pixel pitch and PPI, including panels whose pixels are not square

No dependencies. Python 3.8 or newer.

We wrote these for our own application engineering at
[SuccessLCD](https://successlcd.com/), where the same questions come up on
most projects: will this MCU have enough RAM, does this processor's DSI
output have the bandwidth, why is the gauge on a 1024 x 600 screen oval.
The same maths runs in the browser on our site if you would rather not
install anything:

- [Pixel clock and interface bandwidth calculator](https://successlcd.com/tft-display-pixel-clock-bandwidth-calculator/)
- [MCU display RAM and frame buffer calculator](https://successlcd.com/mcu-display-frame-buffer-ram-calculator/)
- [Screen size, active area and PPI calculator](https://successlcd.com/lcd-screen-size-active-area-ppi-calculator/)

## Install

```
pip install git+https://github.com/successlcd/lcd-display-calculators
```

or copy `lcdcalc/core.py` into your project. It is one file.

## Command line

```
$ python -m lcdcalc pclk 1024 600
Using typical totals 1344 x 635; pass --htotal/--vtotal from your datasheet.
Total timing:      1344 x 635 at 60 Hz
Pixel clock:       51.21 MHz
Parallel RGB:      24 data lines at 51.21 MHz
LVDS single link:  4 pairs + clock, 358 Mbps per pair
LVDS dual link:    2 x 4 pairs, 179 Mbps per pair
MIPI DSI:          737 Mbps per lane on 2 lane(s), 20% margin
SPI at 40 MHz:   2.7 fps max

$ python -m lcdcalc ram 800 480 --buffers 2
One frame:         750.0 KB (768,000 bytes)
2 frame buffer(s): 1.46 MB (1,536,000 bytes)
2 draw buffers of 1/10 screen: 150.0 KB (153,600 bytes)

$ python -m lcdcalc pitch 154.21 85.92 1024 600
Pixel pitch:       0.1506 x 0.1432 mm (H x V)
Pixels are not square: scale vertical sizes by 1.052 to keep circles round.
```

## In code

```python
import lcdcalc as lc

t = lc.Timing(800, 480, hfp=210, hbp=26, hsync=20, vfp=22, vbp=13, vsync=10)
pclk = lc.pixel_clock_from_timing(t, refresh_hz=60)    # 33.264 MHz
lc.lvds_bitrate_per_pair_bps(pclk)                     # 232.8 Mbps
lc.frame_buffer_bytes(800, 480, bits_per_pixel=16, buffers=2)   # 1,536,000
lc.ppi(5, 800, 480)                                    # 186.6
```

## Things that catch people out

**The blanking values matter.** Pixel clock is total pixels per line times total
lines times refresh rate, not just the active resolution. 800 x 480 at 60 Hz is
about 23 MHz if you forget blanking and about 33 MHz with typical timing. Take
the totals from your panel's datasheet; the `TYPICAL_TOTALS` table is only a
starting point.

**Pixels are not always square.** On one of our 7-inch 1024 x 600 modules, the
drawing gives an active area of 154.21 x 85.92 mm. That works out to 0.1506 mm
per pixel across and 0.1432 mm down, so a 300 x 300 pixel circle comes out about
5 % wider than it is tall. Run `pitch` with the numbers from your own drawing
before your UI designer draws round gauges.

**SPI numbers are a ceiling.** `spi_max_fps` assumes the bus sends pixels
non-stop. Commands, chip-select gaps and the CPU rendering the next frame all
cost time, so measure on hardware.

**DSI margin is a planning figure.** The 20 % default is a rough allowance for
blanking and packet overhead, nothing more. Use whatever your SoC vendor
recommends and check the lane rate against your D-PHY version.

## Tests

```
pip install pytest
pytest
```

## License

MIT. See [LICENSE](LICENSE).

Questions about a specific panel or interface are welcome as issues. If you
are working on a product and want a second opinion on display selection, our
engineers are at [successlcd.com/contact](https://successlcd.com/contact/).
