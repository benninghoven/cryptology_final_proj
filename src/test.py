import curses


def main(stdscr):
    stdscr.clear()

    # Turn off cursor blinking
    #curses.curs_set(0)

    height, width = stdscr.getmaxyx()

    x = width // 2
    y = height // 2

    # Display a message in the center of the screen
    stdscr.addstr(y, x - 10, "Hello, Curses!", curses.A_BOLD)

    # Refresh the screen to see the changes
    stdscr.refresh()

    # Wait for a key press
    stdscr.getch()


curses.wrapper(main)
