# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

### New names: Carroussel, ... (?)

from GlyphsApp.plugins import *
from vanilla import *

class ShowRotated(ReporterPlugin):

	def settings(self):

		###################################
		## Rotation Slider for Context Menu:
		self.name = 'Show Rotated'

		# Create Vanilla window and group with controls
		viewWidth = 150
		viewHeight = 70
		self.sliderMenuView = Window((viewWidth, viewHeight))
		self.sliderMenuView.group = Group((0, 0, viewWidth, viewHeight)) # (0, 0, viewWidth, viewHeight)
		self.sliderMenuView.group.line = HorizontalLine((10, 10, -10, 1))
		self.sliderMenuView.group.text = TextBox((10, 20, -10, -10), self.name)
		self.sliderMenuView.group.slider = Slider((10, 38, -10, 23),
                            tickMarkCount = 17,
                            maxValue = 360,
                            stopOnTickMarks = True,
                            continuous = True,
                            callback=self.sliderCallback)
		self.sliderMenuView.group.slider.set(180)

		## Define the menu
		self.generalContextMenus = [
		    {"view": self.sliderMenuView.group.getNSView()}
		]
		###################################


		self.menuName = Glyphs.localize({'en': u'* Rotated', 'de': u'* Rotiert'}) #  ☯
		# self.generalContextMenus = [
		# 	{'name': Glyphs.localize({'en': u'Rotation:', 'de': u'Rotation:'}), 'action': self.setRotationAngle},
		# ]


		

	def background(self, layer):  # def foreground(self, layer):
		NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.0, 0.5, 0.3, 0.3 ).set()
		self.drawRotated( layer )

	# def inactiveLayers(self, layer):
	# 	pass

	def rotationTransform( self, angle, center ):
		try:
			rotation = NSAffineTransform.transform()
			rotation.translateXBy_yBy_( center.x, center.y )
			rotation.rotateByDegrees_( angle )
			rotation.translateXBy_yBy_( -center.x, -center.y )
			return rotation
		except Exception as e:
			self.logToConsole( "rotationTransform: %s" % str(e) )

	def bezierPathComp( self, thisPath ):
		"""Compatibility method for bezierPath before v2.3."""
		try:
			return thisPath.bezierPath() # until v2.2
		except Exception as e:
			return thisPath.bezierPath # v2.3+

	def drawRotated( self, layer ):

		# self.logToConsole( "Here is my log" )

		Glyph = layer.parent
		thisBezierPathWithComponent = self.bezierPathComp(layer.copyDecomposedLayer())
		pathA = thisBezierPathWithComponent.copy()

		bounds = layer.bounds
		x = bounds.origin.x + 0.5 * bounds.size.width
		y = bounds.origin.y + 0.5 * bounds.size.height

		rotation = NSAffineTransform.transform()
		rotation.translateXBy_yBy_( x, y )

		# if NSUserDefaults.standardUserDefaults().floatForKey_("TransformRotate") != 0:
		# 	thisRotation = NSUserDefaults.standardUserDefaults().floatForKey_("TransformRotate")
		# else:
		# 	thisRotation = 180
		# rotation.rotateByDegrees_( thisRotation )
		# rotation.translateXBy_yBy_( -x, -y )

		rotation.rotateByDegrees_( self.sliderMenuView.group.slider.get() )
		rotation.translateXBy_yBy_( -x, -y )		

		thisBezierPathWithComponent.transformUsingAffineTransform_( rotation )
		
		if thisBezierPathWithComponent:
			thisBezierPathWithComponent.fill()

		## UNDER CONSTRUCTION:
		## HIGHTLIGHT IF BOTH PATHS PERFECTLY MATCH
		# pathAStringRepresentation = "%s" % pathA.CGPath
		# thisBezierPathWithComponentStringRepresentation = "%s" % thisBezierPathWithComponent.CGPath
		# AAA = '\n'.join(pathAStringRepresentation.split('\n')[1:])
		# BBB = '\n'.join(thisBezierPathWithComponentStringRepresentation.split('\n')[1:])
		# print AAA
		# print BBB
		# if AAA == BBB:
		# 	print "match"




	def setRotationAngle(self):
		pass
		# print 'Just did something'


	# def conditionalContextMenus(self):

	# 	# Empty list of context menu items
	# 	contextMenus = []

	# 	# Execute only if layers are actually selected
	# 	if Glyphs.font.selectedLayers:
	# 		layer = Glyphs.font.selectedLayers[0]
			
	# 		# Exactly one object is selected and it’s an anchor
	# 		if len(layer.selection) == 1 and type(layer.selection[0]) == GSAnchor:
					
	# 			# Add context menu item
	# 			contextMenus.append({'name': Glyphs.localize({'en': u'Do something else', 'de': u'Tu etwas anderes'}), 'action': self.doSomethingElse})

	# 	# Return list of context menu items
	# 	return contextMenus

	# def doSomethingElse(self):
	# 	print 'Just did something else'


	def RefreshView(self):
		try:
			Glyphs = NSApplication.sharedApplication()
			currentTabView = Glyphs.font.currentTab
			if currentTabView:
				currentTabView.graphicView().setNeedsDisplay_(True)
		except:
			pass

	# Prints the slider’s value
	def sliderCallback(self, sender):
		# print 'Slider value:', sender.get()
		self.RefreshView()
