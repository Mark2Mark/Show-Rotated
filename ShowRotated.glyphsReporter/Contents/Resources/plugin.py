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
		self.thisMenuTitle = {"name": u"%s:" % self.name, "action": None }
		self.color = 0.0, 0.5, 0.3, 0.3
		self.flipH = 0


		# Create Vanilla window and group with controls
		viewWidth = 170
		viewHeight = 28 + 25 + 25
		self.sliderMenuView = Window((viewWidth, viewHeight))
		self.sliderMenuView.group = Group((0, 0, viewWidth, viewHeight)) # (0, 0, viewWidth, viewHeight)
		self.sliderMenuView.group.slider = Slider((20, 0, -1, 25),
							tickMarkCount = 17,
							maxValue = 360,
							stopOnTickMarks = True,
							continuous = True,
							callback=self.sliderCallback)
		self.sliderMenuView.group.slider.set(180)
		self.sliderMenuView.group.checkboxH = CheckBox((20, 28, -1, 25), "Flip Horizontally", callback=self.RefreshView)
		self.sliderMenuView.group.checkboxV = CheckBox((20, 48, -1, 25), "Flip Vertically", callback=self.RefreshView)

		## Define the menu
		self.generalContextMenus = [
			self.thisMenuTitle,
			{"view": self.sliderMenuView.group.getNSView()},
		]
		###################################

		self.menuName = Glyphs.localize({'en': u'Rotated ☯', 'de': u'Rotiert ☯'})


	def sliderCallback(self, sender):
		self.RefreshView(sender)


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
			if self.sliderMenuView.group.checkboxH.get() == True:
				flipH = NSAffineTransform.transform()
				flipH.translateXBy_yBy_( x, y )
				flipH.scaleXBy_yBy_( -1, 1 )
				flipH.translateXBy_yBy_( -x, -y )
				thisBezierPathWithComponent.transformUsingAffineTransform_( flipH )
			if self.sliderMenuView.group.checkboxV.get() == True:
				flipV = NSAffineTransform.transform()
				flipV.translateXBy_yBy_( x, y )
				flipV.scaleXBy_yBy_( 1, -1 )
				flipV.translateXBy_yBy_( -x, -y )
				thisBezierPathWithComponent.transformUsingAffineTransform_( flipV )

		except: pass
		
		if thisBezierPathWithComponent:
			thisBezierPathWithComponent.fill()
	

	def setRotationAngle(self):
		pass


	def RefreshView(self, sender):
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

