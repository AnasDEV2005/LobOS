#!/bin/sh

# Set notification options
NOTIFY_ID=1
NOTIFY_TIMEOUT=2000  # 5 seconds
NOTIFY_MESSAGE="kek lolololo"

# Check if launched from terminal, keybinding, or rofi
if [[ -n $(tty | grep "^/dev/pts") ]]; then
  # Launched from terminal
  NOTIFY_MESSAGE="Test notificationnnnnnn !! wawawa"

fi


# Send notification using notify
notify-send "$NOTIFY_MESSAGE: $NOTIFICATION_TEXT"

