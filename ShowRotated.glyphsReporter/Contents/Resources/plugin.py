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

from GlyphsApp import GSPath, objcObject, TABDIDOPEN, TABWILLCLOSE, Glyphs
from GlyphsApp.plugins import ReporterPlugin, pathForResource, objc
from vanilla import Window, Slider, Group, CheckBox  # type: ignore


# ------------------
# Shut up Pylance
from typing import Any

Glyphs: Any = Glyphs
# ------------------

# Shut up Pylance
from AppKit import (
    NSBezierPath,  # type: ignore
    NSMaxX,  # type: ignore
    NSImage,  # type: ignore
    NSMinX,  # type: ignore
    NSMaxY,  # type: ignore
    NSMidY,  # type: ignore
    NSMinY,  # type: ignore
    NSHeight,  # type: ignore
    NSWidth,  # type: ignore
    NSGradient,  # type: ignore
    NSColor,  # type: ignore
    NSFont,  # type: ignore
    NSMakeRect,  # type: ignore
    NSZeroRect,  # type: ignore
    NSUserDefaults,  # type: ignore
    NSString,  # type: ignore
    NSMutableParagraphStyle,  # type: ignore
    NSAffineTransform,  # type: ignore
    NSCenterTextAlignment,  # type: ignore
    NSFontAttributeName,  # type: ignore
    NSParagraphStyleAttributeName,  # type: ignore
    NSForegroundColorAttributeName,  # type: ignore
    NSApplication,  # type: ignore
    NSFontWeightBold,  # type: ignore
    NSNotificationCenter,  # type: ignore
    NSUserDefaultsController,  # type: ignore
    NSButton,  # type: ignore
    NSRect,  # type: ignore
    NSTexturedRoundedBezelStyle,  # type: ignore
    NSToggleButton,  # type: ignore
    NSImageOnly,  # type: ignore
    NSImageScaleNone,  # type: ignore
)
import traceback

# Changelog
# NEW:
# 	+ Show predefined rotations in the bottom preview
# 	+ Add Selection Mode: draw only selected paths
# 	+ Add Mirror axis if Flipped V/H is active
# 	+ Add Center of Rotation

KEY_ROTATIONSBUTTON = "com_markfromberg_showRotations"


