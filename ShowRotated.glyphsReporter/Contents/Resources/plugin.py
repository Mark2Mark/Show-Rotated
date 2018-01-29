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

from GlyphsApp import GSLayer
from GlyphsApp.plugins import *
from vanilla import *


class ShowRotated(ReporterPlugin):

	def settings(self):
		self.name = 'Show Rotated'
		self.color = 0.0, 0.5, 0.3, 0.3
		self.flipH = 0
		self.flipLabel = {
			0 : "Flip Horizonally",
			1 : "Unflip Horizonally"
			}

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
			{"view": self.sliderMenuView.group.getNSView()},
			{"name": self.flipLabel[0], "action": self.flipHorizontally },
		]
		###################################


		self.menuName = Glyphs.localize({'en': u'Rotated ☯', 'de': u'Rotiert ☯'})
		# self.generalContextMenus = [
		# 	{'name': Glyphs.localize({'en': u'Rotation:', 'de': u'Rotation:'}), 'action': self.setRotationAngle},
		# ]


	def sliderCallback(self, sender):
		self.RefreshView()


	def flipHorizontally(self, sender):
		try:
			self.flipH = not self.flipH
			self.generalContextMenus = [
		    	{"view": self.sliderMenuView.group.getNSView()},
		    	{"name": self.flipLabel[self.flipH], "action": self.flipHorizontally },
			]
		except: pass


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
		#print layer.mutableCopy()#.correctPathDirection() # WHY does it return an ORPHAN?
		Glyph = layer.parent
		#thisBezierPathWithComponent = self.bezierPathComp(layer.copyDecomposedLayer())
		thisBezierPathWithComponent = layer.completeBezierPath
		pathA = thisBezierPathWithComponent.copy()
		

		bounds = layer.bounds
		x = bounds.origin.x + 0.5 * bounds.size.width
		y = bounds.origin.y + 0.5 * bounds.size.height

		rotation = NSAffineTransform.transform()
		rotation.translateXBy_yBy_( x, y )
		rotation.rotateByDegrees_( self.sliderMenuView.group.slider.get() )
		rotation.translateXBy_yBy_( -x, -y )
		thisBezierPathWithComponent.transformUsingAffineTransform_( rotation )

		try:
			if self.flipH:
				flipH = NSAffineTransform.transform()
				flipH.translateXBy_yBy_( x, y )
				flipH.scaleXBy_yBy_( -1, 1 )
				flipH.translateXBy_yBy_( -x, -y )
				thisBezierPathWithComponent.transformUsingAffineTransform_( flipH )
		except: pass
		
		if thisBezierPathWithComponent:
			thisBezierPathWithComponent.fill()
	
			'''
			vLayer = GSLayer.alloc().init()
			vLayer.addPath_(thisBezierPathWithComponent)
			#print vLayer.paths#.correctPathDirection()
			((x1, y1), (w1, h1)) = thisBezierPathWithComponent.controlPointBounds()
			((x2, y2), (w2, h2)) = layer.completeBezierPath.controlPointBounds()
			if int(x1) == int(x2):
				self.color = 0.8, 0.5, 0.3, 0.3
			else: 
				self.color = 0.0, 0.5, 0.3, 0.3
			'''

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


	def RefreshView(self):
		try:
			Glyphs = NSApplication.sharedApplication()
			currentTabView = Glyphs.font.currentTab
			if currentTabView:
				currentTabView.graphicView().setNeedsDisplay_(True)
		except:
			pass


	def background(self, layer):  # def foreground(self, layer):
		NSColor.colorWithCalibratedRed_green_blue_alpha_( *self.color ).set()
		self.drawRotated( layer )

