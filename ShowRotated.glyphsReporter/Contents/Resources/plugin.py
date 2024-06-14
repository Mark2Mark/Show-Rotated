# encoding: utf-8

###########################################################################################################
#
#
# 	Reporter Plugin
#
# 	Read the docs:
# 	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

from GlyphsApp import GSLayer, GSPath
from GlyphsApp.plugins import *
from vanilla import Window, Slider, Group, CheckBox
from AppKit import (
    NSBezierPath,
    NSMaxX,
    NSMidX,
    NSMinX,
    NSMaxY,
    NSMidY,
    NSMinY,
    NSHeight,
    NSWidth,
    NSGradient,
    NSColor,
    NSMakeRect,
    NSZeroRect,
    NSUserDefaults,
)
import traceback

# Changelog
# NEW:
# 	+ Add Selection Mode: draw only selected paths
# 	+ Add Mirror axis if Flipped V/H is active
# 	+ Add Center of Rotation


class ShowRotated(ReporterPlugin):
    @objc.python_method
    def settings(self):
        self.name = "Rotated"
        self.menu_title = {"name": "%s:" % self.name, "action": None}
        self.color = 0.0, 0.5, 0.3, 0.3
        self.flip_h_transform = 0

        # Create Vanilla window and group with controls
        view_width = 170
        view_height = 28 + 25 + 25 + 25
        self.slider_menu_view = Window((view_width, view_height))
        self.slider_menu_view.group = Group((0, 0, view_width, view_height))
        self.slider_menu_view.group.slider = Slider(
            (20, 0, -1, 25),
            tickMarkCount=17,
            maxValue=360,
            stopOnTickMarks=True,
            continuous=True,
            callback=self.update,
        )
        self.slider_menu_view.group.slider.set(180)

        self.slider_menu_view.group.horizontal = CheckBox(
            (20, 28, -1, 25), "Flip Horizontally", callback=self.update
        )
        self.slider_menu_view.group.vertical = CheckBox(
            (20, 48, -1, 25), "Flip Vertically", callback=self.update
        )
        self.slider_menu_view.group.checkbox_selection_mode = CheckBox(
            (20, 68, -1, 25), "Rotate Selection", callback=self.update
        )

        self.generalContextMenus = [
            self.menu_title,
            {"view": self.slider_menu_view.group.getNSView()},
        ]
        ###################################

        self.menuName = Glyphs.localize({"en": "Rotated", "de": "Rotiert"})

    @objc.python_method
    def rotation_transform(self, angle, center):
        try:
            rotation = NSAffineTransform.transform()
            rotation.translateXBy_yBy_(center.x, center.y)
            rotation.rotateByDegrees_(angle)
            rotation.translateXBy_yBy_(-center.x, -center.y)
            return rotation
        except Exception as e:
            self.logToConsole("rotation_transform: %s" % str(e))

    @objc.python_method
    def rotation(self, x, y, angle):
        rotation = NSAffineTransform.transform()
        rotation.translateXBy_yBy_(x, y)
        rotation.rotateByDegrees_(angle)
        rotation.translateXBy_yBy_(-x, -y)
        return rotation

    @objc.python_method
    def selected_paths(self, layer):
        result = []
        selected_shapes = layer.selectedObjects()["shapes"]
        for shape in selected_shapes:
            if isinstance(shape, GSPath):
                result.append(shape)
        return result

    @objc.python_method
    def draw_rotated(self, layer):
        angle = self.slider_menu_view.group.slider.get()
        bezier_path = layer.copyDecomposedLayer().bezierPath
        dash_count_phase = [4 / self.getScale(), 4 / self.getScale()], 2, 0
        if not bezier_path:
            return
        bounds = bezier_path.bounds()

        if self.slider_menu_view.group.checkbox_selection_mode.get() == True:
            try:
                selected_paths = NSBezierPath.alloc().init()
                for p in self.selected_paths(layer):
                    selected_paths.appendBezierPath_(p.bezierPath)
                    bounds = selected_paths.bounds()
                bezier_path = selected_paths
            except:
                pass
        else:
            bezier_path = layer.completeBezierPath
            bounds = layer.bounds

        x = bounds.origin.x + 0.5 * bounds.size.width
        y = bounds.origin.y + 0.5 * bounds.size.height

        rotation = NSAffineTransform.transform()
        rotation.translateXBy_yBy_(x, y)
        rotation.rotateByDegrees_(angle)
        rotation.translateXBy_yBy_(-x, -y)
        bezier_path.transformUsingAffineTransform_(rotation)
        bezier_path_rotated_only = bezier_path.copy()

        do_flip_horizontal = self.slider_menu_view.group.horizontal.get()
        do_flip_vertical = self.slider_menu_view.group.vertical.get()

        cross_size = 10 / self.getScale()
        center_cross_1 = NSBezierPath.alloc().init()
        center_cross_2 = NSBezierPath.alloc().init()
        center_cross_1.moveToPoint_((x, y - cross_size))
        center_cross_2.moveToPoint_((x + cross_size, y))
        center_cross_1.lineToPoint_((x, y + cross_size))
        center_cross_2.lineToPoint_((x - cross_size, y))
        center_cross_1.setLineWidth_(0.75 / self.getScale())
        center_cross_2.setLineWidth_(0.75 / self.getScale())

        mirror_line = NSBezierPath.alloc().init()
        mirror_line.setLineWidth_(0.75 / self.getScale())

        # Apply flipping transformations
        flip_transform = NSAffineTransform.transform()
        flip_transform.translateXBy_yBy_(x, y)

        if do_flip_horizontal:
            flip_transform.scaleXBy_yBy_(-1, 1)
            mirror_line.moveToPoint_((x, NSMaxY(bounds)))
            mirror_line.lineToPoint_((x, NSMinY(bounds)))
            mirror_line.transformUsingAffineTransform_(self.rotation(x, y, 0))
            mirror_line.setLineDash_count_phase_(*dash_count_phase)
            mirror_line.stroke()
        if do_flip_vertical:
            flip_transform.scaleXBy_yBy_(1, -1)
            mirror_line.moveToPoint_((NSMinX(bounds), NSMidY(bounds)))
            mirror_line.lineToPoint_((NSMaxX(bounds), NSMidY(bounds)))
            mirror_line.transformUsingAffineTransform_(self.rotation(x, y, 0))
            mirror_line.setLineDash_count_phase_(*dash_count_phase)
            mirror_line.stroke()

        flip_transform.translateXBy_yBy_(-x, -y)

        if do_flip_horizontal or do_flip_vertical:
            bezier_path.transformUsingAffineTransform_(flip_transform)

        # Draw flipped path
        if bezier_path:
            bezier_path_rotated_only.setLineDash_count_phase_(*dash_count_phase)
            bezier_path_rotated_only.setLineWidth_(1 / self.getScale())
            bezier_path_rotated_only.stroke()
            bezier_path.fill()
            center_cross_1.stroke()
            center_cross_2.stroke()

        # Draw a rectangle with gradient fill
        gradient_rect_horizontal = NSZeroRect
        gradient_rect_vertical = NSZeroRect
        thickness = 100
        mirror_color = NSColor.colorWithDeviceRed_green_blue_alpha_(
            *self.color[:3], 0.2
        )
        mirror_color_clear = NSColor.clearColor()
        if do_flip_horizontal or do_flip_vertical:
            if do_flip_horizontal:
                gradient_rect_horizontal = NSMakeRect(
                    x, NSMinY(bounds), thickness, NSHeight(bounds)
                )
                gradient_path_horizontal = NSBezierPath.bezierPathWithRect_(
                    gradient_rect_horizontal
                )
                gradient_horizontal = NSGradient.alloc().initWithColors_(
                    [
                        mirror_color,
                        mirror_color_clear,
                    ]
                )
                gradient_horizontal.drawInBezierPath_angle_(gradient_path_horizontal, 0)
            if do_flip_vertical:
                gradient_rect_vertical = NSMakeRect(
                    NSMinX(bounds), NSMidY(bounds), NSWidth(bounds), thickness
                )
                gradient_path_vertical = NSBezierPath.bezierPathWithRect_(
                    gradient_rect_vertical
                )
                gradient_vertical = NSGradient.alloc().initWithColors_(
                    [
                        mirror_color,
                        mirror_color_clear,
                    ]
                )
                gradient_vertical.drawInBezierPath_angle_(gradient_path_vertical, 90)

    @objc.python_method
    def update(self, sender):
        try:
            Glyphs = NSApplication.sharedApplication()
            currentTabView = Glyphs.font.currentTab
            if currentTabView:
                currentTabView.graphicView().setNeedsDisplay_(True)
        except:
            pass

    @objc.python_method
    def background(self, layer):  # def foreground(self, layer):
        NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.color).set()
        self.draw_rotated(layer)

    def needsExtraMainOutlineDrawingInPreviewLayer_(self, layer):
        return False

    def drawForegroundInPreviewLayer_options_(self, layer, options):