class ShowRotated(ReporterPlugin):
    @objc.python_method
    def settings(self):
        self.color = 0.0, 0.5, 0.3, 0.3
        self.menuName = Glyphs.localize(
            {
                "en": "Rotated",
                "de": "Rotiert",
                "es": "Rotado",
                "it": "Ruotato",
                "fr": "Tourné",
                "ko": "회전",
                "zh": "旋转",
                "ar": "مدور",
                "el": "Περιστραμμένο",
                "hi": "घुमाया हुआ",
                "sv": "Roterad",
                "no": "Roterte",
                "da": "Roteret",
                "pl": "Obrócone",
                "cs": "Otočeno",
                "pt": "Rotacionado",
                "th": "หมุน",
                "vi": "Xoay",
            }
        )
        self.name = self.menuName

        self.setup_ui()

    def setup_ui(self):
        view_width = 170
        view_height = 103
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
            {"name": "%s:" % self.name, "action": None},
            {"view": self.slider_menu_view.group.getNSView()},
        ]

    @objc.python_method
    def start(self):
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, "addRotationsButton:", TABDIDOPEN, objc.nil
        )
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, "removeRotationsButton:", TABWILLCLOSE, objc.nil
        )
        iconPath = pathForResource("rotatedIcon", "pdf", __file__)
        self.toolBarIcon = NSImage.alloc().initWithContentsOfFile_(iconPath)
        self.toolBarIcon.setTemplate_(True)

    def addRotationsButton_(self, notification):
        tab = notification.object()
        if hasattr(tab, "addViewToBottomToolbar_"):
            button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 18, 14))
            button.setBezelStyle_(NSTexturedRoundedBezelStyle)
            button.setBordered_(False)
            button.setButtonType_(NSToggleButton)
            button.setTitle_("")
            button.cell().setImagePosition_(NSImageOnly)
            button.cell().setImageScaling_(NSImageScaleNone)
            button.setImage_(self.toolBarIcon)
            tab.addViewToBottomToolbar_(button)
            try:
                tab.tempData["rotationsButton"] = button  # Glyphs 3
            except:
                tab.userData["rotationsButton"] = button  # Glyphs 2
            userDefaults = NSUserDefaultsController.sharedUserDefaultsController()
            button.bind_toObject_withKeyPath_options_(
                "value",
                userDefaults,
                objcObject(f"values.{KEY_ROTATIONSBUTTON}"),
                None,
            )
            userDefaults.addObserver_forKeyPath_options_context_(
                tab.graphicView(),
                objcObject(f"values.{KEY_ROTATIONSBUTTON}"),
                0,
                123,
            )

    def removeRotationsButton_(self, notification):
        tab = notification.object()
        try:
            button = tab.tempData["rotationsButton"]  # Glyphs 3
        except:
            button = tab.userData["rotationsButton"]  # Glyphs 2
        if button != None:
            button.unbind_("value")
            userDefaults = NSUserDefaultsController.sharedUserDefaultsController()
            userDefaults.removeObserver_forKeyPath_(
                tab.graphicView(), f"values.{KEY_ROTATIONSBUTTON}"
            )

    @objc.python_method
    def rotation_transform(self, angle, center):
        rotation = NSAffineTransform.transform()
        rotation.translateXBy_yBy_(center.x, center.y)
        rotation.rotateByDegrees_(angle)
        rotation.translateXBy_yBy_(-center.x, -center.y)
        return rotation

    @objc.python_method
    def rotation(self, x, y, angle):
        rotation = NSAffineTransform.transform()
        rotation.translateXBy_yBy_(x, y)
        rotation.rotateByDegrees_(angle)
        rotation.translateXBy_yBy_(-x, -y)
        return rotation

    @objc.python_method
    def selected_paths(self, layer):
        # fmt: off
        return [shape for shape in layer.selectedObjects()["shapes"] if isinstance(shape, GSPath)]
        # fmt: on

    @objc.python_method
    def draw_rotated(self, layer):
        angle = self.slider_menu_view.group.slider.get()
        bezier_path = layer.copyDecomposedLayer().bezierPath
        if not bezier_path:
            return

        try:
            bounds = bezier_path.bounds()
            if self.slider_menu_view.group.checkbox_selection_mode.get():
                selected_paths = NSBezierPath.alloc().init()
                for p in self.selected_paths(layer):
                    selected_paths.appendBezierPath_(p.bezierPath)
                bezier_path = selected_paths
                bounds = selected_paths.bounds()

            x, y = self.get_center(bounds)
            self.transform_path(bezier_path, x, y, angle)
            self.apply_flip_transformations(bezier_path, bounds, x, y)
            self.draw_path(bezier_path, bounds, x, y)
        except:
            print(traceback.format_exc())

    def get_center(self, bounds):
        x = bounds.origin.x + 0.5 * bounds.size.width
        y = bounds.origin.y + 0.5 * bounds.size.height
        return x, y

    def transform_path(self, bezier_path, x, y, angle):
        rotation = self.rotation(x, y, angle)
        bezier_path.transformUsingAffineTransform_(rotation)

    def apply_flip_transformations(self, bezier_path, bounds, x, y):
        flip_transform = NSAffineTransform.transform()
        flip_transform.translateXBy_yBy_(x, y)

        if self.slider_menu_view.group.horizontal.get():
            flip_transform.scaleXBy_yBy_(-1, 1)
            self.draw_mirror_line(x, NSMaxY(bounds), x, NSMinY(bounds), x, y, 0)
        if self.slider_menu_view.group.vertical.get():
            flip_transform.scaleXBy_yBy_(1, -1)
            self.draw_mirror_line(
                NSMinX(bounds), NSMidY(bounds), NSMaxX(bounds), NSMidY(bounds), x, y, 0
            )

        flip_transform.translateXBy_yBy_(-x, -y)
        if (
            self.slider_menu_view.group.horizontal.get()
            or self.slider_menu_view.group.vertical.get()
        ):
            bezier_path.transformUsingAffineTransform_(flip_transform)

    def draw_mirror_line(self, x1, y1, x2, y2, x, y, angle):
        mirror_line = NSBezierPath.alloc().init()
        mirror_line.setLineWidth_(0.75 / self.getScale())
        mirror_line.moveToPoint_((x1, y1))
        mirror_line.lineToPoint_((x2, y2))
        mirror_line.transformUsingAffineTransform_(self.rotation(x, y, angle))
        mirror_line.setLineDash_count_phase_(
            [4 / self.getScale(), 4 / self.getScale()], 2, 0
        )
        mirror_line.stroke()

    def draw_path(self, bezier_path, bounds, x, y):
        if bezier_path:
            bezier_path.setLineDash_count_phase_(
                [4 / self.getScale(), 4 / self.getScale()], 2, 0
            )
            bezier_path.setLineWidth_(1 / self.getScale())
            bezier_path.stroke()
            bezier_path.fill()
            self.draw_center_cross(x, y)
            self.draw_gradient(bounds, x, y)

    def draw_center_cross(self, x, y):
        cross_size = 10 / self.getScale()
        center_cross_1 = NSBezierPath.alloc().init()
        center_cross_2 = NSBezierPath.alloc().init()
        center_cross_1.moveToPoint_((x, y - cross_size))
        center_cross_2.moveToPoint_((x + cross_size, y))
        center_cross_1.lineToPoint_((x, y + cross_size))
        center_cross_2.lineToPoint_((x - cross_size, y))
        center_cross_1.setLineWidth_(0.75 / self.getScale())
        center_cross_2.setLineWidth_(0.75 / self.getScale())
        center_cross_1.stroke()
        center_cross_2.stroke()

    def draw_gradient(self, bounds, x, y):
        do_flip_horizontal = self.slider_menu_view.group.horizontal.get()
        do_flip_vertical = self.slider_menu_view.group.vertical.get()
        thickness = 100
        mirror_color = NSColor.colorWithDeviceRed_green_blue_alpha_(
            *self.color[:3], 0.2
        )
        mirror_color_clear = NSColor.clearColor()
        if do_flip_horizontal:
            gradient_rect_horizontal = NSMakeRect(
                x, NSMinY(bounds), thickness, NSHeight(bounds)
            )
            gradient_path_horizontal = NSBezierPath.bezierPathWithRect_(
                gradient_rect_horizontal
            )
            gradient_horizontal = NSGradient.alloc().initWithColors_(
                [mirror_color, mirror_color_clear]
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
                [mirror_color, mirror_color_clear]
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
        if Glyphs.boolDefaults[KEY_ROTATIONSBUTTON]:
            return False
        else:
            return True

    def drawForegroundInPreviewLayer_options_(self, layer, options):
        if not Glyphs.boolDefaults[KEY_ROTATIONSBUTTON]:
            return

        is_black = NSUserDefaults.standardUserDefaults().boolForKey_("GSPreview_Black")

        base_position_transform = NSAffineTransform.transform()
        padding = 100

        paragraph_style = NSMutableParagraphStyle.alloc().init()
        paragraph_style.setAlignment_(NSCenterTextAlignment)
        string_attributes = {
            NSFontAttributeName: NSFont.systemFontOfSize_weight_(80, NSFontWeightBold),
            NSForegroundColorAttributeName: NSColor.redColor(),
            NSParagraphStyleAttributeName: paragraph_style,
        }
        label_height = 100

        for i in range(8):
            rotation_transform = NSAffineTransform.transform()
            layer_path = layer.completeBezierPath.copy()
            if not layer_path:
                return

            try:
                rotation_degrees = 90 * i
                # TODO: refactor this bounds code. Used in several spots now.
                bounds = layer.bounds

                x = bounds.origin.x + 0.5 * bounds.size.width
                y = bounds.origin.y + 0.5 * bounds.size.height

                label = NSString.stringWithString_(
                    f"{rotation_degrees % 360}° {'↔' if i > 3 else ''}"
                )
                label.drawInRect_withAttributes_(
                    NSRect(
                        (
                            base_position_transform.transformStruct().tX - padding / 2,
                            layer.descender - label_height,
                        ),
                        # (NSWidth(bounds) + padding, label_height),
                        (layer.width + padding, label_height),
                    ),
                    string_attributes,
                )

                rotation_transform.translateXBy_yBy_(x, y)
                if i > 3:
                    rotation_transform.scaleXBy_yBy_(-1, 1)
                rotation_transform.rotateByDegrees_(rotation_degrees)
                rotation_transform.translateXBy_yBy_(-x, -y)

                combined_transform = NSAffineTransform.transform()
                combined_transform.appendTransform_(rotation_transform)
                combined_transform.appendTransform_(base_position_transform)

                layer_path.transformUsingAffineTransform_(combined_transform)

                if is_black:
                    NSColor.whiteColor().set()
                else:
                    NSColor.blackColor().set()

                layer_path.fill()

                # base_position_transform.translateXBy_yBy_(layer.width + padding, 0)
                base_position_transform.translateXBy_yBy_(
                    max(NSWidth(bounds), NSHeight(bounds)) + padding, 0
                )
                # layer_path_bounds = layer_path.bounds()
                # base_position_transform.translateXBy_yBy_(NSWidth(layer_path_bounds), 0)

            except:
                print(traceback.format_exc())
