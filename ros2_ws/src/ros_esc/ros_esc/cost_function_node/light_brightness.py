"""Nominal percentage brightness for the existing simulated light model."""

import math


FULL_BRIGHTNESS_LUMENS = 1600.0


def brightness_percent_to_lumens(value):
    """Convert a finite 0..100 setting using the nominal linear bulb model."""
    if isinstance(value, bool):
        raise ValueError('brightness_percent must be a number from 0 to 100')
    try:
        percent = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            'brightness_percent must be a number from 0 to 100'
        ) from exc
    if not math.isfinite(percent) or not 0.0 <= percent <= 100.0:
        raise ValueError('brightness_percent must be finite and from 0 to 100')
    return percent * (FULL_BRIGHTNESS_LUMENS / 100.0)


def optional_brightness_percent(value):
    """Parse CLI percentages; 'legacy' retains old lumen flags/defaults."""
    if value is None or value == 'legacy':
        return None
    brightness_percent_to_lumens(value)
    return float(value)


def source_intensity_lumens(source):
    """Resolve one JSON source, rejecting conflicting brightness units."""
    percent = source.get('brightness_percent')
    lumens = source.get('intensity_lumens')
    if percent is not None:
        if lumens is not None:
            raise ValueError(
                'specify brightness_percent or intensity_lumens, not both'
            )
        return brightness_percent_to_lumens(percent)
    if lumens is None:
        raise ValueError('light source requires brightness_percent')
    return float(lumens)


def add_brightness_arguments(parser):
    """Add the same optional percentage flags to sensor and plotter CLIs."""
    for index in range(1, 6):
        parser.add_argument(
            f'--light_source_{index}_brightness_percent',
            type=optional_brightness_percent,
            default=None,
            help='0..100 brightness (100 = nominal 1600 lm); '
                 'overrides the legacy lumen setting for this light',
        )


def light_sources_from_arguments(args):
    """Resolve per-light CLI precedence identically for sensing and plots."""
    sources = []
    for index in range(1, 6):
        percent = optional_brightness_percent(getattr(
            args, f'light_source_{index}_brightness_percent', None
        ))
        source = {
            'x': getattr(args, f'light_source_{index}_x', None),
            'y': getattr(args, f'light_source_{index}_y', None),
            'intensity_lumens': getattr(
                args, f'light_source_{index}_intensity_lumens', None
            ) if percent is None else None,
        }
        if percent is not None:
            source['brightness_percent'] = percent
        sources.append(source)
    return sources
