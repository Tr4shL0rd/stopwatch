from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Button, Header, Footer, Static


class TimeDisplay(Static):
    """A widget to display elapsed time"""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1/60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time:float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(Static):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)

        def start():
            time_display.start()
            self.add_class("started")

        def stop():
            time_display.stop()
            self.remove_class("started")

        def reset():
            time_display.reset()

        match button_id:
            case "start": start()
            case "stop": stop()
            case "reset": reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch"""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    """Textual app for managing stopwatches."""

    CSS_PATH = "style.css"
    BINDINGS = [
                    ("d", "toggle_dark", "Toggle dark mode"),
                    ("a", "add_stopwatch", "Add stopwatch"),
                    ("ctrl+r", "remove_all_stopwatches", "Removes all stopwatches"),
                    ("r", "remove_stopwatch", "Remove stopwatch"),
                    ("ctrl+e", "reset_all_stopwatches", "Resets all stopwatches"),
                    ("ctrl+q", "exit_app", "Exits the program")
                ]


    def compose(self) -> ComposeResult:
        """Creates child widgets for the app"""
        yield Header()
        yield Footer()
        yield Container(Stopwatch(),id="timers")

    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_all_stopwatches(self) -> None:
        """Removes all current stopwatches."""
        timers = self.query("Stopwatch")
        timers.remove()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()

    def action_reset_all_stopwatches(self) -> None:
        """Resets all current stopwatches"""
        timers = self.query("Stopwatch")
        for timer in timers:
            time_display = timer.query_one(TimeDisplay)
            time_display.reset()

    def action_toggle_dark(self) -> None:
        """Action to toggle dark mode"""
        self.dark = not self.dark

    def action_exit_app(self) -> None:
        """Exits app"""
        self.app.exit()

if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
