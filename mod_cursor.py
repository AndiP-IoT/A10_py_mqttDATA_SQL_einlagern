# https://stackoverflow.com/questions/46651602/determine-the-terminal-cursor-position-with-an-ansi-sequence-in-python-3/46675451#46675451
# https://stackoverflow.com/questions/8343250/how-can-i-get-position-of-cursor-in-terminal
import os, re, sys, termios, tty

def getcursorpos():
	buf = ""
	stdin = sys.stdin.fileno()
	tattr = termios.tcgetattr(stdin)

	try:
		tty.setcbreak(stdin, termios.TCSANOW)
		sys.stdout.write("\x1b[6n")
		sys.stdout.flush()

		while True:
			buf += sys.stdin.read(1)
			if buf[-1] == "R":
				break

	finally:
		termios.tcsetattr(stdin, termios.TCSANOW, tattr)

	# reading the actual values, but what if a keystroke appears while reading
	# from stdin? As dirty work around, getpos() returns if this fails: None
	try:
		matches = re.match(r"^\x1b\[(\d*);(\d*)R", buf)
		groups = matches.groups()
	except AttributeError:
		return None

	return (int(groups[0]), int(groups[1]))
