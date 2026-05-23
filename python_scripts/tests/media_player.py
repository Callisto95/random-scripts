import sys

from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QApplication, QGridLayout, QWidget


class MediaPlayer(QWidget):
	def __init__(self, video_file: str):
		super().__init__()
		
		self.resize(800, 800)
		
		self.media = QMediaPlayer()
		self.audio = QAudioOutput()
		self.video = QVideoWidget()
		
		self.media.setVideoOutput(self.video)
		self.media.setAudioOutput(self.audio)
		
		self.layout = QGridLayout()
		self.layout.addWidget(self.video)
		
		self.setLayout(self.layout)
		
		self.media.setSource(video_file)
		self.media.play()
		
		self.media.setLoops(5000)
		

if __name__ == '__main__':
	app = QApplication([])
	w = MediaPlayer(sys.argv[1])
	w.show()
	sys.exit(app.exec())
