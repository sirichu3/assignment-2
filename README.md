# Sunrise and Sunset Visualization Program

## Project Overview
This is a Python program for visualizing the changes in sunrise, transit (solar noon), and sunset times throughout the year. It displays these changes through an animated interface and provides interactive timeline navigation.

## Features

1. **Animated Display**: Dynamically showcases sunrise and sunset time changes at a speed of 5 days per second.
2. **Interactive Timeline**: Click on the timeline to quickly jump to a specific date.
3. **Hover Pause**: Animation pauses when hovering over the timeline and resumes when the mouse moves away.
4. **Visual Markers**:
   - Displays markers for 00:00, 12:00, and 24:00 each day.
   - Adds horizontal marker lines for sunrise, transit, and sunset for the current day.
5. **Gradient Display**: The current day's curve is the most opaque, with curves for dates further away having higher transparency.
6. **Layered Display**: The current day's curve is rendered on the top layer, with closer dates having higher layer precedence.
7. **Background Color Transition**: Automatically adjusts the background color based on seasonal changes.
8. **Information Display**: Shows the current date, sunrise time, transit time, and sunset time.

## Installation Dependencies

```bash
pip install matplotlib pandas numpy
```

## Usage Instructions

1. Ensure all required dependency packages are installed.
2. Place the `Sun_rise_set_2024.csv` data file in the same directory as the program.
3. Run the main program:

```bash
python sun_rise_set.py
```

## Interaction Guide

- **Play/Pause**: Click anywhere on the chart to toggle between playing and pausing the animation.
- **Quick Jump**: Click any position on the timeline to jump to the corresponding date.
- **Hover to View**: Hover over the timeline to pause the animation and view detailed information for a specific date.
- **Exit Program**: Close the window to exit the program.

## File Description

- `sun_rise_set.py`: The main program file containing the visualization and interaction logic.
- `Sun_rise_set_2024.csv`: A CSV file containing sunrise and sunset time data for the year 2024.

## Data Format Requirements

The CSV file should include the following columns:
- `Date`: Date (format: YYYY-MM-DD)
- `Dayofyear`: Day of the year
- `RISE`: Sunrise time (format: HH:MM)
- `RISE_min`: Sunrise time in minutes (0-1440)
- `TRAN.`: Solar noon time (format: HH:MM)
- `TRAN_min`: Solar noon time in minutes (0-1440)
- `SET`: Sunset time (format: HH:MM)
- `SET_min`: Sunset time in minutes (0-1440)

## Notes

- Ensure the `Sun_rise_set_2024.csv` file exists and is correctly formatted before running the program.
- For the best visual experience, run the program on a large screen.
- If the animation runs sluggishly, try reducing the chart window size.
- The program uses Matplotlib's animation functionality, which may perform slightly differently across various operating systems.
- If you click on a position on the timeline between two days, there may be an issue where the animation does not automatically resume after moving the mouse away. To resolve this, simply click on a specific day on the timeline again, and then move the mouse away; the animation will resume playing automatically.