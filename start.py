import sys
from MainWindow import App

def main(args):
	global app
	app = App(args)
	app.exec_()
	
	
if __name__ == "__main__":
	main(sys.argv)