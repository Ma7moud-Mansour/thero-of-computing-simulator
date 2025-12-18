from PySide6.QtCore import QTimer

def glow_state(state_item):
    # Highlight state
    state_item.setOpacity(1.0)

    timer = QTimer()
    timer.setSingleShot(True)

    def fade():
        state_item.setOpacity(0.6)

    timer.timeout.connect(fade)
    timer.start(400)

    # prevent garbage collection
    state_item._glow_timer = timer
