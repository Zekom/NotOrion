import pyglet

class CursorLabel(object):
	batch = pyglet.graphics.Batch()

	def __init__(self, marker_color):
		self.visible = False
		self.pyglet_label= pyglet.text.Label(
			"",
			x=0,
			y=0,
			anchor_x='center',
			anchor_y='bottom',
			color=(marker_color[0], marker_color[1], marker_color[2], 255),
			font_size=10,
			batch=CursorLabel.batch
		)
		# shaded masking box behind cursor label, to make text easier to read
		self.mask_vertext_list = pyglet.graphics.vertex_list( 4,
			'v2f',
			('c4B/static', (
				0, 0, 0, 200,
				0, 0, 0, 200,
				0, 0, 0, 200,
				0, 0, 0, 200,
				)
			)
		)
